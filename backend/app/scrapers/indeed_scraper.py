#!/usr/bin/env python3
"""
Scraper pour Indeed.fr - Plateforme d'offres d'emploi
"""
import urllib.parse
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper, logger

class IndeedScraper(BaseScraper):
    """Scraper pour la plateforme Indeed"""
    
    def __init__(self):
        super().__init__()
        self.name = 'indeed'
    
    def get_base_url(self) -> str:
        """URL de base d'Indeed France"""
        return "https://fr.indeed.com"
    
    def build_search_url(self, keywords: str, job_types: List[str], location: str = None) -> str:
        """Construit l'URL de recherche Indeed"""
        base_url = "https://fr.indeed.com/jobs"
        
        params = {
            'q': keywords,
            'sort': 'date',  # Trier par date
            'limit': 50,     # Nombre de résultats par page
        }
        
        # Ajouter localisation si fournie
        if location:
            params['l'] = location
        
        # Mapper les types d'emploi vers les filtres Indeed
        job_type_mapping = {
            'stage': 'internship',
            'alternance': 'apprenticeship', 
            'cdi': 'fulltime',
            'cdd': 'contract',
            'freelance': 'freelance'
        }
        
        # Indeed utilise le paramètre 'jt' pour le type d'emploi
        indeed_job_types = []
        for job_type in job_types:
            if job_type in job_type_mapping:
                indeed_job_types.append(job_type_mapping[job_type])
        
        if indeed_job_types:
            params['jt'] = ','.join(indeed_job_types)
        
        # Construire l'URL finale
        url = f"{base_url}?" + urllib.parse.urlencode(params)
        return url
    
    def _add_pagination(self, base_url: str, page: int) -> str:
        """Ajoute la pagination à l'URL"""
        start = (page - 1) * 50  # Indeed utilise start=0,50,100...
        separator = '&' if '?' in base_url else '?'
        return f"{base_url}{separator}start={start}"
    
    def get_job_listings(self, soup: BeautifulSoup) -> List:
        """Extrait les éléments d'offres d'emploi de la page Indeed"""
        # Indeed utilise différentes structures selon les versions
        selectors = [
            'div[data-result-id]',  # Nouveau format
            '.jobsearch-SerpJobCard',  # Ancien format
            '.slider_container .slider_item',  # Format mobile
            'div[data-jk]'  # Format alternatif
        ]
        
        job_listings = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                logger.info(f"[{self.name}] Found {len(elements)} jobs with selector: {selector}")
                job_listings = elements
                break
        
        return job_listings
    
    def parse_job_listing(self, job_element) -> Dict:
        """Parse une offre d'emploi Indeed"""
        job_data = {}
        
        try:
            # Titre de l'offre
            title_selectors = [
                'h2.jobTitle a span',
                'h2[data-testid="job-title"]',
                '.jobTitle a',
                'h2.jobTitle',
                '[data-testid="job-title"]'
            ]
            title = self._extract_text_by_selectors(job_element, title_selectors)
            if not title:
                return None
            job_data['title'] = self._clean_text(title)
            
            # URL de l'offre
            url_selectors = [
                'h2.jobTitle a',
                'h2[data-testid="job-title"] a',
                '.jobTitle a',
                'a[data-jk]'
            ]
            url_element = self._find_element_by_selectors(job_element, url_selectors)
            if url_element:
                relative_url = url_element.get('href', '')
                if relative_url:
                    # Construire l'URL complète
                    if relative_url.startswith('/'):
                        job_data['url'] = self.get_base_url() + relative_url
                    else:
                        job_data['url'] = relative_url
                    
                    # Nettoyer l'URL des paramètres de tracking
                    job_data['url'] = self._clean_url(job_data['url'])
            
            # Entreprise
            company_selectors = [
                'span.companyName a',
                'span.companyName',
                '[data-testid="company-name"]',
                '.companyName'
            ]
            company = self._extract_text_by_selectors(job_element, company_selectors)
            job_data['company'] = self._clean_text(company) if company else 'Non spécifié'
            
            # Localisation
            location_selectors = [
                '[data-testid="job-location"]',
                '.companyLocation',
                '.locationsContainer'
            ]
            location = self._extract_text_by_selectors(job_element, location_selectors)
            job_data['location'] = self._clean_text(location) if location else None
            
            # Salaire (optionnel)
            salary_selectors = [
                '[data-testid="attribute_snippet_testid"]',
                '.salary-snippet-container',
                '.salaryText'
            ]
            salary = self._extract_text_by_selectors(job_element, salary_selectors)
            if salary:
                job_data['salary'] = self._clean_text(salary)
            
            # Description courte/snippet
            description_selectors = [
                '[data-testid="job-snippet"]',
                '.job-snippet',
                '.summary'
            ]
            description = self._extract_text_by_selectors(job_element, description_selectors)
            if description:
                job_data['description_snippet'] = self._clean_text(description)[:500]
            
            # Date de publication
            date_selectors = [
                '[data-testid="myJobsStateDate"]',
                '.date',
                'span.date'
            ]
            date_text = self._extract_text_by_selectors(job_element, date_selectors)
            if date_text:
                job_data['date_posted'] = self._parse_indeed_date(date_text)
            
            # Type d'emploi (si disponible)
            type_selectors = [
                '[data-testid="attribute_snippet_testid"]'
            ]
            job_type = self._extract_text_by_selectors(job_element, type_selectors)
            if job_type:
                # Mapper vers nos types standard
                job_data['job_type'] = self._normalize_job_type(job_type)
            
            # Identifiant unique (pour éviter les doublons)
            job_id = job_element.get('data-result-id') or job_element.get('data-jk')
            if job_id:
                job_data['external_id'] = f"indeed_{job_id}"
            
            return job_data
            
        except Exception as e:
            logger.warning(f"[{self.name}] Error parsing job element: {e}")
            return None
    
    def _extract_text_by_selectors(self, element, selectors: List[str]) -> str:
        """Essaie plusieurs sélecteurs pour extraire du texte"""
        for selector in selectors:
            try:
                found_element = element.select_one(selector)
                if found_element:
                    return found_element.get_text(strip=True)
            except:
                continue
        return ""
    
    def _find_element_by_selectors(self, element, selectors: List[str]):
        """Essaie plusieurs sélecteurs pour trouver un élément"""
        for selector in selectors:
            try:
                found_element = element.select_one(selector)
                if found_element:
                    return found_element
            except:
                continue
        return None
    
    def _clean_url(self, url: str) -> str:
        """Nettoie l'URL des paramètres de tracking Indeed"""
        if not url:
            return ""
        
        # Supprimer les paramètres de tracking courants
        tracking_params = ['tk', 'from', 'alid', 'rgtk']
        try:
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # Supprimer les paramètres de tracking
            for param in tracking_params:
                query_params.pop(param, None)
            
            # Reconstruire l'URL
            clean_query = urlencode(query_params, doseq=True)
            clean_url = urlunparse((
                parsed.scheme, parsed.netloc, parsed.path,
                parsed.params, clean_query, parsed.fragment
            ))
            return clean_url
        except:
            return url
    
    def _parse_indeed_date(self, date_str: str) -> datetime:
        """Parse les formats de date spécifiques à Indeed"""
        if not date_str:
            return datetime.now()
        
        date_str = date_str.lower().strip()
        
        # Formats spécifiques Indeed en français
        if 'aujourd\'hui' in date_str:
            return datetime.now()
        elif 'hier' in date_str:
            return datetime.now() - timedelta(days=1)
        elif 'il y a' in date_str:
            if 'jour' in date_str:
                try:
                    days = int(''.join(filter(str.isdigit, date_str)))
                    return datetime.now() - timedelta(days=days)
                except:
                    pass
        
        # Utiliser la méthode générique si les formats spécifiques échouent
        return self._parse_date(date_str) or datetime.now()
    
    def _normalize_job_type(self, job_type_text: str) -> str:
        """Normalise le type d'emploi vers nos standards"""
        job_type_text = job_type_text.lower()
        
        if 'stage' in job_type_text:
            return 'stage'
        elif 'alternance' in job_type_text or 'apprentissage' in job_type_text:
            return 'alternance'
        elif 'cdi' in job_type_text or 'temps plein' in job_type_text:
            return 'cdi'
        elif 'cdd' in job_type_text or 'temporaire' in job_type_text:
            return 'cdd'
        elif 'freelance' in job_type_text or 'indépendant' in job_type_text:
            return 'freelance'
        else:
            return 'autre'
    
    def get_supported_job_types(self) -> List[str]:
        """Retourne la liste des types d'emploi supportés par Indeed"""
        return ['stage', 'alternance', 'cdi', 'cdd', 'freelance']
    
    def get_search_suggestions(self, keyword: str) -> List[str]:
        """Récupère des suggestions de mots-clés (optionnel)"""
        # Cette fonctionnalité peut être implémentée plus tard
        return []

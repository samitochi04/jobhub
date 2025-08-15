#!/usr/bin/env python3
"""
Scraper pour LinkedIn - Plateforme d'emploi professionnelle
Note: LinkedIn a des protections anti-bot strictes, ce scraper est basique
"""
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Dict
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper, logger

class LinkedInScraper(BaseScraper):
    """Scraper pour LinkedIn Jobs (version limitée)"""
    
    def __init__(self):
        super().__init__()
        self.name = 'linkedin'
        # LinkedIn nécessite des headers spéciaux
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.8,en-US;q=0.5,en;q=0.3',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        })
    
    def get_base_url(self) -> str:
        """URL de base de LinkedIn"""
        return "https://www.linkedin.com"
    
    def build_search_url(self, keywords: str, job_types: List[str], location: str = None) -> str:
        """
        Construit l'URL de recherche LinkedIn
        Note: LinkedIn a des restrictions, cette version est simplifiée
        """
        base_url = "https://www.linkedin.com/jobs/search"
        
        params = {
            'keywords': keywords,
            'sortBy': 'DD',  # Date Descending
        }
        
        # Ajouter localisation si fournie
        if location:
            params['location'] = location
        else:
            params['location'] = 'France'  # Par défaut
        
        # LinkedIn utilise des codes spéciaux pour les types d'emploi
        job_type_mapping = {
            'cdi': 'F',      # Full-time
            'cdd': 'C',      # Contract
            'stage': 'I',    # Internship
            'alternance': 'I', # Traité comme stage
            'freelance': 'C'  # Traité comme contrat
        }
        
        linkedin_job_types = []
        for job_type in job_types:
            if job_type in job_type_mapping:
                linkedin_job_types.append(job_type_mapping[job_type])
        
        if linkedin_job_types:
            params['f_JT'] = ','.join(set(linkedin_job_types))  # Éviter doublons
        
        url = f"{base_url}?" + urllib.parse.urlencode(params)
        return url
    
    def _add_pagination(self, base_url: str, page: int) -> str:
        """Ajoute la pagination à l'URL LinkedIn"""
        start = (page - 1) * 25  # LinkedIn utilise start=0,25,50...
        separator = '&' if '?' in base_url else '?'
        return f"{base_url}{separator}start={start}"
    
    def get_job_listings(self, soup: BeautifulSoup) -> List:
        """
        Extrait les éléments d'offres d'emploi de LinkedIn
        Note: LinkedIn change fréquemment sa structure
        """
        selectors = [
            '.jobs-search__results-list li',
            '.job-result-card',
            'div[data-job-id]',
            '.search-results__list li'
        ]
        
        job_listings = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                logger.info(f"[{self.name}] Found {len(elements)} jobs with selector: {selector}")
                job_listings = elements
                break
        
        # LinkedIn peut bloquer, log pour diagnostic
        if not job_listings:
            logger.warning(f"[{self.name}] No job listings found. Possible bot detection.")
            # Log first 500 chars of HTML for debugging
            html_preview = str(soup)[:500]
            logger.debug(f"[{self.name}] HTML preview: {html_preview}")
        
        return job_listings
    
    def parse_job_listing(self, job_element) -> Dict:
        """Parse une offre d'emploi LinkedIn"""
        job_data = {}
        
        try:
            # Titre - LinkedIn a plusieurs formats
            title_selectors = [
                '.job-result-card__title',
                'h3.job-result-card__title a',
                '.sr-only',
                'h3 a',
                '.job-title a'
            ]
            title = self._extract_text_by_selectors(job_element, title_selectors)
            if not title:
                return None
            job_data['title'] = self._clean_text(title)
            
            # URL - LinkedIn utilise des IDs spéciaux
            url_selectors = [
                '.job-result-card__title a',
                'h3 a',
                'a[data-job-id]'
            ]
            url_element = self._find_element_by_selectors(job_element, url_selectors)
            if url_element:
                href = url_element.get('href', '')
                if href:
                    if href.startswith('/'):
                        job_data['url'] = self.get_base_url() + href
                    else:
                        job_data['url'] = href
            
            # Entreprise
            company_selectors = [
                '.job-result-card__subtitle',
                'h4.job-result-card__subtitle a',
                '.company-name',
                'h4 a'
            ]
            company = self._extract_text_by_selectors(job_element, company_selectors)
            job_data['company'] = self._clean_text(company) if company else 'Non spécifié'
            
            # Localisation
            location_selectors = [
                '.job-result-card__location',
                '.location',
                'span.location'
            ]
            location = self._extract_text_by_selectors(job_element, location_selectors)
            if location:
                job_data['location'] = self._clean_text(location)
            
            # Date de publication - LinkedIn est souvent vague
            date_selectors = [
                'time',
                '.job-result-card__listdate',
                '.listed-time'
            ]
            date_text = self._extract_text_by_selectors(job_element, date_selectors)
            if date_text:
                job_data['date_posted'] = self._parse_linkedin_date(date_text)
            else:
                job_data['date_posted'] = datetime.now()  # Fallback
            
            # Description courte (souvent limitée sur LinkedIn)
            description_selectors = [
                '.job-result-card__snippet',
                '.job-snippet'
            ]
            description = self._extract_text_by_selectors(job_element, description_selectors)
            if description:
                job_data['description_snippet'] = self._clean_text(description)[:300]
            
            # ID unique LinkedIn
            job_id = job_element.get('data-job-id')
            if not job_id:
                # Essayer d'extraire de l'URL
                url = job_data.get('url', '')
                if '/jobs/view/' in url:
                    try:
                        job_id = url.split('/jobs/view/')[-1].split('/')[0].split('?')[0]
                    except:
                        pass
            
            if job_id:
                job_data['external_id'] = f"linkedin_{job_id}"
            
            # Type d'emploi - difficile à extraire de LinkedIn
            job_data['job_type'] = 'autre'  # Par défaut
            
            return job_data
            
        except Exception as e:
            logger.warning(f"[{self.name}] Error parsing LinkedIn job: {e}")
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
    
    def _parse_linkedin_date(self, date_str: str) -> datetime:
        """Parse les formats de date LinkedIn (souvent en anglais)"""
        if not date_str:
            return datetime.now()
        
        date_str = date_str.lower().strip()
        now = datetime.now()
        
        # Formats LinkedIn courants
        if 'just now' in date_str or 'à l\'instant' in date_str:
            return now
        elif 'today' in date_str or 'aujourd\'hui' in date_str:
            return now
        elif 'yesterday' in date_str or 'hier' in date_str:
            return now - timedelta(days=1)
        elif 'day' in date_str or 'jour' in date_str:
            try:
                days = int(''.join(filter(str.isdigit, date_str)))
                return now - timedelta(days=days)
            except:
                pass
        elif 'week' in date_str or 'semaine' in date_str:
            try:
                weeks = int(''.join(filter(str.isdigit, date_str)))
                return now - timedelta(weeks=weeks)
            except:
                return now - timedelta(weeks=1)  # Fallback
        elif 'month' in date_str or 'mois' in date_str:
            try:
                months = int(''.join(filter(str.isdigit, date_str)))
                return now - timedelta(days=months * 30)
            except:
                return now - timedelta(days=30)  # Fallback
        
        # Fallback pour formats non reconnus
        return self._parse_date(date_str) or now
    
    def test_connection(self) -> bool:
        """
        Test spécialisé pour LinkedIn
        LinkedIn peut bloquer les bots, donc test plus prudent
        """
        try:
            # Test avec une page publique simple
            test_url = "https://www.linkedin.com/jobs/search?keywords=test&location=France"
            response = self._make_request(test_url)
            
            if not response:
                return False
            
            # Vérifier qu'on n'est pas bloqué
            if 'challenge' in response.text.lower() or 'captcha' in response.text.lower():
                logger.warning(f"[{self.name}] Possible bot detection on LinkedIn")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"[{self.name}] LinkedIn connection test failed: {e}")
            return False
    
    def get_supported_job_types(self) -> List[str]:
        """Types d'emploi supportés par LinkedIn"""
        return ['stage', 'alternance', 'cdi', 'cdd', 'freelance']
    
    def scrape_jobs(self, keywords: str, job_types: List[str], location: str = None, 
                   limit: int = 25, since_date: datetime = None) -> List[Dict]:
        """
        Scrape LinkedIn avec limite réduite (LinkedIn est restrictif)
        """
        # Limiter à 25 offres max pour LinkedIn pour éviter la détection
        actual_limit = min(limit, 25)
        logger.info(f"[{self.name}] LinkedIn scraping limited to {actual_limit} jobs")
        
        return super().scrape_jobs(keywords, job_types, location, actual_limit, since_date)

#!/usr/bin/env python3
"""
Base scraper abstrait pour JobHub
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import requests
import time
import random
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingError(Exception):
    """Exception personnalisée pour les erreurs de scraping"""
    pass

class BaseScraper(ABC):
    """Classe abstraite pour tous les scrapers de plateformes d'emploi"""
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace('scraper', '')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self._get_random_user_agent(),
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Configuration anti-détection
        self.request_delay = (1, 3)  # Délai aléatoire entre requêtes (min, max)
        self.max_retries = 3
        self.timeout = 15
    
    def _get_random_user_agent(self) -> str:
        """Retourne un User-Agent aléatoire pour éviter la détection"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        ]
        return random.choice(user_agents)
    
    def _make_request(self, url: str, params: Dict = None, retries: int = 0) -> Optional[requests.Response]:
        """Effectue une requête HTTP avec gestion d'erreurs et retry"""
        try:
            # Délai anti-détection
            delay = random.uniform(*self.request_delay)
            time.sleep(delay)
            
            logger.info(f"[{self.name}] Making request to: {url}")
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                return response
            elif response.status_code == 429 and retries < self.max_retries:
                # Rate limiting - attendre plus longtemps
                wait_time = (2 ** retries) * 60  # Backoff exponentiel
                logger.warning(f"[{self.name}] Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                return self._make_request(url, params, retries + 1)
            else:
                logger.error(f"[{self.name}] HTTP {response.status_code}: {response.text[:200]}")
                return None
                
        except requests.RequestException as e:
            if retries < self.max_retries:
                logger.warning(f"[{self.name}] Request failed, retrying... ({retries + 1}/{self.max_retries})")
                time.sleep(2 ** retries)  # Backoff exponentiel
                return self._make_request(url, params, retries + 1)
            else:
                logger.error(f"[{self.name}] Request failed permanently: {e}")
                raise ScrapingError(f"Failed to fetch {url}: {e}")
    
    def _parse_html(self, html_content: str) -> BeautifulSoup:
        """Parse le contenu HTML avec BeautifulSoup"""
        return BeautifulSoup(html_content, 'html.parser')
    
    def _clean_text(self, text: str) -> str:
        """Nettoie et normalise le texte"""
        if not text:
            return ""
        return ' '.join(text.strip().split())
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse différents formats de date"""
        if not date_str:
            return None
            
        date_str = date_str.lower().strip()
        now = datetime.now()
        
        # Formats relatifs français
        if 'aujourd\'hui' in date_str or 'ajd' in date_str:
            return now
        elif 'hier' in date_str:
            return now - timedelta(days=1)
        elif 'il y a' in date_str:
            if 'jour' in date_str:
                try:
                    days = int(''.join(filter(str.isdigit, date_str)))
                    return now - timedelta(days=days)
                except:
                    pass
            elif 'semaine' in date_str:
                try:
                    weeks = int(''.join(filter(str.isdigit, date_str)))
                    return now - timedelta(weeks=weeks)
                except:
                    pass
        
        # Formats de date standard
        date_formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y-%m-%d',
            '%d %B %Y',
            '%d %b %Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"[{self.name}] Could not parse date: {date_str}")
        return None
    
    @abstractmethod
    def get_base_url(self) -> str:
        """Retourne l'URL de base de la plateforme"""
        pass
    
    @abstractmethod
    def build_search_url(self, keywords: str, job_types: List[str], location: str = None) -> str:
        """Construit l'URL de recherche avec les paramètres"""
        pass
    
    @abstractmethod
    def parse_job_listing(self, job_element) -> Dict:
        """Parse un élément d'offre d'emploi et retourne un dictionnaire"""
        pass
    
    @abstractmethod
    def get_job_listings(self, soup: BeautifulSoup) -> List:
        """Extrait la liste des éléments d'offres d'emploi de la page"""
        pass
    
    def scrape_jobs(self, keywords: str, job_types: List[str], location: str = None, 
                   limit: int = 50, since_date: datetime = None) -> List[Dict]:
        """
        Scrape les offres d'emploi selon les critères
        
        Args:
            keywords: Mots-clés de recherche
            job_types: Types d'emploi recherchés
            location: Localisation (optionnel)
            limit: Nombre maximum d'offres à récupérer
            since_date: Date à partir de laquelle chercher
        
        Returns:
            Liste des offres d'emploi trouvées
        """
        logger.info(f"[{self.name}] Starting scrape: '{keywords}' - {job_types}")
        
        all_jobs = []
        page = 1
        
        try:
            while len(all_jobs) < limit:
                search_url = self.build_search_url(keywords, job_types, location)
                
                # Ajouter pagination si supportée
                if hasattr(self, '_add_pagination'):
                    search_url = self._add_pagination(search_url, page)
                
                response = self._make_request(search_url)
                if not response:
                    break
                
                soup = self._parse_html(response.text)
                job_listings = self.get_job_listings(soup)
                
                if not job_listings:
                    logger.info(f"[{self.name}] No more jobs found on page {page}")
                    break
                
                page_jobs = []
                for job_element in job_listings:
                    try:
                        job_data = self.parse_job_listing(job_element)
                        if job_data and self._is_valid_job(job_data, since_date):
                            job_data['platform'] = self.name
                            job_data['scraped_at'] = datetime.now()
                            page_jobs.append(job_data)
                    except Exception as e:
                        logger.warning(f"[{self.name}] Error parsing job: {e}")
                        continue
                
                all_jobs.extend(page_jobs[:limit - len(all_jobs)])
                logger.info(f"[{self.name}] Page {page}: {len(page_jobs)} jobs found")
                
                # Arrêter si on a atteint la limite ou si since_date est dépassé
                if len(all_jobs) >= limit:
                    break
                
                if since_date and page_jobs and all(job.get('date_posted', datetime.now()) < since_date for job in page_jobs[-5:]):
                    logger.info(f"[{self.name}] Reached since_date limit, stopping")
                    break
                
                page += 1
                
                # Protection contre boucle infinie
                if page > 10:
                    logger.warning(f"[{self.name}] Max pages reached")
                    break
            
        except Exception as e:
            logger.error(f"[{self.name}] Scraping error: {e}")
            raise ScrapingError(f"Error during scraping: {e}")
        
        logger.info(f"[{self.name}] Scraping completed: {len(all_jobs)} jobs found")
        return all_jobs
    
    def _is_valid_job(self, job_data: Dict, since_date: datetime = None) -> bool:
        """Valide si une offre répond aux critères"""
        if not job_data.get('title') or not job_data.get('url'):
            return False
        
        if since_date and job_data.get('date_posted'):
            if job_data['date_posted'] < since_date:
                return False
        
        return True
    
    def test_connection(self) -> bool:
        """Test la connexion à la plateforme"""
        try:
            base_url = self.get_base_url()
            response = self._make_request(base_url)
            return response is not None
        except Exception as e:
            logger.error(f"[{self.name}] Connection test failed: {e}")
            return False

    def get_stats(self) -> Dict:
        """Retourne les statistiques du scraper"""
        return {
            'name': self.name,
            'base_url': self.get_base_url(),
            'connection_ok': self.test_connection(),
            'last_run': None,  # À implémenter avec un système de cache
            'total_scraped': 0,  # À implémenter avec un système de métriques
        }

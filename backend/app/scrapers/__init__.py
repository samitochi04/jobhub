#!/usr/bin/env python3
"""
Gestionnaire des scrapers JobHub
"""
from .base_scraper import BaseScraper, ScrapingError
from .indeed_scraper import IndeedScraper
from .linkedin_scraper import LinkedInScraper

# Export des scrapers disponibles
__all__ = [
    'BaseScraper',
    'ScrapingError', 
    'IndeedScraper',
    'LinkedInScraper',
    'get_scraper',
    'get_available_scrapers',
    'ScraperManager'
]

def get_scraper(platform_name: str) -> BaseScraper:
    """
    Factory pour créer une instance de scraper
    
    Args:
        platform_name: Nom de la plateforme ('indeed', 'linkedin', etc.)
    
    Returns:
        Instance du scraper correspondant
    
    Raises:
        ValueError: Si la plateforme n'est pas supportée
    """
    scrapers = {
        'indeed': IndeedScraper,
        'linkedin': LinkedInScraper,
    }
    
    if platform_name.lower() not in scrapers:
        available = ', '.join(scrapers.keys())
        raise ValueError(f"Platform '{platform_name}' not supported. Available: {available}")
    
    return scrapers[platform_name.lower()]()

def get_available_scrapers() -> list:
    """Retourne la liste des scrapers disponibles"""
    return ['indeed', 'linkedin']

class ScraperManager:
    """Gestionnaire centralisé des scrapers"""
    
    def __init__(self):
        self.scrapers = {}
        self._load_scrapers()
    
    def _load_scrapers(self):
        """Charge tous les scrapers disponibles"""
        for platform in get_available_scrapers():
            try:
                self.scrapers[platform] = get_scraper(platform)
            except Exception as e:
                print(f"Warning: Failed to load scraper for {platform}: {e}")
    
    def get_scraper(self, platform: str) -> BaseScraper:
        """Récupère un scraper par nom de plateforme"""
        if platform not in self.scrapers:
            raise ValueError(f"Scraper for platform '{platform}' not available")
        return self.scrapers[platform]
    
    def get_all_scrapers(self) -> dict:
        """Retourne tous les scrapers chargés"""
        return self.scrapers.copy()
    
    def test_all_connections(self) -> dict:
        """Test la connexion de tous les scrapers"""
        results = {}
        for platform, scraper in self.scrapers.items():
            try:
                results[platform] = scraper.test_connection()
            except Exception as e:
                results[platform] = False
                print(f"Connection test failed for {platform}: {e}")
        return results
    
    def get_stats(self) -> dict:
        """Statistiques de tous les scrapers"""
        stats = {}
        for platform, scraper in self.scrapers.items():
            try:
                stats[platform] = scraper.get_stats()
            except Exception as e:
                stats[platform] = {'error': str(e)}
        return stats

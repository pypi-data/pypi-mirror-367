"""
Scholarly search functionality for academic research

This module provides the main interface for searching scholarly publications,
similar to the scholarly package but with enhanced features.
"""

import asyncio
import time
import random
from typing import Dict, List, Optional, Union, AsyncGenerator, Any
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import aiohttp


class ScholarlySearch:
    """Main class for scholarly search operations"""
    
    def __init__(self, delay_range: tuple = (1, 3)):
        """
        Initialize the ScholarlySearch instance
        
        Args:
            delay_range: Tuple of (min, max) seconds to wait between requests
        """
        self.delay_range = delay_range
        self.session = requests.Session()
        self.ua = UserAgent()
        self._setup_session()
        
    def _setup_session(self):
        """Setup the requests session with headers"""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _delay(self):
        """Random delay to avoid being blocked"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def search_publications(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for publications by query
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            List of publication dictionaries
        """
        publications = []
        
        # Google Scholar search URL
        base_url = "https://scholar.google.com/scholar"
        params = {
            'q': query,
            'hl': 'en',
            'num': min(num_results, 20)  # Google Scholar limits per page
        }
        
        try:
            self._delay()
            response = self.session.get(base_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.find_all('div', class_='gs_r gs_or gs_scl')
            
            for result in results[:num_results]:
                pub_data = self._parse_publication(result)
                if pub_data:
                    publications.append(pub_data)
                    
        except Exception as e:
            print(f"Error searching publications: {e}")
            
        return publications
    
    def _parse_publication(self, result_element) -> Optional[Dict[str, Any]]:
        """Parse a single publication result"""
        try:
            # Title
            title_elem = result_element.find('h3', class_='gs_rt')
            title = title_elem.get_text() if title_elem else "Unknown"
            
            # Authors and publication info
            info_elem = result_element.find('div', class_='gs_a')
            authors_info = info_elem.get_text() if info_elem else ""
            
            # Citation count
            citation_elem = result_element.find('div', class_='gs_fl')
            citations = 0
            if citation_elem:
                cite_links = citation_elem.find_all('a')
                for link in cite_links:
                    if 'Cited by' in link.get_text():
                        try:
                            citations = int(link.get_text().split('Cited by ')[1])
                        except:
                            citations = 0
                        break
            
            # Abstract/snippet
            snippet_elem = result_element.find('div', class_='gs_rs')
            abstract = snippet_elem.get_text() if snippet_elem else ""
            
            # URL
            url = ""
            title_link = title_elem.find('a') if title_elem else None
            if title_link and title_link.get('href'):
                url = title_link.get('href')
            
            return {
                'title': title.strip(),
                'authors': authors_info.strip(),
                'citations': citations,
                'abstract': abstract.strip(),
                'url': url,
                'source': 'Google Scholar'
            }
            
        except Exception as e:
            print(f"Error parsing publication: {e}")
            return None
    
    def search_author(self, author_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for author information
        
        Args:
            author_name: Name of the author to search
            
        Returns:
            Author information dictionary
        """
        # Google Scholar author search
        base_url = "https://scholar.google.com/citations"
        params = {
            'mauthors': author_name,
            'hl': 'en'
        }
        
        try:
            self._delay()
            response = self.session.get(base_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find first author result
            author_elem = soup.find('div', class_='gsc_1usr')
            if not author_elem:
                return None
            
            name_elem = author_elem.find('h3', class_='gs_ai_name')
            name = name_elem.get_text() if name_elem else author_name
            
            affiliation_elem = author_elem.find('div', class_='gs_ai_aff')
            affiliation = affiliation_elem.get_text() if affiliation_elem else ""
            
            # Citation metrics
            citation_elem = author_elem.find('div', class_='gs_ai_cby')
            total_citations = 0
            if citation_elem:
                try:
                    total_citations = int(citation_elem.get_text().split('Cited by ')[1])
                except:
                    pass
            
            return {
                'name': name.strip(),
                'affiliation': affiliation.strip(),
                'total_citations': total_citations,
                'source': 'Google Scholar'
            }
            
        except Exception as e:
            print(f"Error searching author: {e}")
            return None
    
    async def async_search_publications(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Async version of publication search"""
        # Implementation for async search
        # This is a placeholder for future async implementation
        return self.search_publications(query, num_results)
    
    def close(self):
        """Close the session"""
        if hasattr(self, 'session'):
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

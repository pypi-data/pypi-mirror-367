"""
Journal analysis and metrics

This module provides functionality to analyze academic journals,
their metrics, rankings, and publication patterns.
"""

import time
import random
from typing import Dict, List, Optional, Union, Any
import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent


class JournalAnalyzer:
    """Class for analyzing journal metrics and information"""
    
    def __init__(self, delay_range: tuple = (1, 3)):
        """
        Initialize the Journal Analyzer
        
        Args:
            delay_range: Tuple of (min, max) seconds to wait between requests
        """
        self.delay_range = delay_range
        self.session = requests.Session()
        self.ua = UserAgent()
        self._setup_session()
        
        # Cache for journal data
        self._journal_cache = {}
        
    def _setup_session(self):
        """Setup the requests session with headers"""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def _delay(self):
        """Random delay to avoid being blocked"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def get_journal_info(self, journal_name: str, issn: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive journal information
        
        Args:
            journal_name: Name of the journal
            issn: ISSN if known
            
        Returns:
            Dictionary with journal information
        """
        # Check cache first
        cache_key = issn or journal_name.lower()
        if cache_key in self._journal_cache:
            return self._journal_cache[cache_key]
        
        journal_info = None
        
        # Try different sources
        journal_info = self._get_journal_from_doaj(journal_name, issn)
        
        if not journal_info:
            journal_info = self._get_journal_from_crossref(journal_name, issn)
        
        if not journal_info:
            journal_info = self._create_basic_journal_info(journal_name, issn)
        
        # Cache the result
        if journal_info:
            self._journal_cache[cache_key] = journal_info
            
        return journal_info
    
    def _get_journal_from_doaj(self, journal_name: str, issn: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get journal information from Directory of Open Access Journals (DOAJ)"""
        try:
            # DOAJ API
            base_url = "https://doaj.org/api/v2/search/journals/"
            
            if issn:
                query = f"issn:{issn}"
            else:
                query = f'bibjson.title:"{journal_name}"'
            
            params = {
                'q': query,
                'pageSize': 1
            }
            
            self._delay()
            response = self.session.get(base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('results') and len(data['results']) > 0:
                result = data['results'][0]
                bibjson = result.get('bibjson', {})
                
                return {
                    'title': bibjson.get('title', journal_name),
                    'issn_print': bibjson.get('pissn', ''),
                    'issn_electronic': bibjson.get('eissn', ''),
                    'publisher': bibjson.get('publisher', {}).get('name', ''),
                    'country': bibjson.get('publisher', {}).get('country', ''),
                    'language': ', '.join(bibjson.get('language', [])),
                    'subject': [subj.get('term', '') for subj in bibjson.get('subject', [])],
                    'open_access': True,
                    'url': bibjson.get('link', [{}])[0].get('url', '') if bibjson.get('link') else '',
                    'source': 'DOAJ'
                }
                
        except Exception as e:
            print(f"Error getting journal from DOAJ: {e}")
            
        return None
    
    def _get_journal_from_crossref(self, journal_name: str, issn: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get journal information from Crossref API"""
        try:
            base_url = "https://api.crossref.org/journals"
            
            if issn:
                url = f"{base_url}/{issn}"
                self._delay()
                response = self.session.get(url)
            else:
                params = {
                    'query': journal_name,
                    'rows': 1
                }
                self._delay()
                response = self.session.get(base_url, params=params)
            
            response.raise_for_status()
            data = response.json()
            
            if issn and 'message' in data:
                journal_data = data['message']
            elif 'message' in data and 'items' in data['message'] and len(data['message']['items']) > 0:
                journal_data = data['message']['items'][0]
            else:
                return None
            
            return {
                'title': journal_data.get('title', journal_name),
                'issn_print': ', '.join(journal_data.get('ISSN', [])),
                'publisher': journal_data.get('publisher', ''),
                'subject': journal_data.get('subject', []),
                'total_dois': journal_data.get('total-dois', 0),
                'current_dois': journal_data.get('current-dois', 0),
                'source': 'Crossref'
            }
            
        except Exception as e:
            print(f"Error getting journal from Crossref: {e}")
            
        return None
    
    def _create_basic_journal_info(self, journal_name: str, issn: Optional[str] = None) -> Dict[str, Any]:
        """Create basic journal info when other sources fail"""
        return {
            'title': journal_name,
            'issn_print': issn or '',
            'issn_electronic': '',
            'publisher': 'Unknown',
            'country': 'Unknown',
            'source': 'Basic Info'
        }
    
    def search_journals_by_subject(self, subject: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for journals in a specific subject area
        
        Args:
            subject: Subject area or field
            limit: Maximum number of journals to return
            
        Returns:
            List of journals in the subject area
        """
        journals = []
        
        try:
            # Use DOAJ API to search by subject
            base_url = "https://doaj.org/api/v2/search/journals/"
            params = {
                'q': f'bibjson.subject.term:"{subject}"',
                'pageSize': min(limit, 100)
            }
            
            self._delay()
            response = self.session.get(base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            for result in data.get('results', []):
                bibjson = result.get('bibjson', {})
                
                journals.append({
                    'title': bibjson.get('title', ''),
                    'issn_print': bibjson.get('pissn', ''),
                    'issn_electronic': bibjson.get('eissn', ''),
                    'publisher': bibjson.get('publisher', {}).get('name', ''),
                    'country': bibjson.get('publisher', {}).get('country', ''),
                    'subjects': [subj.get('term', '') for subj in bibjson.get('subject', [])],
                    'open_access': True,
                    'source': 'DOAJ'
                })
                
        except Exception as e:
            print(f"Error searching journals by subject: {e}")
            
        return journals[:limit]
    
    def get_journal_metrics_history(self, journal_name: str, years: List[int]) -> Optional[pd.DataFrame]:
        """
        Get journal metrics over multiple years
        
        Args:
            journal_name: Name of the journal
            years: List of years to analyze
            
        Returns:
            DataFrame with historical metrics
        """
        # This would integrate with the ImpactFactorAnalyzer
        from .impact_factor import ImpactFactorAnalyzer
        
        if_analyzer = ImpactFactorAnalyzer()
        
        try:
            metrics_data = []
            
            for year in years:
                metrics = if_analyzer.get_journal_impact_factor(journal_name, year)
                if metrics:
                    metrics_data.append({
                        'year': year,
                        'impact_factor': metrics.get('impact_factor', 0),
                        'citescore': metrics.get('citescore', 0),
                        'sjr': metrics.get('sjr', 0),
                        'snip': metrics.get('snip', 0),
                        'h_index': metrics.get('h_index', 0),
                        'quartile': metrics.get('quartile', 'N/A')
                    })
            
            if metrics_data:
                return pd.DataFrame(metrics_data)
                
        finally:
            if_analyzer.close()
            
        return None
    
    def analyze_journal_publication_pattern(self, journal_name: str, 
                                          start_year: int, end_year: int) -> Dict[str, Any]:
        """
        Analyze publication patterns for a journal
        
        Args:
            journal_name: Name of the journal
            start_year: Start year for analysis
            end_year: End year for analysis
            
        Returns:
            Analysis of publication patterns
        """
        # This is a placeholder implementation
        # In practice, this would query publication databases
        
        analysis = {
            'journal_name': journal_name,
            'analysis_period': f"{start_year}-{end_year}",
            'total_articles': random.randint(500, 2000),
            'avg_articles_per_year': random.randint(50, 200),
            'article_types': {
                'research_articles': random.randint(60, 80),
                'review_articles': random.randint(10, 20),
                'short_communications': random.randint(5, 15),
                'editorials': random.randint(1, 5)
            },
            'international_collaboration': random.randint(40, 80),
            'open_access_percentage': random.randint(20, 100)
        }
        
        return analysis
    
    def compare_journal_metrics(self, journal_names: List[str], 
                               year: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        Compare metrics across multiple journals
        
        Args:
            journal_names: List of journal names to compare
            year: Year for comparison (defaults to latest)
            
        Returns:
            DataFrame with comparison data
        """
        from .impact_factor import ImpactFactorAnalyzer
        
        if_analyzer = ImpactFactorAnalyzer()
        
        try:
            comparison_data = []
            
            for journal in journal_names:
                # Get journal info
                journal_info = self.get_journal_info(journal)
                
                # Get impact metrics
                metrics = if_analyzer.get_journal_impact_factor(journal, year)
                
                comparison_data.append({
                    'journal': journal,
                    'publisher': journal_info.get('publisher', 'Unknown') if journal_info else 'Unknown',
                    'impact_factor': metrics.get('impact_factor', 0) if metrics else 0,
                    'citescore': metrics.get('citescore', 0) if metrics else 0,
                    'sjr': metrics.get('sjr', 0) if metrics else 0,
                    'quartile': metrics.get('quartile', 'N/A') if metrics else 'N/A',
                    'subject_area': metrics.get('subject_area', 'Unknown') if metrics else 'Unknown',
                    'open_access': journal_info.get('open_access', False) if journal_info else False
                })
            
            if comparison_data:
                return pd.DataFrame(comparison_data)
                
        finally:
            if_analyzer.close()
            
        return None
    
    def get_journal_editorial_board(self, journal_name: str) -> List[Dict[str, Any]]:
        """
        Get editorial board information for a journal
        
        Args:
            journal_name: Name of the journal
            
        Returns:
            List of editorial board members
        """
        # This would require scraping journal websites
        # Placeholder implementation
        
        editorial_board = []
        
        # Mock data for demonstration
        positions = ['Editor-in-Chief', 'Associate Editor', 'Editorial Board Member']
        
        for i in range(random.randint(5, 15)):
            editorial_board.append({
                'name': f'Dr. Editorial Member {i+1}',
                'position': random.choice(positions),
                'affiliation': f'University {i+1}',
                'country': 'Unknown'
            })
        
        return editorial_board
    
    def recommend_journals(self, keywords: List[str], min_if: float = 0, 
                          max_if: float = 10, open_access: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Recommend journals based on keywords and criteria
        
        Args:
            keywords: List of research keywords
            min_if: Minimum impact factor
            max_if: Maximum impact factor
            open_access: Filter for open access journals
            
        Returns:
            List of recommended journals
        """
        recommendations = []
        
        # This would use machine learning or keyword matching algorithms
        # Placeholder implementation with mock data
        
        for i in range(10):
            if_value = random.uniform(min_if, max_if)
            is_oa = random.choice([True, False]) if open_access is None else open_access
            
            # Only include if it matches open access criteria
            if open_access is not None and is_oa != open_access:
                continue
            
            recommendations.append({
                'journal_name': f'Journal of {" ".join(keywords[:2])} Research {i+1}',
                'impact_factor': round(if_value, 2),
                'relevance_score': random.uniform(0.7, 1.0),
                'open_access': is_oa,
                'subject_area': keywords[0] if keywords else 'General',
                'publisher': f'Academic Publisher {i+1}',
                'acceptance_rate': random.randint(15, 60)
            })
        
        # Sort by relevance score
        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return recommendations
    
    def clear_cache(self):
        """Clear the journal data cache"""
        self._journal_cache.clear()
    
    def close(self):
        """Close the session"""
        if hasattr(self, 'session'):
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

"""
Author analysis and researcher metrics

This module provides functionality to analyze author profiles, 
citation metrics, and research impact.
"""

import time
import random
from typing import Dict, List, Optional, Union, Any
import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent


class AuthorAnalyzer:
    """Class for analyzing author profiles and metrics"""
    
    def __init__(self, delay_range: tuple = (1, 3)):
        """
        Initialize the Author Analyzer
        
        Args:
            delay_range: Tuple of (min, max) seconds to wait between requests
        """
        self.delay_range = delay_range
        self.session = requests.Session()
        self.ua = UserAgent()
        self._setup_session()
        
        # Cache for author data
        self._author_cache = {}
        
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
    
    def get_author_profile(self, author_name: str, scholar_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive author profile
        
        Args:
            author_name: Name of the author
            scholar_id: Google Scholar ID if known
            
        Returns:
            Dictionary with author profile data
        """
        # Check cache first
        cache_key = scholar_id or author_name.lower()
        if cache_key in self._author_cache:
            return self._author_cache[cache_key]
        
        profile = None
        
        if scholar_id:
            profile = self._get_scholar_profile_by_id(scholar_id)
        else:
            profile = self._search_author_profile(author_name)
        
        # Cache the result
        if profile:
            self._author_cache[cache_key] = profile
            
        return profile
    
    def _get_scholar_profile_by_id(self, scholar_id: str) -> Optional[Dict[str, Any]]:
        """Get author profile using Google Scholar ID"""
        try:
            url = f"https://scholar.google.com/citations?user={scholar_id}&hl=en"
            
            self._delay()
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract profile information
            name_elem = soup.find('div', id='gsc_prf_in')
            name = name_elem.get_text() if name_elem else "Unknown"
            
            # Affiliation
            affiliation_elem = soup.find('div', class_='gsc_prf_il')
            affiliation = affiliation_elem.get_text() if affiliation_elem else ""
            
            # Citation metrics
            citation_table = soup.find('table', id='gsc_rsb_st')
            metrics = {}
            
            if citation_table:
                rows = citation_table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        metric_name = cells[0].get_text().strip()
                        all_value = cells[1].get_text().strip()
                        since_2019 = cells[2].get_text().strip()
                        
                        metrics[metric_name.lower().replace(' ', '_')] = {
                            'all': int(all_value) if all_value.isdigit() else 0,
                            'since_2019': int(since_2019) if since_2019.isdigit() else 0
                        }
            
            # Research interests
            interests_elem = soup.find('div', id='gsc_prf_int')
            interests = []
            if interests_elem:
                interest_links = interests_elem.find_all('a', class_='gsc_prf_inta')
                interests = [link.get_text() for link in interest_links]
            
            # Get publications
            publications = self._get_author_publications(scholar_id)
            
            profile = {
                'name': name.strip(),
                'scholar_id': scholar_id,
                'affiliation': affiliation.strip(),
                'interests': interests,
                'metrics': metrics,
                'publications': publications,
                'total_citations': metrics.get('citations', {}).get('all', 0),
                'h_index': metrics.get('h-index', {}).get('all', 0),
                'i10_index': metrics.get('i10-index', {}).get('all', 0),
                'source': 'Google Scholar'
            }
            
            return profile
            
        except Exception as e:
            print(f"Error getting scholar profile: {e}")
            return None
    
    def _search_author_profile(self, author_name: str) -> Optional[Dict[str, Any]]:
        """Search for author profile by name"""
        try:
            # Search for author on Google Scholar
            base_url = "https://scholar.google.com/citations"
            params = {
                'mauthors': author_name,
                'hl': 'en'
            }
            
            self._delay()
            response = self.session.get(base_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find first author result
            author_elem = soup.find('div', class_='gsc_1usr')
            if not author_elem:
                return None
            
            # Extract scholar ID from the profile link
            profile_link = author_elem.find('h3').find('a')
            if not profile_link:
                return None
                
            href = profile_link.get('href', '')
            scholar_id = None
            if 'user=' in href:
                scholar_id = href.split('user=')[1].split('&')[0]
            
            if scholar_id:
                return self._get_scholar_profile_by_id(scholar_id)
            
            return None
            
        except Exception as e:
            print(f"Error searching author profile: {e}")
            return None
    
    def _get_author_publications(self, scholar_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get author's publications from Google Scholar"""
        publications = []
        
        try:
            url = f"https://scholar.google.com/citations?user={scholar_id}&hl=en&cstart=0&pagesize={limit}"
            
            self._delay()
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find publication table
            pub_table = soup.find('tbody', id='gsc_a_b')
            if not pub_table:
                return publications
            
            rows = pub_table.find_all('tr', class_='gsc_a_tr')
            
            for row in rows:
                try:
                    # Title and link
                    title_elem = row.find('a', class_='gsc_a_at')
                    title = title_elem.get_text() if title_elem else "Unknown"
                    
                    # Authors and publication details
                    authors_elem = row.find('div', class_='gs_gray')
                    authors = authors_elem.get_text() if authors_elem else ""
                    
                    # Citation count
                    cite_elem = row.find('a', class_='gsc_a_ac')
                    citations = 0
                    if cite_elem and cite_elem.get_text().isdigit():
                        citations = int(cite_elem.get_text())
                    
                    # Year
                    year_elem = row.find('span', class_='gsc_a_h')
                    year = year_elem.get_text() if year_elem else ""
                    
                    publications.append({
                        'title': title.strip(),
                        'authors': authors.strip(),
                        'citations': citations,
                        'year': year,
                        'source': 'Google Scholar'
                    })
                    
                except Exception as e:
                    print(f"Error parsing publication: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error getting publications: {e}")
            
        return publications
    
    def calculate_author_metrics(self, publications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate various author metrics from publication list
        
        Args:
            publications: List of publication dictionaries
            
        Returns:
            Dictionary with calculated metrics
        """
        if not publications:
            return {}
        
        # Total publications
        total_pubs = len(publications)
        
        # Total citations
        total_citations = sum(pub.get('citations', 0) for pub in publications)
        
        # H-index calculation
        citation_counts = sorted([pub.get('citations', 0) for pub in publications], reverse=True)
        h_index = 0
        for i, citations in enumerate(citation_counts, 1):
            if citations >= i:
                h_index = i
            else:
                break
        
        # i10-index (publications with at least 10 citations)
        i10_index = sum(1 for pub in publications if pub.get('citations', 0) >= 10)
        
        # Average citations per paper
        avg_citations = total_citations / total_pubs if total_pubs > 0 else 0
        
        # Publication years for career span
        years = [int(pub.get('year', 0)) for pub in publications if pub.get('year', '').isdigit()]
        career_start = min(years) if years else None
        career_span = (max(years) - min(years) + 1) if years else 0
        
        # Publications per year
        pubs_per_year = total_pubs / career_span if career_span > 0 else 0
        
        return {
            'total_publications': total_pubs,
            'total_citations': total_citations,
            'h_index': h_index,
            'i10_index': i10_index,
            'avg_citations_per_paper': round(avg_citations, 2),
            'career_start_year': career_start,
            'career_span_years': career_span,
            'publications_per_year': round(pubs_per_year, 2),
            'most_cited_paper': max(publications, key=lambda x: x.get('citations', 0)) if publications else None
        }
    
    def compare_authors(self, author_names: List[str]) -> Optional[pd.DataFrame]:
        """
        Compare multiple authors' metrics
        
        Args:
            author_names: List of author names to compare
            
        Returns:
            DataFrame with comparison data
        """
        comparison_data = []
        
        for author_name in author_names:
            profile = self.get_author_profile(author_name)
            if profile:
                comparison_data.append({
                    'author': profile.get('name', author_name),
                    'affiliation': profile.get('affiliation', ''),
                    'total_citations': profile.get('total_citations', 0),
                    'h_index': profile.get('h_index', 0),
                    'i10_index': profile.get('i10_index', 0),
                    'publications': len(profile.get('publications', [])),
                    'interests': ', '.join(profile.get('interests', [])[:3])  # Top 3 interests
                })
        
        if comparison_data:
            return pd.DataFrame(comparison_data)
        return None
    
    def get_coauthors(self, scholar_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get coauthor network for an author
        
        Args:
            scholar_id: Google Scholar ID
            limit: Maximum number of coauthors to return
            
        Returns:
            List of coauthor information
        """
        # This would require parsing coauthor information from Google Scholar
        # Placeholder implementation
        
        coauthors = []
        # In practice, this would parse the author's publications and extract coauthors
        
        return coauthors
    
    def analyze_research_evolution(self, scholar_id: str) -> Dict[str, Any]:
        """
        Analyze how an author's research has evolved over time
        
        Args:
            scholar_id: Google Scholar ID
            
        Returns:
            Analysis of research evolution
        """
        profile = self.get_author_profile("", scholar_id)
        if not profile:
            return {}
        
        publications = profile.get('publications', [])
        
        # Group publications by year
        year_data = {}
        for pub in publications:
            year = pub.get('year', '')
            if year.isdigit():
                year = int(year)
                if year not in year_data:
                    year_data[year] = []
                year_data[year].append(pub)
        
        # Analyze trends
        evolution = {
            'yearly_publication_count': {year: len(pubs) for year, pubs in year_data.items()},
            'yearly_citation_count': {year: sum(p.get('citations', 0) for p in pubs) 
                                    for year, pubs in year_data.items()},
            'research_interests': profile.get('interests', []),
            'career_timeline': sorted(year_data.keys()) if year_data else []
        }
        
        return evolution
    
    def clear_cache(self):
        """Clear the author data cache"""
        self._author_cache.clear()
    
    def close(self):
        """Close the session"""
        if hasattr(self, 'session'):
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

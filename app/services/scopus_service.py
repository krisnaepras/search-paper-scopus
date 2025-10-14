"""
Scopus API Service - Business logic for interacting with Scopus API
"""

import requests
from typing import Dict, List, Any, Optional
from fastapi import HTTPException
from app.core.config import settings


class ScopusService:
    """Service for Scopus API operations"""
    
    def __init__(self, api_key: str):
        # API key is required - no fallback to default
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.base_url = settings.scopus_base_url
        self.timeout = settings.request_timeout
        self.max_per_page = settings.max_results_per_page
    
    def set_api_key(self, api_key: str):
        """Set API key for this instance"""
        self.api_key = api_key
    
    def build_query(
        self,
        query: str,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        document_type: Optional[str] = None,
        subject_areas: Optional[List[str]] = None
    ) -> str:
        """Build Scopus query with filters"""
        full_query = query
        
        if year_from and year_to:
            full_query += f" AND PUBYEAR > {year_from-1} AND PUBYEAR < {year_to+1}"
        elif year_from:
            full_query += f" AND PUBYEAR > {year_from-1}"
        elif year_to:
            full_query += f" AND PUBYEAR < {year_to+1}"
        
        if document_type:
            full_query += f" AND DOCTYPE({document_type})"
        
        if subject_areas:
            area_query = " OR ".join([f"SUBJAREA({area})" for area in subject_areas])
            full_query += f" AND ({area_query})"
        
        return full_query
    
    def search(
        self,
        query: str,
        count: int = 25,
        start: int = 0,
        sort: str = "-citedby-count"
    ) -> Dict[str, Any]:
        """Execute single search request to Scopus API"""
        headers = {
            'X-ELS-APIKey': self.api_key,
            'Accept': 'application/json'
        }
        
        params = {
            'query': query,
            'count': min(count, self.max_per_page),
            'start': start,
            'sort': sort,
            'view': 'STANDARD'
        }
        
        try:
            response = requests.get(
                self.base_url, 
                headers=headers, 
                params=params, 
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Scopus API error: {str(e)}"
            )
    
    def parse_entry(self, entry: Dict) -> Dict[str, Any]:
        """Parse single entry from Scopus response"""
        # Get Scopus URL
        scopus_url = 'N/A'
        if entry.get('link'):
            for link in entry['link']:
                if link.get('@ref') == 'scopus':
                    scopus_url = link.get('@href', 'N/A')
                    break
        
        # Get affiliation
        affiliation = 'N/A'
        if entry.get('affiliation'):
            affs = entry['affiliation']
            if isinstance(affs, list) and len(affs) > 0:
                affiliation = affs[0].get('affilname', 'N/A')
            elif isinstance(affs, dict):
                affiliation = affs.get('affilname', 'N/A')
        
        # Get PDF link if available
        pdf_url = 'N/A'
        if entry.get('link'):
            for link in entry['link']:
                if link.get('@ref') == 'full-text' or 'pdf' in link.get('@href', '').lower():
                    pdf_url = link.get('@href', 'N/A')
                    break
        
        return {
            'title': entry.get('dc:title', 'N/A'),
            'authors': entry.get('dc:creator', 'N/A'),
            'year': entry.get('prism:coverDate', 'N/A')[:4] if entry.get('prism:coverDate') else 'N/A',
            'publication': entry.get('prism:publicationName', 'N/A'),
            'cited_by': int(entry.get('citedby-count', 0)),
            'doi': entry.get('prism:doi', 'N/A'),
            'document_type': entry.get('subtypeDescription', 'N/A'),
            'source_type': entry.get('prism:aggregationType', 'N/A'),
            'affiliation': affiliation,
            'eid': entry.get('eid', 'N/A'),
            'scopus_url': scopus_url,
            'open_access': entry.get('openaccessFlag', False),
            'pdf_url': pdf_url
        }
    
    def fetch_multiple_pages(
        self,
        query: str,
        total_limit: int,
        sort: str = "-citedby-count",
        start: int = 0
    ) -> tuple[List[Dict], int]:
        """Fetch multiple pages to get more results (supports offsets for pagination)"""
        all_entries: List[Dict] = []
        current_start = max(start, 0)
        remaining = max(total_limit, 0)
        total_available: Optional[int] = None

        while remaining > 0:
            count = min(self.max_per_page, remaining)
            result = self.search(query, count=count, start=current_start, sort=sort)

            if not result or 'search-results' not in result:
                break

            search_results = result['search-results']
            if total_available is None:
                try:
                    total_available = int(search_results.get('opensearch:totalResults', 0))
                except (TypeError, ValueError):
                    total_available = 0

            entries = search_results.get('entry', []) or []
            if not entries:
                break

            all_entries.extend(entries)
            retrieved = len(entries)
            remaining -= retrieved
            current_start += retrieved

            if total_available is not None and current_start >= total_available:
                break

            if retrieved < count:
                break

        if total_available is None:
            total_available = 0

        return all_entries[:total_limit], total_available
    
    def search_papers(
        self,
        query: str,
        limit: int,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        document_type: Optional[str] = None,
        subject_areas: Optional[List[str]] = None,
        sort_by: str = "-citedby-count",
        page: int = 1,
        use_cache: bool = True
    ) -> tuple[List[Dict], str, int]:
        """
        High-level search method with caching support
        Returns: (papers, full_query, total_available)
        """
        # Build query with filters
        full_query = self.build_query(
            query=query,
            year_from=year_from,
            year_to=year_to,
            document_type=document_type,
            subject_areas=subject_areas
        )
        
        # Check cache first if enabled
        if use_cache:
            from app.services.redis_service import redis_cache
            filters = {
                "year_from": year_from,
                "year_to": year_to,
                "document_type": document_type,
                "subject_areas": subject_areas,
                "sort_by": sort_by,
                "page": page
            }
            cached_result = redis_cache.get_cached_search(query, limit, filters)
            if cached_result:
                return (
                    cached_result["papers"],
                    cached_result["query"],
                    cached_result["total"]
                )
        
        # Fetch entries
        start_index = max(page - 1, 0) * limit
        entries, total_available = self.fetch_multiple_pages(
            full_query,
            limit,
            sort_by,
            start=start_index
        )
        
        # Parse results
        papers = [self.parse_entry(entry) for entry in entries if 'error' not in entry]

        if total_available is None:
            total_available = 0
        
        # Cache results if enabled
        if use_cache:
            from app.services.redis_service import redis_cache
            redis_cache.cache_search_results(
                query, limit, filters,
                {"papers": papers, "query": full_query, "total": total_available}
            )
        
        return papers, full_query, total_available
    
    def search_by_author(self, author_name: str, limit: int = 25) -> List[Dict]:
        """Search papers by author name"""
        query = f"AUTHOR-NAME({author_name})"
        entries, _ = self.fetch_multiple_pages(query, limit)
        return [self.parse_entry(entry) for entry in entries if 'error' not in entry]
    
    def search_by_affiliation(self, institution: str, limit: int = 25) -> List[Dict]:
        """Search papers by institution/affiliation"""
        query = f"AFFIL({institution})"
        entries, _ = self.fetch_multiple_pages(query, limit)
        return [self.parse_entry(entry) for entry in entries if 'error' not in entry]
    
    def get_paper_by_eid(self, eid: str) -> Optional[Dict]:
        """Get single paper by EID"""
        try:
            result = self.search(f'EID({eid})', count=1)
            entries = result.get('search-results', {}).get('entry', [])
            if entries:
                return self.parse_entry(entries[0])
            return None
        except Exception:
            return None


# Singleton instance removed - each user should create their own instance with their API key
scopus_service = None  # Deprecated: use ScopusService(api_key) instead

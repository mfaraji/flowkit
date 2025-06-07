#!/usr/bin/env python3
"""
Confluence utilities for managing Confluence operations.
"""

from typing import Optional, Dict, Any, List
import requests
import json


class Confluence:
    """
    Utility class for Confluence operations.
    """
    
    def __init__(self, base_url: str, username: str, api_token: str, default_space: str = None):
        """
        Initialize the Confluence interface.

        Args:
            base_url: The base URL of your Confluence instance (e.g., 'https://yourcompany.atlassian.net/wiki')
            username: Your Confluence username (email)
            api_token: Your Confluence API token
            default_space: Default space key to use for searches (optional)
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.default_space = default_space
        self.session = requests.Session()
        self.session.auth = (username, api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def test_connection(self) -> bool:
        """
        Test the connection to Confluence.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/rest/api/user/current")
            if response.status_code == 200:
                user_info = response.json()
                print(f"✓ Connected to Confluence as: {user_info.get('displayName', 'Unknown')}")
                return True
            else:
                print(f"✗ Connection failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False

    def get_spaces(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all accessible spaces.

        Returns:
            List of spaces, or None if error
        """
        try:
            response = self.session.get(f"{self.base_url}/rest/api/space")
            if response.status_code == 200:
                data = response.json()
                spaces = data.get('results', [])
                print(f"✓ Found {len(spaces)} spaces")
                return spaces
            else:
                print(f"✗ Failed to get spaces: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"✗ Error getting spaces: {e}")
            return None

    def search_content(self, query: str, space_key: str = None, content_type: str = None, 
                      limit: int = 25, start: int = 0, expand: str = None, use_default_space: bool = True) -> Optional[Dict[str, Any]]:
        """
        Search for content in Confluence.

        Args:
            query: Search query string
            space_key: Optional space key to limit search to specific space
            content_type: Optional content type filter (page, blogpost, attachment, etc.)
            limit: Maximum number of results to return (default: 25, max: 200)
            start: Starting index for pagination (default: 0)
            expand: Optional comma-separated list of properties to expand
            use_default_space: Whether to use default space if no space_key provided (default: True)

        Returns:
            Search results dictionary with results list and metadata, or None if error
        """
        try:
            # Build search parameters
            params = {
                'cql': query,
                'limit': min(limit, 200),  # Confluence API limit is 200
                'start': start
            }
            
            # Add expand parameter if provided
            if expand:
                params['expand'] = expand
            else:
                # Default expand to get useful information
                params['expand'] = 'space,history,body.view,metadata.labels'
            
            # Build CQL query with filters
            cql_parts = [query]
            
            # Use space_key if provided, otherwise use default_space if available and use_default_space is True
            effective_space = space_key
            if not effective_space and use_default_space and self.default_space:
                effective_space = self.default_space
                print(f"🏠 Using default space: {self.default_space}")
            
            if effective_space:
                cql_parts.append(f'space = "{effective_space}"')
            
            if content_type:
                cql_parts.append(f'type = "{content_type}"')
            
            # Combine CQL parts
            params['cql'] = ' AND '.join(cql_parts)
            
            print(f"🔍 Searching with CQL: {params['cql']}")
            
            response = self.session.get(f"{self.base_url}/rest/api/content/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                # Format results for better usability
                formatted_results = []
                for result in results:
                    formatted_result = {
                        'id': result.get('id'),
                        'title': result.get('title'),
                        'type': result.get('type'),
                        'status': result.get('status'),
                        'space': {
                            'key': result.get('space', {}).get('key'),
                            'name': result.get('space', {}).get('name')
                        } if result.get('space') else None,
                        'url': f"{self.base_url}{result.get('_links', {}).get('webui', '')}" if result.get('_links', {}).get('webui') else None,
                        'created': result.get('history', {}).get('createdDate') if result.get('history') else None,
                        'updated': result.get('history', {}).get('lastUpdated', {}).get('when') if result.get('history', {}).get('lastUpdated') else None,
                        'creator': {
                            'name': result.get('history', {}).get('createdBy', {}).get('displayName'),
                            'username': result.get('history', {}).get('createdBy', {}).get('username')
                        } if result.get('history', {}).get('createdBy') else None,
                        'excerpt': self._extract_excerpt(result.get('body', {}).get('view', {}).get('value', '')) if result.get('body', {}).get('view') else None,
                        'labels': [label.get('name') for label in result.get('metadata', {}).get('labels', {}).get('results', [])] if result.get('metadata', {}).get('labels') else []
                    }
                    formatted_results.append(formatted_result)
                
                search_result = {
                    'results': formatted_results,
                    'size': data.get('size', 0),
                    'limit': data.get('limit', limit),
                    'start': data.get('start', start),
                    'total_results': len(formatted_results),
                    'query': params['cql']
                }
                
                print(f"✓ Found {search_result['total_results']} results")
                return search_result
                
            else:
                print(f"✗ Search failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"✗ Error searching content: {e}")
            return None

    def search_in_space(self, space_key: str, query: str, content_type: str = None, 
                       limit: int = 25) -> Optional[List[Dict[str, Any]]]:
        """
        Search for content within a specific space.

        Args:
            space_key: The space key to search in
            query: Search query string
            content_type: Optional content type filter (page, blogpost, attachment, etc.)
            limit: Maximum number of results to return (default: 25)

        Returns:
            List of search results, or None if error
        """
        try:
            print(f"🔍 Searching in space '{space_key}' for: {query}")
            
            search_result = self.search_content(
                query=query,
                space_key=space_key,
                content_type=content_type,
                limit=limit
            )
            
            if search_result:
                return search_result['results']
            else:
                return None
                
        except Exception as e:
            print(f"✗ Error searching in space: {e}")
            return None

    def get_space_content(self, space_key: str, content_type: str = "page", 
                         limit: int = 25, start: int = 0) -> Optional[List[Dict[str, Any]]]:
        """
        Get all content from a specific space.

        Args:
            space_key: The space key
            content_type: Content type to retrieve (page, blogpost, etc.)
            limit: Maximum number of results to return (default: 25)
            start: Starting index for pagination (default: 0)

        Returns:
            List of content items, or None if error
        """
        try:
            params = {
                'spaceKey': space_key,
                'type': content_type,
                'limit': min(limit, 200),
                'start': start,
                'expand': 'space,history,body.view,metadata.labels'
            }
            
            print(f"📄 Getting {content_type} content from space '{space_key}'...")
            
            response = self.session.get(f"{self.base_url}/rest/api/content", params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                # Format results similar to search results
                formatted_results = []
                for result in results:
                    formatted_result = {
                        'id': result.get('id'),
                        'title': result.get('title'),
                        'type': result.get('type'),
                        'status': result.get('status'),
                        'space': {
                            'key': result.get('space', {}).get('key'),
                            'name': result.get('space', {}).get('name')
                        } if result.get('space') else None,
                        'url': f"{self.base_url}{result.get('_links', {}).get('webui', '')}" if result.get('_links', {}).get('webui') else None,
                        'created': result.get('history', {}).get('createdDate') if result.get('history') else None,
                        'updated': result.get('history', {}).get('lastUpdated', {}).get('when') if result.get('history', {}).get('lastUpdated') else None,
                        'creator': {
                            'name': result.get('history', {}).get('createdBy', {}).get('displayName'),
                            'username': result.get('history', {}).get('createdBy', {}).get('username')
                        } if result.get('history', {}).get('createdBy') else None,
                        'excerpt': self._extract_excerpt(result.get('body', {}).get('view', {}).get('value', '')) if result.get('body', {}).get('view') else None,
                        'labels': [label.get('name') for label in result.get('metadata', {}).get('labels', {}).get('results', [])] if result.get('metadata', {}).get('labels') else []
                    }
                    formatted_results.append(formatted_result)
                
                print(f"✓ Found {len(formatted_results)} {content_type} items in space '{space_key}'")
                return formatted_results
                
            else:
                print(f"✗ Failed to get space content: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"✗ Error getting space content: {e}")
            return None

    def _extract_excerpt(self, html_content: str, max_length: int = 200) -> str:
        """
        Extract a plain text excerpt from HTML content.

        Args:
            html_content: HTML content string
            max_length: Maximum length of excerpt

        Returns:
            Plain text excerpt
        """
        try:
            import re
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', html_content)
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            # Truncate to max length
            if len(text) > max_length:
                text = text[:max_length].rsplit(' ', 1)[0] + '...'
            return text
        except Exception:
            return html_content[:max_length] + '...' if len(html_content) > max_length else html_content 
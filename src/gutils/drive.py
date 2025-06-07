#!/usr/bin/env python3
"""
Google Drive utilities for working with Google Drive URLs and file IDs.
"""

import os
import re
from typing import Optional, List, Dict, Any

try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.errors import HttpError
except ImportError as e:
    print(f"Error: Missing required dependencies. Please install them using:")
    print("pip install -r requirements.txt")
    import sys
    sys.exit(1)

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/drive'
]


class Drive:
    """
    Utility class for Google Drive operations.
    """
    
    @staticmethod
    def extract_id(url_or_id: str) -> str:
        """
        Extract file ID from any Google Drive URL or return the ID if already provided.
        
        Supports various Google Drive URL formats:
        - Google Sheets: https://docs.google.com/spreadsheets/d/{id}/edit
        - Google Docs: https://docs.google.com/document/d/{id}/edit
        - Google Slides: https://docs.google.com/presentation/d/{id}/edit
        - Google Forms: https://docs.google.com/forms/d/{id}/edit
        - Google Drive files: https://drive.google.com/file/d/{id}/view
        - Google Drive open: https://drive.google.com/open?id={id}
        - Short URLs: https://docs.google.com/d/{id}

        Args:
            url_or_id: Either a full Google Drive URL or just the file ID

        Returns:
            The file ID

        Raises:
            ValueError: If the URL format is not recognized or ID cannot be extracted
        """
        # If it's already just an ID (no URL components), return it
        if not ('google.com' in url_or_id or 'drive.google.com' in url_or_id or 'docs.google.com' in url_or_id):
            return url_or_id
        
        # List of regex patterns for different Google Drive URL formats
        patterns = [
            # Standard Google Docs/Sheets/Slides/Forms URLs
            r'/(?:spreadsheets|document|presentation|forms)/d/([a-zA-Z0-9-_]+)',
            # Google Drive file URLs
            r'/file/d/([a-zA-Z0-9-_]+)',
            # Google Drive open URLs with id parameter
            r'[?&]id=([a-zA-Z0-9-_]+)',
            # Short Google Docs URLs
            r'/d/([a-zA-Z0-9-_]+)',
            # Alternative formats
            r'id=([a-zA-Z0-9-_]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        
        # If no pattern matches, raise an error
        raise ValueError(f"Could not extract file ID from URL: {url_or_id}")

    @staticmethod
    def find_by_name(name: str, file_type: Optional[str] = None, credentials_file: str = 'credentials.json', token_file: str = 'token.json') -> Optional[str]:
        """
        Find a Google Drive file ID by its name.

        Args:
            name: The name/title of the file to find
            file_type: Optional file type filter. Options:
                - 'spreadsheet' for Google Sheets
                - 'document' for Google Docs  
                - 'presentation' for Google Slides
                - 'form' for Google Forms
                - 'folder' for Google Drive folders
                - None for any file type
            credentials_file: Path to the OAuth2 credentials JSON file
            token_file: Path to store the access token

        Returns:
            The file ID if found and unique, or None if not found or multiple matches
        """
        # Authenticate
        creds = None

        # Load existing token
        try:
            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(
                    token_file, SCOPES)
        except Exception as e:
            print(f"Warning: Could not load existing token: {e}")

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    creds = None

            if not creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                except FileNotFoundError:
                    print(
                        f"Error: Credentials file '{credentials_file}' not found.")
                    print(
                        "Please download your OAuth2 credentials from Google Cloud Console.")
                    return None
                except Exception as e:
                    print(f"Error during authentication: {e}")
                    return None

            # Save the credentials for the next run
            try:
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Warning: Could not save token: {e}")

        try:
            # Build Drive service to search for files
            drive_service = build('drive', 'v3', credentials=creds)

            # Build the search query
            query = f"name='{name}' and trashed=false"
            
            # Add file type filter if specified
            if file_type:
                mime_types = {
                    'spreadsheet': 'application/vnd.google-apps.spreadsheet',
                    'document': 'application/vnd.google-apps.document',
                    'presentation': 'application/vnd.google-apps.presentation',
                    'form': 'application/vnd.google-apps.form',
                    'folder': 'application/vnd.google-apps.folder'
                }
                
                if file_type in mime_types:
                    query += f" and mimeType='{mime_types[file_type]}'"
                else:
                    print(f"Warning: Unknown file type '{file_type}'. Searching all file types.")

            # Search for files with the given name
            results = drive_service.files().list(
                q=query, 
                fields="files(id, name, mimeType, webViewLink)"
            ).execute()
            files = results.get('files', [])

            if not files:
                file_type_str = f" {file_type}" if file_type else ""
                print(f"✗ No{file_type_str} file found with name: '{name}'")
                return None
            elif len(files) == 1:
                file_id = files[0]['id']
                file_type_desc = files[0].get('mimeType', 'Unknown type').split('.')[-1]
                print(f"✓ Found unique file: '{name}' (ID: {file_id}, Type: {file_type_desc})")
                return file_id
            else:
                file_type_str = f" {file_type}" if file_type else ""
                print(f"✗ Multiple{file_type_str} files found with name: '{name}'")
                print("Found files:")
                for file in files:
                    file_type_desc = file.get('mimeType', 'Unknown type').split('.')[-1]
                    print(f"  - {file['name']} (ID: {file['id']}, Type: {file_type_desc})")
                print("Please use a more specific name or use the file ID directly.")
                return None

        except HttpError as error:
            print(f"HTTP Error {error.resp.status}: {error}")
            return None
        except Exception as error:
            print(f"An error occurred: {error}")
            return None
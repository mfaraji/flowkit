#!/usr/bin/env python3
"""
Google Sheets API Script

This script provides a comprehensive interface to Google Spreadsheets using the Google Sheets API.
It supports reading, writing, and managing Google Sheets data.

Usage:
    python google_sheets.py <spreadsheet_id> <sheet_name>
    
Example:
    python google_sheets.py "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms" "Class Data"
"""

import sys
import os
from typing import List, Optional, Dict, Any
import re

try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.errors import HttpError
except ImportError as e:
    print(f"Error: Missing required dependencies. Please install them using:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# Import utilities from utils module
from ..utils import save_to_csv, print_data
from .drive import Drive

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


class GoogleSheets:
    def __init__(self, spreadsheet_id: str, credentials_file: str = 'credentials.json', token_file: str = 'token.json'):
        """
        Initialize the Google Sheets interface.

        Args:
            spreadsheet_id: The ID of the spreadsheet to work with (or full URL)
            credentials_file: Path to the OAuth2 credentials JSON file
            token_file: Path to store the access token
        """
        self.spreadsheet_id = Drive.extract_id(spreadsheet_id)
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None

    @staticmethod
    def create_spreadsheet(title: str, credentials_file: str = 'credentials.json', token_file: str = 'token.json') -> Optional[str]:
        """
        Create a new Google Spreadsheet.

        Args:
            title: The title/name for the new spreadsheet
            credentials_file: Path to the OAuth2 credentials JSON file
            token_file: Path to store the access token

        Returns:
            The spreadsheet ID of the newly created spreadsheet, or None if error
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
            service = build('sheets', 'v4', credentials=creds)

            # Create the spreadsheet
            spreadsheet_body = {
                'properties': {
                    'title': title
                }
            }

            request = service.spreadsheets().create(body=spreadsheet_body)
            response = request.execute()

            spreadsheet_id = response.get('spreadsheetId')
            spreadsheet_url = response.get('spreadsheetUrl')

            print(f"✓ Successfully created spreadsheet: '{title}'")
            print(f"📄 Spreadsheet ID: {spreadsheet_id}")
            print(f"🔗 URL: {spreadsheet_url}")

            return spreadsheet_id

        except HttpError as error:
            print(f"HTTP Error {error.resp.status}: {error}")
            return None
        except Exception as error:
            print(f"An error occurred: {error}")
            return None

    @staticmethod
    def create_and_get_instance(title: str, credentials_file: str = 'credentials.json', token_file: str = 'token.json') -> Optional['GoogleSheets']:
        """
        Create a new Google Spreadsheet and return a GoogleSheets instance for it.

        Args:
            title: The title/name for the new spreadsheet
            credentials_file: Path to the OAuth2 credentials JSON file
            token_file: Path to store the access token

        Returns:
            GoogleSheets instance for the newly created spreadsheet, or None if error
        """
        spreadsheet_id = GoogleSheets.create_spreadsheet(
            title, credentials_file, token_file)

        if spreadsheet_id:
            instance = GoogleSheets(
                spreadsheet_id, credentials_file, token_file)
            if instance.authenticate():
                return instance
            else:
                print("Error: Failed to authenticate with the newly created spreadsheet")
                return None
        else:
            return None

    @staticmethod
    def find_spreadsheet_by_name(name: str, credentials_file: str = 'credentials.json', token_file: str = 'token.json') -> Optional[str]:
        """
        Find a spreadsheet ID by its name.

        Args:
            name: The name/title of the spreadsheet to find
            credentials_file: Path to the OAuth2 credentials JSON file
            token_file: Path to store the access token

        Returns:
            The spreadsheet ID if found and unique, or None if not found or multiple matches
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
            from googleapiclient.discovery import build
            drive_service = build('drive', 'v3', credentials=creds)

            # Search for spreadsheets with the given name
            query = f"name='{name}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
            results = drive_service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])

            if not files:
                print(f"✗ No spreadsheet found with name: '{name}'")
                return None
            elif len(files) == 1:
                spreadsheet_id = files[0]['id']
                print(
                    f"✓ Found unique spreadsheet: '{name}' (ID: {spreadsheet_id})")
                return spreadsheet_id
            else:
                print(f"✗ Multiple spreadsheets found with name: '{name}'")
                print("Found spreadsheets:")
                for file in files:
                    print(f"  - {file['name']} (ID: {file['id']})")
                print(
                    "Please use a more specific name or use the spreadsheet ID directly.")
                return None

        except HttpError as error:
            print(f"HTTP Error {error.resp.status}: {error}")
            return None
        except Exception as error:
            print(f"An error occurred: {error}")
            return None

    @staticmethod
    def delete_spreadsheet(spreadsheet_id: str = None, name: str = None, credentials_file: str = 'credentials.json', token_file: str = 'token.json') -> bool:
        """
        Delete a spreadsheet by ID or name.

        Args:
            spreadsheet_id: The ID of the spreadsheet to delete (optional if name is provided)
            name: The name of the spreadsheet to delete (optional if spreadsheet_id is provided)
            credentials_file: Path to the OAuth2 credentials JSON file
            token_file: Path to store the access token

        Returns:
            True if deletion successful, False otherwise
        """
        if not spreadsheet_id and not name:
            print("Error: Either spreadsheet_id or name must be provided")
            return False

        if spreadsheet_id and name:
            print("Warning: Both spreadsheet_id and name provided. Using spreadsheet_id.")

        # If name is provided, find the spreadsheet ID
        if not spreadsheet_id and name:
            spreadsheet_id = GoogleSheets.find_spreadsheet_by_name(
                name, credentials_file, token_file)
            if not spreadsheet_id:
                print(
                    f"Cannot delete: Spreadsheet '{name}' not found or multiple matches exist")
                return False

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
                    return False
                except Exception as e:
                    print(f"Error during authentication: {e}")
                    return False

            # Save the credentials for the next run
            try:
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Warning: Could not save token: {e}")

        try:
            # Build Drive service to delete the file
            from googleapiclient.discovery import build
            drive_service = build('drive', 'v3', credentials=creds)

            # Get file info first to confirm it exists and get its name
            try:
                file_info = drive_service.files().get(
                    fileId=spreadsheet_id, fields="name").execute()
                file_name = file_info.get('name', 'Unknown')
            except HttpError as e:
                if e.resp.status == 404:
                    print(
                        f"✗ Spreadsheet with ID '{spreadsheet_id}' not found")
                    return False
                else:
                    raise e

            # Confirm deletion
            print(f"⚠️  WARNING: You are about to delete the spreadsheet:")
            print(f"   Name: {file_name}")
            print(f"   ID: {spreadsheet_id}")

            confirmation = input(
                "Are you sure you want to delete this spreadsheet? (yes/no): ").lower().strip()
            if confirmation not in ['yes', 'y']:
                print("❌ Deletion cancelled by user")
                return False

            # Delete the file (move to trash)
            drive_service.files().delete(fileId=spreadsheet_id).execute()

            print(
                f"✅ Successfully deleted spreadsheet: '{file_name}' (ID: {spreadsheet_id})")
            return True

        except HttpError as error:
            print(f"HTTP Error {error.resp.status}: {error}")
            return False
        except Exception as error:
            print(f"An error occurred: {error}")
            return False

    def authenticate(self) -> bool:
        """
        Authenticate with Google Sheets API.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        creds = None

        # The file token.json stores the user's access and refresh tokens.
        try:
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(
                    self.token_file, SCOPES)
        except Exception as e:
            print(f"Warning: Could not load existing token: {e}")

        # If there are no (valid) credentials available, let the user log in.
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
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                except FileNotFoundError:
                    print(
                        f"Error: Credentials file '{self.credentials_file}' not found.")
                    print(
                        "Please download your OAuth2 credentials from Google Cloud Console.")
                    return False
                except Exception as e:
                    print(f"Error during authentication: {e}")
                    return False

            # Save the credentials for the next run
            try:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Warning: Could not save token: {e}")

        try:
            self.service = build('sheets', 'v4', credentials=creds)
            return True
        except Exception as e:
            print(f"Error building service: {e}")
            return False

    def get_sheet_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get the list of all sheets in the spreadsheet.

        Returns:
            List of dictionaries containing sheet information, or None if error
        """
        if not self.service:
            print("Error: Not authenticated. Call authenticate() first.")
            return None

        try:
            sheet = self.service.spreadsheets()
            result = sheet.get(spreadsheetId=self.spreadsheet_id).execute()
            sheets = result.get('sheets', [])

            sheet_list = []
            for sheet_data in sheets:
                sheet_props = sheet_data.get('properties', {})
                sheet_info = {
                    'name': sheet_props.get('title', 'Unknown'),
                    'id': sheet_props.get('sheetId', 0),
                    'rows': sheet_props.get('gridProperties', {}).get('rowCount', 0),
                    'columns': sheet_props.get('gridProperties', {}).get('columnCount', 0),
                    'index': sheet_props.get('index', 0)
                }
                sheet_list.append(sheet_info)

            return sheet_list

        except HttpError as error:
            print(f"HTTP Error {error.resp.status}: {error}")
            return None
        except Exception as error:
            print(f"An error occurred: {error}")
            return None

    def read_all(self, sheet_name: str) -> Optional[List[List[Any]]]:
        """
        Read all data from a specific sheet.

        Args:
            sheet_name: The name of the sheet to read

        Returns:
            List of lists containing all the spreadsheet data, or None if error
        """
        if not self.service:
            print("Error: Not authenticated. Call authenticate() first.")
            return None

        try:
            # Call the Sheets API to get all data from the sheet
            sheet = self.service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                        range=sheet_name).execute()
            values = result.get('values', [])

            if not values:
                print(f"No data found in sheet '{sheet_name}'.")
                return []

            return values

        except HttpError as error:
            if error.resp.status == 404:
                print(f"Error: Spreadsheet or sheet '{sheet_name}' not found.")
            elif error.resp.status == 403:
                print(
                    f"Error: Access denied. Please check sharing permissions for the spreadsheet.")
            else:
                print(f"HTTP Error {error.resp.status}: {error}")
            return None
        except Exception as error:
            print(f"An error occurred: {error}")
            return None

    def read_range(self, sheet_name: str, range_name: str) -> Optional[List[List[Any]]]:
        """
        Read data from a specific range in a sheet.

        Args:
            sheet_name: The name of the sheet to read
            range_name: Range specification (e.g., 'A1:D10')

        Returns:
            List of lists containing the spreadsheet data, or None if error
        """
        if not self.service:
            print("Error: Not authenticated. Call authenticate() first.")
            return None

        full_range = f"{sheet_name}!{range_name}"

        try:
            sheet = self.service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                        range=full_range).execute()
            values = result.get('values', [])

            if not values:
                print(
                    f"No data found in range '{range_name}' of sheet '{sheet_name}'.")
                return []

            return values

        except HttpError as error:
            if error.resp.status == 404:
                print(f"Error: Spreadsheet or sheet '{sheet_name}' not found.")
            elif error.resp.status == 403:
                print(f"Error: Access denied. Please check sharing permissions.")
            else:
                print(f"HTTP Error {error.resp.status}: {error}")
            return None
        except Exception as error:
            print(f"An error occurred: {error}")
            return None

    def write_row(self, sheet_name: str, row_data: List[Any], row_number: Optional[int] = None) -> bool:
        """
        Write a row of data to a sheet.

        Args:
            sheet_name: The name of the sheet to write to
            row_data: List of values to write
            row_number: Specific row number to write to (1-indexed). If None, appends to the end.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.service:
            print("Error: Not authenticated. Call authenticate() first.")
            return False

        try:
            if row_number is None:
                # Append to the end of the sheet
                range_name = f"{sheet_name}!A:A"
                value_input_option = 'USER_ENTERED'

                body = {
                    'values': [row_data]
                }

                result = self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body
                ).execute()

                print(
                    f"Row appended successfully. Updated range: {result.get('updates', {}).get('updatedRange', 'Unknown')}")
            else:
                # Write to specific row
                range_name = f"{sheet_name}!A{row_number}:{chr(65 + len(row_data) - 1)}{row_number}"

                body = {
                    'values': [row_data]
                }

                result = self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()

                print(
                    f"Row {row_number} updated successfully. {result.get('updatedCells', 0)} cells updated.")

            return True

        except HttpError as error:
            print(f"HTTP Error {error.resp.status}: {error}")
            return False
        except Exception as error:
            print(f"An error occurred: {error}")
            return False

    def write_cell(self, sheet_name: str, cell_address: str, value: Any) -> bool:
        """
        Write a value to a specific cell.

        Args:
            sheet_name: The name of the sheet to write to
            cell_address: Cell address (e.g., 'A1', 'B5')
            value: Value to write to the cell

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.service:
            print("Error: Not authenticated. Call authenticate() first.")
            return False

        try:
            range_name = f"{sheet_name}!{cell_address}"

            body = {
                'values': [[value]]
            }

            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            print(
                f"Cell {cell_address} updated successfully. {result.get('updatedCells', 0)} cells updated.")
            return True

        except HttpError as error:
            print(f"HTTP Error {error.resp.status}: {error}")
            return False
        except Exception as error:
            print(f"An error occurred: {error}")
            return False

    def write_range(self, sheet_name: str, range_name: str, data: List[List[Any]]) -> bool:
        """
        Write data to a specific range in a sheet.

        Args:
            sheet_name: The name of the sheet to write to
            range_name: Range specification (e.g., 'A1:D10')
            data: 2D list of values to write

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.service:
            print("Error: Not authenticated. Call authenticate() first.")
            return False

        try:
            full_range = f"{sheet_name}!{range_name}"

            body = {
                'values': data
            }

            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=full_range,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            print(
                f"Range {range_name} updated successfully. {result.get('updatedCells', 0)} cells updated.")
            return True

        except HttpError as error:
            print(f"HTTP Error {error.resp.status}: {error}")
            return False
        except Exception as error:
            print(f"An error occurred: {error}")
            return False

    def get_spreadsheet_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the spreadsheet.

        Returns:
            Dictionary containing spreadsheet metadata, or None if error
        """
        if not self.service:
            print("Error: Not authenticated. Call authenticate() first.")
            return None

        try:
            sheet = self.service.spreadsheets()
            result = sheet.get(spreadsheetId=self.spreadsheet_id).execute()
            return result
        except HttpError as error:
            print(f"HTTP Error {error.resp.status}: {error}")
            return None
        except Exception as error:
            print(f"An error occurred: {error}")
            return None

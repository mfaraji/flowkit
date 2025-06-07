#!/usr/bin/env python3
"""
File utilities for data export and manipulation.
"""

from typing import List, Any
import pandas as pd


def save_to_csv(data: List[List[Any]], filename: str) -> bool:
    """
    Save spreadsheet data to a CSV file.

    Args:
        data: The spreadsheet data
        filename: Output CSV filename

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        df = pd.DataFrame(data[1:], columns=data[0] if data else [])
        df.to_csv(filename, index=False)
        print(f"Data saved to '{filename}'")
        return True
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False


def print_data(data: List[List[Any]], max_rows: int = 50, max_cols: int = 10) -> None:
    """
    Print spreadsheet data in a formatted way.

    Args:
        data: The spreadsheet data
        max_rows: Maximum number of rows to display
        max_cols: Maximum number of columns to display
    """
    if not data:
        print("No data to display.")
        return

    print(
        f"\nDisplaying data ({len(data)} rows, {len(data[0]) if data else 0} columns):")
    print("-" * 80)

    # Display headers if available
    if data:
        headers = data[0][:max_cols]
        print(" | ".join(f"{str(header)[:15]:15}" for header in headers))
        print("-" * 80)

        # Display data rows
        for i, row in enumerate(data[1:max_rows], 1):
            row_data = row[:max_cols]
            # Pad row with empty strings if it's shorter than headers
            while len(row_data) < len(headers):
                row_data.append("")
            print(" | ".join(f"{str(cell)[:15]:15}" for cell in row_data))

        if len(data) > max_rows:
            print(f"... and {len(data) - max_rows} more rows") 
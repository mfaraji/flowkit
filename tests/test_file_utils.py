"""
Tests for file utilities module.
"""

import pytest
import tempfile
import os
from pathlib import Path
from personal_utils.file_utils import FileUtils


class TestFileUtils:
    """Test cases for FileUtils class."""
    
    def test_get_file_hash(self):
        """Test file hash calculation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            hash_result = FileUtils.get_file_hash(temp_file)
            assert isinstance(hash_result, str)
            assert len(hash_result) == 32  # MD5 hash length
        finally:
            os.unlink(temp_file)
    
    def test_format_bytes(self):
        """Test byte formatting."""
        assert FileUtils._format_bytes(1024) == "1.0 KB"
        assert FileUtils._format_bytes(1048576) == "1.0 MB"
        assert FileUtils._format_bytes(500) == "500.0 B"
    
    def test_get_file_info_nonexistent(self):
        """Test file info for non-existent file."""
        with pytest.raises(FileNotFoundError):
            FileUtils.get_file_info("/nonexistent/file.txt") 
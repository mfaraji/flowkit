"""
Tests for text utilities module.
"""

import pytest
from personal_utils.text_utils import TextUtils


class TestTextUtils:
    """Test cases for TextUtils class."""
    
    def test_clean_whitespace(self):
        """Test whitespace cleaning."""
        text = "  hello    world  \n\t  "
        result = TextUtils.clean_whitespace(text)
        assert result == "hello world"
    
    def test_extract_emails(self):
        """Test email extraction."""
        text = "Contact us at support@example.com or admin@test.org"
        emails = TextUtils.extract_emails(text)
        assert "support@example.com" in emails
        assert "admin@test.org" in emails
        assert len(emails) == 2
    
    def test_generate_slug(self):
        """Test slug generation."""
        text = "Hello World! This is a Test"
        slug = TextUtils.generate_slug(text)
        assert slug == "hello-world-this-is-a-test"
    
    def test_word_frequency(self):
        """Test word frequency calculation."""
        text = "hello world hello python world"
        freq = TextUtils.word_frequency(text)
        assert freq["hello"] == 2
        assert freq["world"] == 2
        assert freq["python"] == 1
    
    def test_text_similarity(self):
        """Test text similarity calculation."""
        text1 = "hello world"
        text2 = "hello python"
        similarity = TextUtils.text_similarity(text1, text2)
        assert 0 <= similarity <= 1
        assert similarity > 0  # Should have some similarity due to "hello" 
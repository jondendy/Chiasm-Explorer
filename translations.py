"""
Translation layer for accessing multiple Bible translations.
Supports Sefaria API (Hebrew + JPS 1917) and bible-api.com (WEB).
"""

import requests
import re
from typing import Dict, Optional
import streamlit as st


class TranslationService:
    """Service for fetching multiple Bible translations."""
    
    def __init__(self):
        self.sefaria_base = "https://www.sefaria.org/api/texts"
        self.bible_api_base = "https://bible-api.com"
        
    def _book_id_to_sefaria(self, book_id: str) -> str:
        """Convert book ID to Sefaria format."""
        mapping = {
            "GEN": "Genesis",
            "EXO": "Exodus",
            "LEV": "Leviticus",
            "NUM": "Numbers",
            "DEU": "Deuteronomy",
            "PSA": "Psalms"
        }
        return mapping.get(book_id, book_id)
    
    def _book_id_to_bible_api(self, book_id: str) -> str:
        """Convert book ID to bible-api.com format."""
        mapping = {
            "GEN": "Genesis",
            "EXO": "Exodus",
            "LEV": "Leviticus",
            "NUM": "Numbers",
            "DEU": "Deuteronomy",
            "PSA": "Psalms"
        }
        return mapping.get(book_id, book_id)
    
    @st.cache_data(ttl=3600)
    def get_sefaria_verse(_self, book_id: str, chapter: int, verse: int) -> Dict:
        """
        Fetch verse from Sefaria with Hebrew and JPS 1917 translation.
        Returns dict with 'hebrew', 'jps1917', 'transliteration' keys.
        """
        try:
            book_name = _self._book_id_to_sefaria(book_id)
            
            # For Psalms, chapter is actually psalm number
            if book_id == "PSA":
                url = f"{_self.sefaria_base}/{book_name}.{chapter}.{verse}"
            else:
                url = f"{_self.sefaria_base}/{book_name}.{chapter}.{verse}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract Hebrew text
            hebrew = ""
            if isinstance(data.get('he'), list) and len(data['he']) > 0:
                hebrew = data['he'][0]
            elif isinstance(data.get('he'), str):
                hebrew = data['he']
            hebrew = re.sub(r'<[^>]+>', '', hebrew)  # Clean HTML tags
            
            # Extract JPS 1917 translation
            jps1917 = ""
            if 'versions' in data:
                for version in data['versions']:
                    if 'JPS' in version.get('versionTitle', ''):
                        jps_text = version.get('text', '')
                        if isinstance(jps_text, list) and len(jps_text) > 0:
                            jps1917 = jps_text[0]
                        elif isinstance(jps_text, str):
                            jps1917 = jps_text
                        jps1917 = re.sub(r'<[^>]+>', '', jps1917)
                        break
            
            # Fallback to default English if JPS not found
            if not jps1917:
                english = data.get('text', '')
                if isinstance(english, list) and len(english) > 0:
                    jps1917 = english[0]
                elif isinstance(english, str):
                    jps1917 = english
                jps1917 = re.sub(r'<[^>]+>', '', jps1917)
            
            # Simple transliteration (Hebrew words as-is for now)
            transliteration = hebrew
            
            return {
                "hebrew": hebrew,
                "jps1917": jps1917,
                "transliteration": transliteration,
                "ref": f"{book_id}.{chapter:02d}.{verse:02d}"
            }
            
        except Exception as e:
            st.warning(f"Error fetching verse from Sefaria: {e}")
            return {
                "hebrew": "[Hebrew text unavailable]",
                "jps1917": "[Translation unavailable]",
                "transliteration": "",
                "ref": f"{book_id}.{chapter:02d}.{verse:02d}"
            }
    
    @st.cache_data(ttl=3600)
    def get_web_translation(_self, book_id: str, chapter: int, verse: int) -> str:
        """
        Fetch World English Bible translation from bible-api.com.
        """
        try:
            book_name = _self._book_id_to_bible_api(book_id)
            url = f"{_self.bible_api_base}/{book_name}+{chapter}:{verse}?translation=web"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            text = data.get('text', '').strip()
            text = re.sub(r'<[^>]+>', '', text)  # Clean HTML tags
            
            return text
            
        except Exception as e:
            return "[WEB translation unavailable]"
    
    def get_verse_all_translations(self, book_id: str, chapter: int, verse: int) -> Dict:
        """
        Get verse with all available translations.
        Returns dict with hebrew, jps1917, web, transliteration.
        """
        sefaria_data = self.get_sefaria_verse(book_id, chapter, verse)
        web_text = self.get_web_translation(book_id, chapter, verse)
        
        return {
            "hebrew": sefaria_data["hebrew"],
            "transliteration": sefaria_data["transliteration"],
            "jps1917": sefaria_data["jps1917"],
            "web": web_text,
            "ref": sefaria_data["ref"]
        }

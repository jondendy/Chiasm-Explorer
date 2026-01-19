"""
Chiasm analysis functions for Old Testament texts.
Provides middle verse, quartile analysis, and interpretive framing.
"""

from typing import Dict, List
from verse_indexing import VerseIndex
from translations import TranslationService


class ChiasmAnalyzer:
    """Analyzer for chiastic structures across OT texts."""
    
    def __init__(self, scope_id: str):
        """
        Initialize analyzer for a specific scope.
        
        Args:
            scope_id: Scope identifier (e.g., "pentateuch", "genesis")
        """
        self.scope_id = scope_id
        self.index = VerseIndex(scope_id)
        self.translation_service = TranslationService()
        
    def get_scope_summary(self) -> Dict:
        """Get summary statistics about the scope."""
        return {
            "scope_id": self.scope_id,
            "verse_count": self.index.get_verse_count(),
            "books": self.index.books
        }
    
    def get_middle_verse_analysis(self) -> Dict:
        """
        Get the exact middle verse of the scope with all translations.
        This is the theological center point for chiastic interpretation.
        """
        middle_verse = self.index.get_middle_verse()
        
        verse_data = self.translation_service.get_verse_all_translations(
            middle_verse["book_id"],
            middle_verse["chapter"],
            middle_verse["verse"]
        )
        
        return {
            "position": "Center (Q2)",
            "verse_info": middle_verse,
            "index": middle_verse["index"],
            "total_verses": self.index.get_verse_count(),
            "hebrew": verse_data["hebrew"],
            "transliteration": verse_data["transliteration"],
            "jps1917": verse_data["jps1917"],
            "web": verse_data["web"],
            "interpretation_note": "This is the exact middle verse of the entire scope - often the theological hinge point in chiastic structures."
        }
    
    def get_quartile_frame_analysis(self) -> List[Dict]:
        """
        Get quartile anchor verses (Q1, Q2/middle, Q3) with translations.
        These frame the chiastic structure and point toward the center's meaning.
        """
        quartiles = self.index.get_quartile_verses()
        results = []
        
        for position, verse_info in quartiles.items():
            verse_data = self.translation_service.get_verse_all_translations(
                verse_info["book_id"],
                verse_info["chapter"],
                verse_info["verse"]
            )
            
            interpretation_notes = {
                "Q1": "First quartile - introduces themes that will be developed toward the center",
                "Q2": "MIDDLE/CENTER - the theological hinge and interpretive key",
                "Q3": "Third quartile - echoes and resolves themes from Q1, pointing back to center"
            }
            
            results.append({
                "position": position,
                "verse_info": verse_info,
                "index": verse_info["index"],
                "hebrew": verse_data["hebrew"],
                "transliteration": verse_data["transliteration"],
                "jps1917": verse_data["jps1917"],
                "web": verse_data["web"],
                "interpretation_note": interpretation_notes[position]
            })
        
        return results
    
    def get_full_chiasm_anchors(self) -> List[Dict]:
        """
        Get all chiasm anchor points: First, Q1, Q2/Middle, Q3, Last.
        These provide the complete chiastic frame for interpretation.
        """
        anchors = self.index.get_chiasm_anchors()
        results = []
        
        position_names = {
            "first": ("Opening", "The beginning - sets the stage for the chiastic structure"),
            "Q1": ("First Quartile", "Introduces major themes pointing toward the center"),
            "Q2_middle": ("MIDDLE/CENTER", "The theological and structural hinge - the key to interpretation"),
            "Q3": ("Third Quartile", "Mirrors Q1, resolving and echoing earlier themes"),
            "last": ("Closing", "Conclusion - completes the chiastic arc")
        }
        
        for key, verse_info in anchors.items():
            verse_data = self.translation_service.get_verse_all_translations(
                verse_info["book_id"],
                verse_info["chapter"],
                verse_info["verse"]
            )
            
            position_display, note = position_names[key]
            
            results.append({
                "position": position_display,
                "key": key,
                "verse_info": verse_info,
                "index": verse_info["index"],
                "hebrew": verse_data["hebrew"],
                "transliteration": verse_data["transliteration"],
                "jps1917": verse_data["jps1917"],
                "web": verse_data["web"],
                "interpretation_note": note
            })
        
        return results
    
    def compare_anchor_themes(self, anchors: List[Dict]) -> Dict:
        """
        Analyze shared words/themes between anchor verses.
        Helps identify chiastic patterns.
        """
        # Simple word frequency analysis across anchors
        word_freq = {}
        
        for anchor in anchors:
            hebrew_words = anchor["hebrew"].split()
            for word in hebrew_words:
                word = word.strip()
                if len(word) > 2:  # Filter very short words
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Find words that appear in multiple anchors
        repeated_words = {word: count for word, count in word_freq.items() if count >= 2}
        
        return {
            "total_unique_words": len(word_freq),
            "repeated_words": repeated_words,
            "interpretation": "Repeated Hebrew words across anchor points often indicate intentional chiastic connections."
        }

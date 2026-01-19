"""
Linear verse indexing for Old Testament texts.
Provides sequential indexing across multiple books for chiasm analysis.
"""

from typing import List, Dict, Tuple
from scopes import OT_BOOKS, get_scope_books, get_verse_ref, parse_verse_ref


class VerseIndex:
    """
    Linear indexing of verses across one or more biblical books.
    """
    
    def __init__(self, scope_id: str):
        """
        Initialize verse index for a given scope.
        
        Args:
            scope_id: The scope identifier (e.g., "pentateuch", "genesis")
        """
        self.scope_id = scope_id
        self.books = get_scope_books(scope_id)
        self.verse_list = self._build_verse_list()
        
    def _build_verse_list(self) -> List[Dict]:
        """Build ordered list of all verses in scope."""
        verses = []
        
        for book_id in self.books:
            if book_id not in OT_BOOKS:
                continue
                
            book_info = OT_BOOKS[book_id]
            for chapter in range(1, book_info["chapters"] + 1):
                verse_count = book_info["verses_per_chapter"].get(chapter, 0)
                for verse in range(1, verse_count + 1):
                    verses.append({
                        "book_id": book_id,
                        "book_name": book_info["name"],
                        "chapter": chapter,
                        "verse": verse,
                        "ref": get_verse_ref(book_id, chapter, verse),
                        "index": len(verses)
                    })
        
        return verses
    
    def get_verse_count(self) -> int:
        """Get total verse count in scope."""
        return len(self.verse_list)
    
    def get_verse_by_index(self, index: int) -> Dict:
        """Get verse data by linear index."""
        if 0 <= index < len(self.verse_list):
            return self.verse_list[index]
        return None
    
    def get_verse_by_ref(self, ref: str) -> Dict:
        """Get verse data by reference string."""
        for verse in self.verse_list:
            if verse["ref"] == ref:
                return verse
        return None
    
    def get_index_by_ref(self, ref: str) -> int:
        """Get linear index by reference string."""
        verse = self.get_verse_by_ref(ref)
        return verse["index"] if verse else -1
    
    def get_middle_verse(self) -> Dict:
        """Get the middle verse of the scope."""
        n = len(self.verse_list)
        middle_index = n // 2
        return self.verse_list[middle_index]
    
    def get_quartile_verses(self) -> Dict[str, Dict]:
        """Get quartile anchor verses."""
        n = len(self.verse_list)
        return {
            "Q1": self.verse_list[n // 4],
            "Q2": self.verse_list[n // 2],  # Middle
            "Q3": self.verse_list[3 * n // 4]
        }
    
    def get_chiasm_anchors(self) -> Dict[str, Dict]:
        """
        Get key anchor points for chiastic analysis.
        Returns first, Q1, middle, Q3, and last verses.
        """
        n = len(self.verse_list)
        return {
            "first": self.verse_list[0],
            "Q1": self.verse_list[n // 4],
            "Q2_middle": self.verse_list[n // 2],
            "Q3": self.verse_list[3 * n // 4],
            "last": self.verse_list[n - 1]
        }

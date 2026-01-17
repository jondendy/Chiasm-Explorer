import streamlit as st
import pandas as pd
import requests
import json
import re
from typing import Dict, List, Tuple

# Sefaria API endpoint for Psalms
SEFARIA_API_BASE = "https://www.sefaria.org/api/texts/Psalms.{}"

@st.cache_data
def load_psalm_from_sefaria(psalm_number: int) -> Dict:
    """Load a specific Psalm from Sefaria API"""
    try:
        url = SEFARIA_API_BASE.format(psalm_number)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error loading Psalm {psalm_number}: {e}")
        return None

def parse_psalm_sefaria(sefaria_data: Dict, psalm_number: int) -> List[Dict]:
    """Parse Sefaria API data into structured format"""
    if not sefaria_data or 'he' not in sefaria_data:
        return []
    
    verses = []
    hebrew_verses = sefaria_data['he']
    english_verses = sefaria_data.get('text', [])
    
    # Handle both single verse and multi-verse Psalms
    if isinstance(hebrew_verses, str):
        hebrew_verses = [hebrew_verses]
    if isinstance(english_verses, str):
        english_verses = [english_verses]
    
    for idx, hebrew_text in enumerate(hebrew_verses, 1):
        # Clean HTML tags from Hebrew text
        clean_hebrew = re.sub(r'<[^>]+>', '', hebrew_text)
        
        # Get corresponding English translation
        english_text = ""
        if idx <= len(english_verses):
            english_text = re.sub(r'<[^>]+>', '', english_verses[idx-1])
        
        # Extract individual Hebrew words for lemma analysis
        hebrew_words = clean_hebrew.split()
        
        # For Sefaria data, we create simple lemmas from the words themselves
        # (Sefaria doesn't provide morphological data in the basic API)
        lemmas = [(word, word) for word in hebrew_words if word.strip()]
        
        verses.append({
            "verse": idx,
            "hebrew": clean_hebrew,
            "english": english_text,
            "hebrew_words": hebrew_words,
            "lemmas": lemmas
        })
    
    return verses

def highlight_lemmas_in_text(hebrew_text: str, lemmas_to_highlight: List[str], color: str = "#FFEB99") -> str:
    """Highlight specific lemmas in Hebrew text with light background color"""
    if not lemmas_to_highlight:
        return hebrew_text
    
    highlighted_text = hebrew_text
    for lemma in lemmas_to_highlight:
        if lemma.strip():
            pattern = f"({re.escape(lemma)})"
            highlighted_text = re.sub(pattern, f'<mark style="background-color: {color}; padding: 2px 4px; border-radius: 3px;">\\1</mark>', highlighted_text)
    
    return highlighted_text

def compute_pairings(psalm_data: List[Dict]) -> List[Dict]:
    """Compute chiastic verse pairings"""
    n = len(psalm_data)
    pairs = []
    
    for i in range(n // 2):
        pair_type = "Outer Mirror" if i == 0 else "Quartile Echo"
        v1 = psalm_data[i]
        v2 = psalm_data[n - 1 - i]
        
        # Extract words for comparison
        words_1 = set(word.strip() for word in v1["hebrew_words"] if word.strip())
        words_2 = set(word.strip() for word in v2["hebrew_words"] if word.strip())
        shared_words = words_1 & words_2
        
        # Get shared word details
        shared_details = [(word, word) for word in shared_words]
        shared_hebrew = list(shared_words)
        
        pairs.append({
            "type": pair_type,
            "verse_1": v1,
            "verse_2": v2,
            "shared_lemmas": shared_details,
            "shared_hebrew": shared_hebrew
        })
    
    # Handle center verse if odd number
    if n % 2 == 1:
        center = psalm_data[n // 2]
        pairs.append({
            "type": "Center Hinge",
            "verse_1": center,
            "verse_2": None,
            "shared_lemmas": [],
            "shared_hebrew": []
        })
    
    return pairs

# Streamlit UI
st.set_page_config(page_title="Psalm Chiasm Explorer", layout="wide")
st.title("📖 Psalm Chiasm Explorer")
st.markdown("*Exploring chiastic structures in Biblical Psalms with Hebrew text analysis*")

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    
    # Psalm selector
    psalm_number = st.selectbox(
        "Select Psalm",
        options=list(range(1, 151)),
        index=22  # Default to Psalm 23
    )
    
    st.markdown("---")
    
    min_lemmas = st.slider("Minimum shared words to display", 0, 5, 0)
    show_lemmas = st.checkbox("Show word details", value=True)
    highlight_shared = st.checkbox("Highlight shared words in text", value=True)
    show_english = st.checkbox("Show English translation", value=True)
    
    st.markdown("---")
    st.markdown("### About Chiasm")
    st.markdown("""
    A **chiasm** (or chiastic structure) is a literary pattern where concepts 
    are presented in mirrored sequence (A-B-C-B'-A'). 
    
    The **center** often holds the theological key to the passage.
    
    **Shared words** are Hebrew words that appear in both paired verses,
    suggesting intentional literary connections.
    """)
    
    st.markdown("---")
    st.caption("📚 Data: Sefaria.org Hebrew Bible")

# Load Psalm data
with st.spinner(f"Loading Psalm {psalm_number}..."):
    sefaria_data = load_psalm_from_sefaria(psalm_number)

if sefaria_data:
    psalm_data = parse_psalm_sefaria(sefaria_data, psalm_number)
    
    if not psalm_data:
        st.error("Failed to parse Psalm data. The Psalm may not be available.")
    else:
        st.markdown("---")
        st.subheader(f"Psalm {psalm_number}")
        st.caption(f"{len(psalm_data)} verses | Hebrew text from Sefaria")
        
        if len(psalm_data) < 2:
            st.warning("This Psalm is too short for chiastic analysis (requires at least 2 verses).")
        else:
            # Compute pairings
            pairs = compute_pairings(psalm_data)
            
            # Display pairs
            for pair in pairs:
                if len(pair["shared_lemmas"]) < min_lemmas and pair["type"] != "Center Hinge":
                    continue
                
                # Choose color based on type
                if pair["type"] == "Outer Mirror":
                    bg_color = "#FFE4E1"  # Coral/peach
                    emoji = "🔴"
                elif pair["type"] == "Quartile Echo":
                    bg_color = "#FFF8DC"  # Gold
                    emoji = "🟡"
                else:  # Center Hinge
                    bg_color = "#E6E6FA"  # Lavender
                    emoji = "🟣"
                
                with st.container():
                    st.markdown(f"<div style='background-color: {bg_color}; padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
                    st.markdown(f"### {emoji} {pair['type']}")
                    
                    if pair["verse_2"] is not None:
                        # Two-column layout for pairs
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Verse {pair['verse_1']['verse']}**")
                            
                            # Highlight shared words if enabled
                            if highlight_shared and pair["shared_hebrew"]:
                                hebrew_highlighted = highlight_lemmas_in_text(
                                    pair['verse_1']['hebrew'], 
                                    pair['shared_hebrew']
                                )
                                st.markdown(f"*{hebrew_highlighted}*", unsafe_allow_html=True)
                            else:
                                st.markdown(f"*{pair['verse_1']['hebrew']}*")
                            
                            if show_english and pair['verse_1'].get('english'):
                                st.markdown(f"\n{pair['verse_1']['english']}")
                        
                        with col2:
                            st.markdown(f"**Verse {pair['verse_2']['verse']}**")
                            
                            # Highlight shared words if enabled
                            if highlight_shared and pair["shared_hebrew"]:
                                hebrew_highlighted = highlight_lemmas_in_text(
                                    pair['verse_2']['hebrew'], 
                                    pair['shared_hebrew']
                                )
                                st.markdown(f"*{hebrew_highlighted}*", unsafe_allow_html=True)
                            else:
                                st.markdown(f"*{pair['verse_2']['hebrew']}*")
                            
                            if show_english and pair['verse_2'].get('english'):
                                st.markdown(f"\n{pair['verse_2']['english']}")
                        
                        # Show shared words
                        if show_lemmas and pair["shared_lemmas"]:
                            st.markdown(f"\n🏷️ **Shared words ({len(pair['shared_lemmas'])})**")
                            
                            with st.expander("View word details"):
                                lemma_df = pd.DataFrame(pair["shared_lemmas"], columns=["Hebrew Word", "Word Form"])
                                st.table(lemma_df)
                    
                    else:
                        # Center verse (single column)
                        st.markdown(f"**⭐ Verse {pair['verse_1']['verse']} — Theological Hinge ⭐**")
                        st.markdown(f"*{pair['verse_1']['hebrew']}*")
                        
                        if show_english and pair['verse_1'].get('english'):
                            st.markdown(f"\n{pair['verse_1']['english']}")
                        
                        st.info("This central verse often contains the main theological point of the entire Psalm.")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("❌ Failed to load Psalm data. Please check your internet connection or try again later.")
    st.info("💡 The app fetches data from Sefaria.org, a comprehensive Jewish texts library.")

st.markdown("---")
st.markdown("### Features")
st.markdown("""
- **✅ Psalm selector** – Choose any Psalm (1-150)
- **✅ Sefaria integration** – Reliable Hebrew text and English translations
- **✅ Word highlighting** – Shared words highlighted in yellow
- **✅ English translations** – Toggle to show/hide English text
- **🔄 Future**: Enhanced lemma analysis with morphological tagging
""")

st.caption("Built with Streamlit | Data: Sefaria.org | Text: CC BY-SA 4.0")

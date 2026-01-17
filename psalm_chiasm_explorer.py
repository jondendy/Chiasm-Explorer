import streamlit as st
import pandas as pd
import requests
import json
import re
from typing import Dict, List, Tuple

# OSHB Psalm mapping (book 19 in OSHB)
OSHB_BASE_URL = "https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Ps.json"

@st.cache_data
def load_oshb_psalms():
    """Load all Psalms from OSHB GitHub repository"""
    try:
        response = requests.get(OSHB_BASE_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        st.error(f"Error loading OSHB data: {e}")
        return None

def parse_psalm(psalm_data: List, psalm_number: int) -> List[Dict]:
    """Parse OSHB JSON data for a specific psalm into structured format"""
    verses = []
    
    for verse_idx, verse in enumerate(psalm_data, 1):
        hebrew_words = []
        lemmas = []
        
        for word in verse:
            if len(word) >= 3:
                word_text = word[0]  # Hebrew word
                lemma = word[1] if len(word) > 1 else ""
                morph = word[2] if len(word) > 2 else ""
                
                # Clean lemma (remove prefixes like 'a/', 'c/', etc.)
                clean_lemma = re.sub(r'^[a-z]/', '', lemma) if lemma else ""
                
                hebrew_words.append(word_text)
                if clean_lemma:
                    lemmas.append((clean_lemma, word_text))
        
        # Join Hebrew words with spaces
        hebrew_text = " ".join(hebrew_words)
        
        verses.append({
            "verse": verse_idx,
            "hebrew": hebrew_text,
            "hebrew_words": hebrew_words,
            "lemmas": lemmas
        })
    
    return verses

def highlight_lemmas_in_text(hebrew_text: str, lemmas_to_highlight: List[str], color: str = "#FFEB99") -> str:
    """Highlight specific lemmas in Hebrew text with light background color"""
    if not lemmas_to_highlight:
        return hebrew_text
    
    # Create a pattern that matches any of the lemmas
    highlighted_text = hebrew_text
    for lemma in lemmas_to_highlight:
        # Use word boundary to match whole words
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
        
        # Extract lemma IDs for comparison (just the Strong's-like number)
        lemmas_1 = {lem[0] for lem in v1["lemmas"]}
        lemmas_2 = {lem[0] for lem in v2["lemmas"]}
        shared = lemmas_1 & lemmas_2
        
        # Get shared lemma details with Hebrew forms
        shared_details = []
        shared_hebrew = []
        for lem in v1["lemmas"]:
            if lem[0] in shared:
                shared_details.append(lem)
                shared_hebrew.append(lem[1])
        
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
st.markdown("*Exploring chiastic structures in Biblical Psalms with Hebrew lemma analysis*")

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
    
    min_lemmas = st.slider("Minimum shared lemmas to display", 0, 5, 0)
    show_lemmas = st.checkbox("Show lemma details", value=True)
    highlight_shared = st.checkbox("Highlight shared lemmas in text", value=True)
    
    st.markdown("---")
    st.markdown("### About Chiasm")
    st.markdown("""
    A **chiasm** (or chiastic structure) is a literary pattern where concepts 
    are presented in mirrored sequence (A-B-C-B'-A'). 
    
    The **center** often holds the theological key to the passage.
    
    **Shared lemmas** are Hebrew root words that appear in both paired verses,
    suggesting intentional literary connections.
    """)
    
    st.markdown("---")
    st.caption("📚 Data: Open Scriptures Hebrew Bible (OSHB)")

# Load OSHB data
with st.spinner("Loading Hebrew Bible data..."):
    all_psalms = load_oshb_psalms()

if all_psalms and len(all_psalms) >= psalm_number:
    # Parse the selected psalm (subtract 1 for 0-based index)
    psalm_data = parse_psalm(all_psalms[psalm_number - 1], psalm_number)
    
    st.markdown("---")
    st.subheader(f"Psalm {psalm_number}")
    st.caption(f"{len(psalm_data)} verses | Hebrew text from Westminster Leningrad Codex")
    
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
                        
                        # Highlight shared lemmas if enabled
                        if highlight_shared and pair["shared_hebrew"]:
                            hebrew_highlighted = highlight_lemmas_in_text(
                                pair['verse_1']['hebrew'], 
                                pair['shared_hebrew']
                            )
                            st.markdown(f"*{hebrew_highlighted}*", unsafe_allow_html=True)
                        else:
                            st.markdown(f"*{pair['verse_1']['hebrew']}*")
                    
                    with col2:
                        st.markdown(f"**Verse {pair['verse_2']['verse']}**")
                        
                        # Highlight shared lemmas if enabled
                        if highlight_shared and pair["shared_hebrew"]:
                            hebrew_highlighted = highlight_lemmas_in_text(
                                pair['verse_2']['hebrew'], 
                                pair['shared_hebrew']
                            )
                            st.markdown(f"*{hebrew_highlighted}*", unsafe_allow_html=True)
                        else:
                            st.markdown(f"*{pair['verse_2']['hebrew']}*")
                    
                    # Show shared lemmas
                    if show_lemmas and pair["shared_lemmas"]:
                        st.markdown(f"\n🏷️ **Shared lemmas ({len(pair['shared_lemmas'])})**")
                        
                        with st.expander("View lemma details"):
                            lemma_df = pd.DataFrame(pair["shared_lemmas"], columns=["Lemma ID", "Hebrew Form"])
                            st.table(lemma_df)
                
                else:
                    # Center verse (single column)
                    st.markdown(f"**⭐ Verse {pair['verse_1']['verse']} — Theological Hinge ⭐**")
                    st.markdown(f"*{pair['verse_1']['hebrew']}*")
                    st.info("This central verse often contains the main theological point of the entire Psalm.")
                
                st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("❌ Failed to load Psalm data. Please check your internet connection or try again later.")
    st.info("💡 The app fetches data from the Open Scriptures Hebrew Bible (OSHB) repository on GitHub.")

st.markdown("---")
st.markdown("### Next Steps")
st.markdown("""
- **✅ Psalm selector** – Choose any Psalm (1-150)
- **✅ OSHB integration** – Live Hebrew text with lemma data
- **✅ Lemma highlighting** – Shared words highlighted in yellow
- **🔄 Coming soon**: English translation comparison, deeper semantic analysis
""")

st.caption("Built with Streamlit | Data: Open Scriptures Hebrew Bible (OSHB) | License: CC BY 4.0")

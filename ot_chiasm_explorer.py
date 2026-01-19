"""
Old Testament Chiasm Explorer - Main UI
Explores chiastic structures across any OT text or series of texts.
"""

import streamlit as st
import pandas as pd
from scopes import SCOPES
from verse_indexing import VerseIndex
from chiasm_analysis import ChiasmAnalyzer

# Page config
st.set_page_config(
    page_title="OT Chiasm Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("📚 Old Testament Chiasm Explorer")
st.markdown("*Explore chiastic structures across the Old Testament using quartile analysis and middle verse interpretation*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Scope selector
    scope_options = {k: v["name"] for k, v in SCOPES.items()}
    selected_scope = st.selectbox(
        "Select Text Scope",
        options=list(scope_options.keys()),
        format_func=lambda x: scope_options[x],
        index=0  # Default to Pentateuch
    )
    
    st.markdown("---")
    
    # Analysis options
    st.subheader("Analysis Options")
    show_hebrew = st.checkbox("Show Hebrew text", value=True)
    show_transliteration = st.checkbox("Show transliteration", value=True)
    show_jps1917 = st.checkbox("Show JPS 1917", value=True)
    show_web = st.checkbox("Show World English Bible", value=False)
    
    st.markdown("---")
    
    # Info
    st.subheader("About Chiastic Analysis")
    st.markdown("""
    **Chiasm** is a literary structure where elements mirror each other (A-B-C-B'-A').
    
    The **middle verse** is the theological and structural center - the key to interpreting the entire passage.
    
    **Quartile analysis** examines verses at Q1 (25%), Q2 (50%/middle), and Q3 (75%) to see how they frame the center's meaning.
    """)
    
    st.markdown("---")
    st.caption("Data: Sefaria.org • bible-api.com")

# Load scope info
scope_info = SCOPES[selected_scope]
st.subheader(f"📖 {scope_info['name']}")
st.caption(scope_info['description'])

# Initialize analyzer
with st.spinner("Analyzing chiastic structure..."):
    analyzer = Ch

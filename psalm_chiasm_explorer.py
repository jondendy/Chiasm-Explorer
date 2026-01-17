import streamlit as st
import pandas as pd

# Sample data for Psalm 23 with Hebrew lemmas and glosses
psalm_23_data = [
    {
        "verse": 1,
        "hebrew": "יְהוָה רֹעִי לֹא אֶחְסָר",
        "english": "The LORD is my shepherd; I shall not want.",
        "lemmas": [("H3068", "יהוה", "YHWH"), ("H7462", "רעה", "shepherd"), ("H3808", "לא", "not"), ("H2637", "חסר", "lack")]
    },
    {
        "verse": 2,
        "hebrew": "בִּנְאוֹת דֶּשֶׁא יַרְבִּיצֵנִי עַל־מֵי מְנֻחוֹת יְנַהֲלֵנִי",
        "english": "He makes me lie down in green pastures; He leads me beside quiet waters.",
        "lemmas": [("H5116", "נוה", "pasture"), ("H1877", "דשא", "grass"), ("H7257", "רבץ", "lie down"), ("H4325", "מים", "water"), ("H4496", "מנוחה", "rest"), ("H5095", "נהל", "lead")]
    },
    {
        "verse": 3,
        "hebrew": "נַפְשִׁי יְשׁוֹבֵב יַנְחֵנִי בְמַעְגְּלֵי־צֶדֶק לְמַעַן שְׁמוֹ",
        "english": "He restores my soul; He guides me in paths of righteousness for His name's sake.",
        "lemmas": [("H5315", "נפש", "soul"), ("H7725", "שוב", "restore"), ("H5148", "נחה", "guide"), ("H4570", "מעגל", "path"), ("H6664", "צדק", "righteousness"), ("H8034", "שם", "name")]
    },
    {
        "verse": 4,
        "hebrew": "גַּם כִּי־אֵלֵךְ בְּגֵיא צַלְמָוֶת לֹא־אִירָא רָע כִּי־אַתָּה עִמָּדִי שִׁבְטְךָ וּמִשְׁעַנְתֶּךָ הֵמָּה יְנַחֲמֻנִי",
        "english": "Even though I walk through the valley of the shadow of death, I will fear no evil, for You are with me; Your rod and Your staff, they comfort me.",
        "lemmas": [("H1571", "גם", "even"), ("H1980", "הלך", "walk"), ("H1516", "גיא", "valley"), ("H6757", "צלמות", "death-shadow"), ("H3808", "לא", "not"), ("H3372", "ירא", "fear"), ("H7451", "רע", "evil"), ("H5973", "עם", "with"), ("H7626", "שבט", "rod"), ("H4938", "משענת", "staff"), ("H5162", "נחם", "comfort")]
    },
    {
        "verse": 5,
        "hebrew": "תַּעֲרֹךְ לְפָנַי שֻׁלְחָן נֶגֶד צֹרְרָי דִּשַּׁנְתָּ בַשֶּׁמֶן רֹאשִׁי כּוֹסִי רְוָיָה",
        "english": "You prepare a table before me in the presence of my enemies; You anoint my head with oil; my cup overflows.",
        "lemmas": [("H6186", "ערך", "arrange"), ("H6440", "פנים", "face"), ("H7979", "שלחן", "table"), ("H5048", "נגד", "before"), ("H6887", "צרר", "enemy"), ("H1878", "דשן", "anoint"), ("H8081", "שמן", "oil"), ("H7218", "ראש", "head"), ("H3563", "כוס", "cup"), ("H7310", "רויה", "overflow")]
    },
    {
        "verse": 6,
        "hebrew": "אַךְ טוֹב וָחֶסֶד יִרְדְּפוּנִי כָּל־יְמֵי חַיָּי וְשַׁבְתִּי בְּבֵית־יְהוָה לְאֹרֶךְ יָמִים",
        "english": "Surely goodness and mercy shall follow me all the days of my life, and I shall dwell in the house of the LORD forever.",
        "lemmas": [("H389", "אך", "surely"), ("H2896", "טוב", "good"), ("H2617", "חסד", "mercy"), ("H7291", "רדף", "follow"), ("H3117", "יום", "day"), ("H2416", "חיים", "life"), ("H7725", "שוב", "return"), ("H1004", "בית", "house"), ("H3068", "יהוה", "YHWH"), ("H753", "ארך", "length")]
    }
]

# Compute verse pairings
def compute_pairings(psalm_data):
    n = len(psalm_data)
    pairs = []
    
    for i in range(n // 2):
        pair_type = "Outer Mirror" if i == 0 else "Quartile Echo"
        v1 = psalm_data[i]
        v2 = psalm_data[n - 1 - i]
        
        # Extract lemma IDs for comparison
        lemmas_1 = {lem[0] for lem in v1["lemmas"]}
        lemmas_2 = {lem[0] for lem in v2["lemmas"]}
        shared = lemmas_1 & lemmas_2
        
        # Get shared lemma details
        shared_details = []
        for lem in v1["lemmas"]:
            if lem[0] in shared:
                shared_details.append(lem)
        
        pairs.append({
            "type": pair_type,
            "verse_1": v1,
            "verse_2": v2,
            "shared_lemmas": shared_details
        })
    
    # Handle center verse if odd number
    if n % 2 == 1:
        center = psalm_data[n // 2]
        pairs.append({
            "type": "Center Hinge",
            "verse_1": center,
            "verse_2": None,
            "shared_lemmas": []
        })
    
    return pairs

# Streamlit UI
st.set_page_config(page_title="Psalm Chiasm Explorer", layout="wide")
st.title("📖 Psalm Chiasm Explorer")
st.markdown("*Exploring chiastic structures in Biblical Psalms with Hebrew lemma analysis*")

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    min_lemmas = st.slider("Minimum shared lemmas to display", 0, 5, 0)
    show_lemmas = st.checkbox("Show lemma details", value=True)
    st.markdown("---")
    st.markdown("### About Chiasm")
    st.markdown("""
    A **chiasm** (or chiastic structure) is a literary pattern where concepts 
    are presented in mirrored sequence (A-B-C-B'-A'). 
    
    The **center** often holds the theological key to the passage.
    """)

st.markdown("---")
st.subheader("Psalm 23")
st.caption("Demonstration using actual OSHB Hebrew lemma data")

# Compute pairings
pairs = compute_pairings(psalm_23_data)

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
                st.markdown(f"*{pair['verse_1']['hebrew']}*")
                st.markdown(pair['verse_1']['english'])
            
            with col2:
                st.markdown(f"**Verse {pair['verse_2']['verse']}**")
                st.markdown(f"*{pair['verse_2']['hebrew']}*")
                st.markdown(pair['verse_2']['english'])
            
            # Show shared lemmas
            if show_lemmas and pair["shared_lemmas"]:
                st.markdown(f"\n🏷️ **Shared lemmas ({len(pair['shared_lemmas'])})**")
                
                with st.expander("View lemma details"):
                    lemma_df = pd.DataFrame(pair["shared_lemmas"], columns=["Strong's", "Hebrew", "Gloss"])
                    st.table(lemma_df)
        
        else:
            # Center verse (single column)
            st.markdown(f"**⭐ Verse {pair['verse_1']['verse']} — Theological Hinge ⭐**")
            st.markdown(f"*{pair['verse_1']['hebrew']}*")
            st.markdown(pair['verse_1']['english'])
            st.info("This central verse often contains the main theological point of the entire Psalm.")
        
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### Next Steps")
st.markdown("""
- **Expand to more Psalms** using OSHB data (GitHub repo: `openscriptures/morphhb`)
- **Add API integration** for multiple Bible versions (e.g., API.Bible, getBible)
- **Lemma scoring** using semantic similarity or frequency analysis
- **User uploads** for custom Psalms or passages
""")

st.caption("Built with Streamlit | Data: Open Scriptures Hebrew Bible")

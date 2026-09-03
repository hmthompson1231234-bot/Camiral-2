import streamlit as st
import pandas as pd
import threading

st.set_page_config(page_title="Camiral Invitational '26", layout="centered", initial_sidebar_state="collapsed")

# --- BULLETPROOF MASTERS CSS ---
st.markdown("""
<style>
    /* Force overall background to crisp white */
    .stApp { background-color: #F8F9FA !important; }
    
    /* Fix invisible text (forces all standard text to dark grey) */
    .stMarkdown p, .stExpander p, label, .stRadio div { color: #2C3E50 !important; font-weight: 500; }
    
    /* Typography - Augusta Green Headers */
    h1, h2, h3 { color: #005A34 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    h1 { border-bottom: 3px solid #EAD15F !important; padding-bottom: 10px; }
    
    /* Fix Dark Input Boxes & Dropdowns */
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        border: 1px solid #005A34 !important;
        border-radius: 4px !important;
    }
    
    /* Master's Green Buttons */
    .stButton>button { 
        background-color: #005A34 !important; 
        color: white !important; 
        border-radius: 6px !important; 
        font-weight: bold !important; 
        border: 1px solid #005A34 !important;
        width: 100%;
    }
    .stButton>button:active {
        background-color: #EAD15F !important;
        color: #005A34 !important;
    }
    
    /* Red Bullshit Button */
    .stButton:last-of-type>button { background-color: #D32F2F !important; border-color: #D32F2F !important; }
    
    /* Clean Table Styling */
    [data-testid="stDataFrame"] { background-color: #FFFFFF !important; border-radius: 8px; border: 1px solid #005A34; }
</style>
""", unsafe_allow_html=True)

# --- COURSE & PLAYER DATA ---
HOLES = list(range(1, 19))
PARS = [4, 3, 4, 4, 5, 4, 5, 3, 4,  5, 3, 4, 4, 3, 5, 3, 4, 5]
SIS  = [14, 18, 6, 2, 16, 12, 8, 4, 10,  9, 7, 11, 1, 13, 5, 17, 3, 15]

PLAYERS = {
    "Tommy": {"hcp": 14, "group": 1}, "Hidde": {"hcp": 15, "group": 1},
    "Weeman": {"hcp": 20, "group": 1}, "Brad": {"hcp": 22, "group": 1},
    "Harry": {"hcp": 14, "group": 2}, "James": {"hcp": 16, "group": 2}, "Ted": {"hcp": 22, "group": 2}
}

@st.cache_resource
def get_score_db():
    cols = HOLES + ['bullshit']
    return {
        "lock": threading.Lock(), 
        "data": pd.DataFrame(index=list(PLAYERS.keys()), columns=cols).fillna(0)
    }

db_wrapper = get_score_db()
db = db_wrapper["data"]
db_lock = db_wrapper["lock"]

def calc_stableford(player, hole, gross):
    if gross <= 0:
        return 0
    hcp = PLAYERS[player]["hcp"]
    par = PARS[hole-1]
    si = SIS[hole-1]
    extra_strokes = (hcp // 18) + (1 if (hcp % 18) >= si else 0)
    net_score = gross - extra_strokes
    return max(0, par - net_score + 2)

# --- APP HEADER ---
st.title("⛳️ CAMIRAL INVITATIONAL")

with st.expander("📖 How to use this app (Read First)"):
    st.write("""
    **1. Scoring:** Select your group, select the hole, and log the gross strokes. The app handles the Stableford math based on your handicaps.
    **2. Leaderboard:** Check the 'Leaderboard' tab for the live standings. Hit the Refresh button to pull the other group's scores!
    **3. The BS Button:** If someone cheats, go to the bottom of the Scorecard tab and smash the red button.
    """)

tab1

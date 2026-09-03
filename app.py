import streamlit as st
import pandas as pd

# Set up the app UI to be wider and mobile-friendly
st.set_page_config(page_title="Camiral Invitational '26", layout="centered", initial_sidebar_state="collapsed")

# --- CUSTOM MASTERS/CAMIRAL CSS ---
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #F8F9FA;
    }
    /* Masters Green typography */
    h1, h2, h3, p, span {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    h1 {
        color: #005A34 !important; 
        font-weight: 700;
        text-align: center;
        border-bottom: 2px solid #005A34;
        padding-bottom: 10px;
    }
    h2, h3 {
        color: #005A34 !important;
    }
    /* Custom Button Styling */
    .stButton>button {
        background-color: #005A34;
        color: white;
        border-radius: 4px;
        border: none;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #003F24;
        color: white;
    }
    /* Danger Button for Bullshit */
    .btn-danger>button {
        background-color: #D32F2F !important;
    }
    /* Table Styling */
    [data-testid="stDataFrame"] {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- COURSE & PLAYER DATA ---
HOLES = list(range(1, 19))
PARS = [4, 3, 4, 4, 5, 4, 5, 3, 4,  5, 3, 4, 4, 3, 5, 3, 4, 5]
SIS  = [14, 18, 6, 2, 16, 12, 8, 4, 10,  9, 7, 11, 1, 13, 5, 17, 3, 15]

PLAYERS = {
    "Tommy": {"hcp": 14, "group": 1},
    "Hidde": {"hcp": 15, "group": 1},
    "Weeman": {"hcp": 20, "group": 1},
    "Brad": {"hcp": 22, "group": 1},
    "Harry": {"hcp": 14, "group": 2},
    "James": {"hcp": 16, "group": 2},
    "Ted": {"hcp": 22, "group": 2}
}

@st.cache_resource
def get_score_db():
    cols = HOLES + ['bullshit']
    return pd.DataFrame(index=list(PLAYERS.keys()), columns=cols).fillna(0)

db = get_score_db()

def calc_stableford(player, hole, gross):
    if gross == 0:
        return 0
    hcp = PLAYERS[player]["hcp"]
    par = PARS[hole-1]
    si = SIS[hole-1]
    extra_strokes = (hcp // 18) + (1 if (hcp % 18) >= si else 0)
    net_score = gross - extra_strokes
    return max(0, par - net_score + 2)

# --- APP HEADER ---
st.title("⛳️ CAMIRAL INVITATIONAL")
st.markdown("<p style='text-align: center; color: #555;'>Tour Course (Yellow Tees) • Live Scoring</p>", unsafe_allow_html=True)

with st.expander("📖 How to use this app (Read First)"):
    st.write("""
    **1. Scoring:** Go to the 'Scorecard' tab. Select your group, select the hole, and log the gross strokes for everyone in your group. The app handles the Stableford math based on your handicaps.
    **2. Leaderboard:** Check the 'Leaderboard' tab for the live standings. It calculates your 'THRU' (holes played) automatically. Hit the Refresh button to pull the other group's scores!
    **3. The BS Button:** If someone cheats, go to the bottom of the Scorecard tab and smash the red button.
    """)

tab1, tab2, tab3 = st.tabs(["📝 Scorecard", "🏆 Leaderboard", "⛳️ Course"])

# --- SCORECARD TAB ---
with tab1:
    st.subheader("Group Scoring")
    col1, col2 = st.columns(2)
    selected_group = col1.radio("Select Group", [1, 2], horizontal=True)
    selected_hole = col2.selectbox("Select Hole", HOLES)
    
    group_players = [p for p, data in PLAYERS.items() if data["group"] == selected_group]
    
    with st.form("score_form"):
        st.markdown(f"**Hole {selected_hole}** | Par {PARS[selected_hole-1]} | Stroke Index {SIS[selected_hole-1]}")
        scores = {}
        for p in group_players:
            current_score = db.at[p, selected_hole]
            val = int(current_score) if current_score > 0 else PARS[selected_hole-1]
            scores[p] = st.number_input(f"{p}'s Gross Score", min_value=1, max_value=15, value=val)
        
        if st.form_submit_button("SAVE SCORES"):
            for p, s in scores.items():
                db.at[p, selected_hole] = s
            st.success(f"Scores locked in for Hole {selected_hole}!")
            
    st.markdown("---")
    
    st.subheader("🚨 Penalty & Infractions")
    st.write("Call out fake scores here. It stays on the leaderboard forever.")
    bs_player = st.selectbox("Who is talking bullshit?", list(PLAYERS.keys()))
    if st.button(f"CALL BULLSHIT ON {bs_player.upper()}"):
        db.at[bs_player, 'bullshit'] += 1
        st.error(f"🚨 OFFICIAL RULING: BULLSHIT CALLED ON {bs_player.upper()}! 🚨")

# --- LEADERBOARD TAB ---
with tab2:
    if st.button("🔄 REFRESH LEADERBOARD"):
        st.rerun()
        
    st.subheader("Tournament Leaderboard")
    
    leaderboard = []
    points_dict = {}
    
    for player in PLAYERS.keys():
        total_points = 0
        holes_played = 0
        for hole in HOLES:
            gross = db.at[player, hole]
            if gross > 0:
                total_points += calc_stableford(player, hole, gross)
                holes_played += 1
                
        points_dict[player] = total_points
        bs_count = db.at[player, 'bullshit']
        
        thru_str = str(holes_played) if holes_played < 18 else "F"
        
        leaderboard.append({
            "PLAYER": player, 
            "PTS": total_points,
            "THRU": thru_str,
            "HCP": PLAYERS[player]["hcp"], 
            "BS 🚨": int(bs_count)
        })
        
    # Sort by Points
    df_leaderboard = pd.DataFrame(leaderboard).sort_values(by="PTS", ascending=False).reset_index(drop=True)
    
    # Adjust index to show Position (POS) starting at 1
    df_leaderboard.index += 1
    df_leaderboard.index.name = "POS"
    
    st.dataframe(df_leaderboard, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Team Matchup")
    g1_points = sum([pts for p, pts in points_dict.items() if PLAYERS[p]["group"] == 1])
    g2_points_raw = sum([pts for p, pts in points_dict.items() if PLAYERS[p]["group"] == 2])
    g2_points_weighted = round(g2_points_raw * (4/3), 1)
    
    colA, colB = st.columns(2)
    colA.metric("Group 1 (4-Ball)", f"{g1_points} pts")
    colB.metric("Group 2 (3-Ball)", f"{g2_points_weighted} pts", f"Unweighted: {g2_points_raw}", delta_color="off")
    st.caption("*Group 2 is weighted by 1.33x to account for the missing player.*")

# --- COURSE INFO TAB ---
with tab3:
    st.subheader("Camiral Tour Course")
    st.write("Yellow Tees - Par & Stroke Index")
    course_df = pd.DataFrame({"Hole": HOLES, "Par": PARS, "S.I.": SIS})
    st.dataframe(course_df.set_index("Hole").T, use_container_width=True)



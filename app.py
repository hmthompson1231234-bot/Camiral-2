import streamlit as st
import pandas as pd
import threading

st.set_page_config(page_title="Girona Invitational '26", layout="centered", initial_sidebar_state="collapsed")

# --- BULLETPROOF MASTERS CSS ---
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA !important; }
    .stMarkdown p, .stExpander p, label, .stRadio div { color: #2C3E50 !important; font-weight: 500; }
    h1, h2, h3 { color: #005A34 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    h1 { border-bottom: 3px solid #EAD15F !important; padding-bottom: 10px; }
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important; color: #111111 !important;
        border: 1px solid #005A34 !important; border-radius: 4px !important;
    }
    .stButton>button { 
        background-color: #005A34 !important; color: white !important; 
        border-radius: 6px !important; font-weight: bold !important; 
        border: 1px solid #005A34 !important; width: 100%;
    }
    .stButton>button:active { background-color: #EAD15F !important; color: #005A34 !important; }
    .stButton:last-of-type>button { background-color: #D32F2F !important; border-color: #D32F2F !important; }
    [data-testid="stDataFrame"] { background-color: #FFFFFF !important; border-radius: 8px; border: 1px solid #005A34; }
</style>
""", unsafe_allow_html=True)

# --- COURSE & PLAYER DATA ---
HOLES = list(range(1, 19))

COURSES = {
    "Round 1: Camiral Tour": {
        "key": "camiral",
        "pars": [4, 3, 4, 4, 5, 4, 5, 3, 4,  5, 3, 4, 4, 3, 5, 3, 4, 5],
        "sis":  [14, 18, 6, 2, 16, 12, 8, 4, 10,  9, 7, 11, 1, 13, 5, 17, 3, 15]
    },
    "Round 2: Peralada": {
        "key": "peralada",
        "pars": [4, 4, 4, 5, 4, 3, 5, 4, 3,  4, 4, 3, 5, 3, 4, 4, 5, 3],
        "sis":  [18, 2, 8, 16, 6, 4, 10, 14, 12, 11, 9, 13, 5, 17, 7, 1, 3, 15]
    }
}

# HANGOVER FAILSAFE ACTIVATED: Camiral Round 1 Scores Locked In
PLAYERS = {
    "Tommy":  {"hcp": 14, "group": 1, "r1_points": 30, "r1_gross": 0, "r1_bs": 2},
    "Hidde":  {"hcp": 15, "group": 1, "r1_points": 29, "r1_gross": 0, "r1_bs": 0},
    "Weeman": {"hcp": 20, "group": 1, "r1_points": 23, "r1_gross": 0, "r1_bs": 0},
    "Brad":   {"hcp": 22, "group": 1, "r1_points": 18, "r1_gross": 0, "r1_bs": 0},
    "Harry":  {"hcp": 14, "group": 2, "r1_points": 35, "r1_gross": 0, "r1_bs": 0},
    "Ted":    {"hcp": 22, "group": 2, "r1_points": 32, "r1_gross": 0, "r1_bs": 0},
    "James":  {"hcp": 16, "group": 2, "r1_points": 20, "r1_gross": 0, "r1_bs": 0}
}

@st.cache_resource
def get_score_db():
    cols = HOLES + ['bullshit']
    return {
        "lock": threading.Lock(), 
        "camiral": pd.DataFrame(index=list(PLAYERS.keys()), columns=cols).fillna(0),
        "peralada": pd.DataFrame(index=list(PLAYERS.keys()), columns=cols).fillna(0)
    }

db_wrapper = get_score_db()
db_lock = db_wrapper["lock"]

# --- APP HEADER ---
st.title("⛳️ GIRONA INVITATIONAL")

active_course_name = st.selectbox("📍 Select Current Round", list(COURSES.keys()))
active_course_data = COURSES[active_course_name]
db = db_wrapper[active_course_data["key"]]
PARS = active_course_data["pars"]
SIS = active_course_data["sis"]

def calc_stableford(player, hole, gross, course_pars, course_sis):
    if gross <= 0: return 0
    hcp = PLAYERS[player]["hcp"]
    par = course_pars[hole-1]
    si = course_sis[hole-1]
    extra_strokes = (hcp // 18) + (1 if (hcp % 18) >= si else 0)
    net_score = gross - extra_strokes
    return max(0, par - net_score + 2)

tab1, tab2, tab3 = st.tabs(["📝 Scorecard", "🏆 Leaderboards", "⛳️ Course"])

# --- SCORECARD TAB ---
with tab1:
    col1, col2 = st.columns(2)
    selected_group = col1.radio("Select Group", [1, 2], horizontal=True)
    selected_hole = col2.selectbox("Select Hole", HOLES)
    group_players = [p for p, data in PLAYERS.items() if data["group"] == selected_group]
    
    with st.form("score_form"):
        st.markdown(f"**Hole {selected_hole}** | Par {PARS[selected_hole-1]} | SI {SIS[selected_hole-1]}")
        scores = {}
        for p in group_players:
            current_score = db.at[p, selected_hole]
            val = int(current_score) if current_score > 0 else PARS[selected_hole-1]
            scores[p] = st.number_input(f"{p}'s Gross Score", min_value=1, max_value=20, value=val)
        
        if st.form_submit_button("SAVE SCORES"):
            with db_lock:
                for p, s in scores.items():
                    db.at[p, selected_hole] = s
            st.success(f"Scores locked for Hole {selected_hole} at {active_course_name}!")
            
    st.markdown("---")
    st.markdown("### 🚨 Penalty & Infractions")
    bs_player = st.selectbox("Who is talking bullshit?", list(PLAYERS.keys()))
    if st.button(f"CALL BULLSHIT ON {bs_player.upper()}"):
        with db_lock:
            db.at[bs_player, 'bullshit'] += 1
        st.error(f"🚨 OFFICIAL RULING: BULLSHIT CALLED ON {bs_player.upper()}! 🚨")

# --- LEADERBOARD TAB ---
with tab2:
    lb_view = st.radio("Select Leaderboard:", ["Current Round", "Overall Weekend"], horizontal=True)
    
    if st.button("🔄 REFRESH LEADERBOARDS"):
        st.rerun()
        
    leaderboard = []
    points_dict = {}
    
    with db_lock:
        for player in PLAYERS.keys():
            # Current Round Calcs
            round_pts = 0
            round_gross = 0
            holes_played = 0
            
            for hole in HOLES:
                gross = db.at[player, hole]
                if gross > 0:
                    round_pts += calc_stableford(player, hole, gross, PARS, SIS)
                    round_gross += gross
                    holes_played += 1
            
            # Overall Calcs (combining both databases + hangover failsafe)
            overall_pts = PLAYERS[player]["r1_points"]
            overall_gross = PLAYERS[player]["r1_gross"]
            overall_bs = PLAYERS[player]["r1_bs"]
            
            # Add what is currently in memory for both courses
            for c_name, c_data in COURSES.items():
                c_db = db_wrapper[c_data["key"]]
                for hole in HOLES:
                    g = c_db.at[player, hole]
                    if g > 0:
                        overall_pts += calc_stableford(player, hole, g, c_data["pars"], c_data["sis"])
                        overall_gross += g
            
            overall_bs += int(db_wrapper["camiral"].at[player, 'bullshit']) + int(db_wrapper["peralada"].at[player, 'bullshit'])

            if lb_view == "Current Round":
                points_dict[player] = round_pts
                leaderboard.append({
                    "PLAYER": player, "PTS": round_pts, "GROSS": int(round_gross),
                    "THRU": str(holes_played) if holes_played < 18 else "F",
                    "BS 🚨": int(db.at[player, 'bullshit'])
                })
            else:
                points_dict[player] = overall_pts
                leaderboard.append({
                    "PLAYER": player, "TOTAL PTS": overall_pts, "TOTAL GROSS": int(overall_gross),
                    "HCP": PLAYERS[player]["hcp"], "TOTAL BS 🚨": int(overall_bs)
                })
        
    sort_col = "PTS" if lb_view == "Current Round" else "TOTAL PTS"
    df_leaderboard = pd.DataFrame(leaderboard).sort_values(by=sort_col, ascending=False).reset_index(drop=True)
    df_leaderboard.index += 1
    st.dataframe(df_leaderboard, use_container_width=True)
    
    st.markdown("---")
    st.markdown(f"### Team Matchup ({lb_view})")
    g1_points = sum([pts for p, pts in points_dict.items() if PLAYERS[p]["group"] == 1])
    g2_points_raw = sum([pts for p, pts in points_dict.items() if PLAYERS[p]["group"] == 2])
    g2_points_weighted = round(g2_points_raw * (4/3), 1)
    
    colA, colB = st.columns(2)
    colA.metric("Group 1 (4-Ball)", f"{g1_points} pts")
    colB.metric("Group 2 (3-Ball)", f"{g2_points_weighted} pts", f"Raw: {g2_points_raw}", delta_color="off")

with tab3:
    st.markdown(f"**{active_course_name}**")
    course_df = pd.DataFrame({"Hole": HOLES, "Par": PARS, "S.I.": SIS})
    st.dataframe(course_df.set_index("Hole").T, use_container_width=True)

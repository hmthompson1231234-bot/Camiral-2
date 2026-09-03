import streamlit as st
import pandas as pd

# Set up the app UI
st.set_page_config(page_title="Girona Boys Trip '26", layout="centered")

HOLES = list(range(1, 19))
# Par and Stroke Index for Camiral Tour Course (Yellow Tees)
PARS = [4, 3, 4, 4, 5, 4, 5, 3, 4,  5, 3, 4, 4, 3, 5, 3, 4, 5]
SIS  = [14, 18, 6, 2, 16, 12, 8, 4, 10,  9, 7, 11, 1, 13, 5, 17, 3, 15]

PLAYERS = {
    "Tommy": 14,
    "Harry": 14,
    "Hidde": 15,
    "James": 16,
    "Weeman": 20,
    "Ted": 22,
    "Brad": 22
}

# This clever decorator shares the scoreboard state across everyone's phones!
@st.cache_resource
def get_score_db():
    return pd.DataFrame(index=list(PLAYERS.keys()), columns=HOLES).fillna(0)

db = get_score_db()

# Golf Stableford Math
def calc_stableford(player, hole, gross):
    if gross == 0:
        return 0
    hcp = PLAYERS[player]
    par = PARS[hole-1]
    si = SIS[hole-1]
    
    # Calculate extra strokes received for this specific hole
    extra_strokes = (hcp // 18) + (1 if (hcp % 18) >= si else 0)
    net_score = gross - extra_strokes
    return max(0, par - net_score + 2)

# Frontend Design
st.title("⛳️ Girona Boys Trip '26")
st.write("Camiral Tour Course (Yellow Tees) Live Scoring")

tab1, tab2, tab3 = st.tabs(["Record Score", "Leaderboard", "Course Info"])

with tab1:
    st.header("Log a Score")
    col1, col2 = st.columns(2)
    selected_player = col1.selectbox("Select Player", list(PLAYERS.keys()))
    selected_hole = col2.selectbox("Select Hole", HOLES)
    
    gross_score = st.number_input(f"Gross Score for {selected_player} (Hole {selected_hole})", min_value=1, max_value=15, value=4)
    
    if st.button("Save Score"):
        db.at[selected_player, selected_hole] = gross_score
        st.success(f"Saved: {selected_player} shot {gross_score} on Hole {selected_hole}")

with tab2:
    st.header("🏆 Live Stableford Leaderboard")
    if st.button("🔄 Refresh Leaderboard"):
        st.rerun() # Pulls the latest scores from the other group!
        
    leaderboard = []
    for player in PLAYERS.keys():
        total_points = 0
        for hole in HOLES:
            gross = db.at[player, hole]
            if gross > 0:
                total_points += calc_stableford(player, hole, gross)
        leaderboard.append({"Player": player, "HCP": PLAYERS[player], "Points": total_points})
        
    df_leaderboard = pd.DataFrame(leaderboard).sort_values(by="Points", ascending=False).reset_index(drop=True)
    df_leaderboard.index += 1
    st.dataframe(df_leaderboard, use_container_width=True)

with tab3:
    st.header("Course Data")
    st.write("Par & Stroke Index mapping for Camiral Tour.")
    course_df = pd.DataFrame({"Hole": HOLES, "Par": PARS, "Stroke Index": SIS})
    st.dataframe(course_df.set_index("Hole"), use_container_width=True)

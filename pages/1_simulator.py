import streamlit as st
import plotly.express as px
import fastf1 as f1
from utils import wear, lap_time
from utils.f1_config import F1_CONFIG

st.header('⚡ F1 Lap Simulator')

# SAME TRACK SELECTOR AS STRATEGY LAB ✅
track = st.selectbox("🏁 Track:", list(F1_CONFIG.keys()))
track_data = F1_CONFIG[track]

# CONTROLS
lap_no = st.slider('Lap Progress:', 0, track_data['laps'], 20)
tire_comp = st.selectbox(
    "Tire compound:", ["SOFT", "MEDIUM", 'HARD', 'INTERMEDIATE', 'WET'])
rain = st.slider("Rain", 0.0, 1.0, 0.0, 0.1)

# TOGGLE
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Lap Progress & Conditions")
with col2:
    use_real_data = st.toggle("Real F1 Data", value=False)

current_lap_time = None

if use_real_data:
    with st.spinner("Loading real F1 data..."):
        try:
            session = f1.get_session(2025, 'Monaco', 'R')
            session.load()
            verstappen = session.laps.pick_driver('VER')
            if lap_no < len(verstappen):
                current_lap_time = verstappen['LapTime'].iloc[lap_no].total_seconds(
                )
                st.info(f"Verstappen lap {lap_no}: {current_lap_time:.2f}s")
                fig = px.line(verstappen, x="LapNumber",
                              y="LapTime", title="MaxV Monaco 2025")
                st.plotly_chart(fig)
        except Exception as e:
            st.error(f"Using sim: {e}")
            current_lap_time = lap_time(
                wear(lap_no), tire_comp, rain, 110, track_data)
else:
    current_lap_time = lap_time(
        wear(lap_no), tire_comp, rain, 110, track_data)


st.header("📊 Lap Data")
col1, col2 = st.columns(2)
with col1:
    st.metric("Tire Wear:", f"{wear(lap_no)}%")
with col2:
    st.metric("LAP TIME:", f"{current_lap_time:.2f}s")

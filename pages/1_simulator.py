import streamlit as st
import plotly.express as px
import fastf1 as f1
from utils import wear, lap_time

st.header('⚡ F1 Lap Simulator - 14')

# CONTROLS
lap_no = st.slider('Lap Progress:', 0, 78, 20)
tire_comp = st.selectbox(
    "Tire compound:", ["SOFT", "MEDIUM", 'HARD', 'INTERMEDIATE', 'WET'], index=0)
rain = st.slider("Rain", 0.0, 1.0, 0.0, 0.1)

# TOGGLE
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Lap Progress nd COnditions")
with col2:
    use_real_data = st.toggle(
        "Real F1 Data", value=False, help="Loads verstappen Monaco 2025")

if use_real_data:
    with st.spinner("Loading real F1 data...."):
        try:
            # Downloads from F1 servers
            session = f1.get_session(2025, 'Monaco', 'R')
            session.load()  # Converts to DataFrames
            verstappen = session.laps.pick_driver(
                'VER')  # Table with 78 rows (laps)
            # max_laps = len(verstappen)-1
            # safe_lap = min(lap_no, max_laps)
            current_lap_time = verstappen['LapTime'].iloc[lap_no].total_seconds(
            )
            st.info(
                f"Verstappen did {len(verstappen)} laps (showing lap {lap_no})")
            fig = px.line(verstappen, x="LapNumber",
                          y="LapTime", title="Max Verstappen - Real Monaco 2025")
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Data loading issue: {e}")
            current_lap_time = lap_time(wear(lap_no), tire_comp, rain, 110)
else:
    current_lap_time = lap_time(wear(lap_no), tire_comp, rain, 110)

st.header("📊 Lap Data")
col1, col2 = st.columns(2)
with col1:
    st.metric("Tire Wear:", f"{wear(lap_no)}%")
with col2:
    st.metric("LAP TIME:", f"{current_lap_time:.2f} s")

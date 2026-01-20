import streamlit as st
from utils import wear, lap_time

st.header('⚡ Lap Simulator')
lap_no = st.slider('Lap Progress:', 0, 60, 0)
tire_comp = st.selectbox(
    "Tire compound:", ["SOFT", "MEDIUM", 'HARD', 'INTERMEDIATE', 'WET'], index=0)
rain = st.slider("Rain", 0.0, 1.0, 0.0, 0.1)

with open('canvas.html', 'r', encoding='utf-8') as c:
    code = c.read()
    code = code.replace('{lap_no}', str(lap_no))

# YOUR EXACT METRICS
st.metric("Tire Wear:", f"{wear(lap_no)}%")
st.metric("LAP TIME:", f"{lap_time(wear(lap_no), tire_comp, rain, 110)} s")

# YOUR PIT WARNING LOGIC - SAME!
if lap_no > 45 and lap_no != 60:
    st.warning("🛞 Tires CRITICAL! Consider Pitting Soon.")
    if st.button('🛑 PIT STOP'):
        st.session_state.tire_wear = 0
        st.success("🔧 Pitted!")

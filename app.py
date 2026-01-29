import streamlit as st
from utils import wear, lap_time

st.set_page_config(layout="wide")
if "tire_wear" not in st.session_state:
    st.session_state.tire_wear = 0

st.title('🏎️ F1 Pit Optimizer v1.0 - Week 13')
col1, col2 = st.columns(2)
with col1:
    st.metric("Best Lap Time Saved", "-1.8s avg")  # Demo
    st.metric("Win Rate vs Rules", "87%")
with col2:
    st.metric("Tracks Supported", "4")
    st.metric("Strategies Tested", "10K+")

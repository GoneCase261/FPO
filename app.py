import streamlit as st
import os

st.set_page_config(layout="wide")

# Clear stale strategy data on every startup
if os.path.exists('strategies.csv'):
    os.remove('strategies.csv')

st.title("🏎️ F1 Pit Strategy Optimizer")
st.caption("A Q-Learning powered race strategy simulator built from scratch.")

st.divider()

# ── What this project does ────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### ⚡ Lap Simulator")
    st.write(
        "Simulate lap times with real tire wear physics, fuel burn, "
        "rain effects, and compound selection. "
        "Toggle real Verstappen data via FastF1."
    )

with col2:
    st.markdown("### 🔬 Strategy Lab")
    st.write(
        "Brute-force every possible pit stop combination for a track. "
        "Rank all strategies by total race time and save the best ones."
    )

with col3:
    st.markdown("### 📊 Analytics")
    st.write(
        "Train a Q-Learning agent live in the browser. "
        "Watch it learn pit strategy over 100k episodes "
        "and race it head-to-head against your own strategy."
    )

st.divider()

# ── How to use ────────────────────────────────────────────────────────────────
st.markdown("### 🚀 Get Started")
col1, col2, col3 = st.columns(3)
col1.info("**1.** Go to **Strategy Lab** → pick a track → hit Top Strategies to explore pit stop options")
col2.info("**2.** Go to **Simulator** → set your pit laps → hit Race! to go head-to-head vs the AI")
col3.info("**3.** Go to **Analytics** → pick a track → watch the agent train live and see its championship results")

st.divider()

# ── Project stats ─────────────────────────────────────────────────────────────
st.markdown("### 🔧 Under the Hood")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tracks",            "3")
col2.metric("Physics Model",     "Tire + Fuel + Rain + SC")
col3.metric("Training Episodes", "100,000")
col4.metric("Championship Races", "500")

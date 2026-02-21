import streamlit as st
import pandas as pd
import os
import numpy as np
from utils import race_simulation, generate_strategies
from utils.f1_config import F1_CONFIG, TIRE_MULTIPLIERS

st.header('🔬 Strategy Lab')

num_stops = st.slider("Number of stops", 1, 4, 2)
tire_comp = st.selectbox(
    "Tire compound:", ["SOFT", "MEDIUM", 'HARD', 'INTERMEDIATE', 'WET'])
rain = st.slider("Rain intensity", 0.0, 1.0, 0.0, 0.1)
track = st.selectbox("🏁 Track:", list(F1_CONFIG.keys()))


# Track info
track_data = F1_CONFIG[track]
st.info(f"🏁 {track}: {track_data['laps']} laps")

# Session state
if 'top_strategies' not in st.session_state:
    st.session_state.top_strategies = []

# BRUTE FORCE ONLY - Generate + Rank ALL strategies
if st.button("🚀 TOP STRATEGIES", type="primary"):
    with st.spinner(f"Computing {num_stops}-stop strategies..."):
        strategies = generate_strategies(num_stops)
        st.info(f"Generated {len(strategies)} strategies")

        results = []
        for pits in strategies:
            time = race_simulation(pits, track, tire_comp, rain)[0]
            results.append({"pits": pits, "time": time})

        # Sort + take top 5
        results.sort(key=lambda x: x["time"])
        st.session_state.top_strategies = results[:5]

        # Display ranked results
        st.write("**🏅 TOP 5 STRATEGIES:**")
        best_time = results[0]["time"]
        for i, r in enumerate(results[:5], 1):
            gap = r["time"] - best_time
            st.write(
                f"{i}. **{r['pits']}** → **{r['time']:.1f}s** {f'(+{gap:.1f}s)' if i > 1 else '(BEST)'}")

# Display current best
if st.session_state.top_strategies:
    best = st.session_state.top_strategies[0]
    st.metric("⏱️ BEST RACE TIME", f"{best['time']:.1f}s")
    st.code(f"Best pits: {best['pits']}")

# SAVE RESULTS
if st.button("💾 SAVE TOP 5") and st.session_state.top_strategies:
    data = []
    for r in st.session_state.top_strategies:
        data.append({
            'track': track,
            'stops': num_stops,
            'pits': str(r['pits']),
            'tire': tire_comp,
            'rain': rain,
            'time': r['time']
        })

    df = pd.DataFrame(data)
    if os.path.exists('strategies.csv'):
        old = pd.read_csv('strategies.csv')
        df = pd.concat([old, df]).drop_duplicates(
            subset=['pits']).reset_index(drop=True)
    df.to_csv('strategies.csv', index=False)
    st.success(f"✅ Saved {len(df)} unique strategies")
    st.dataframe(df.tail(5))

# File status
st.write("📁 Files:", [f for f in os.listdir('.') if f.endswith('.csv')])

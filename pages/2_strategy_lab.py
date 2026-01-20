import streamlit as st
import pandas as pd
from utils import race_simulation, generate_strategies

st.header('🔬 Strategy Lab')
num_stops = st.slider("Number of stops", 1, 4, 2)

# ADD THESE - were missing!
tire_comp = st.selectbox(
    "Tire compound:", ["SOFT", "MEDIUM", 'HARD', 'INTERMEDIATE', 'WET'], index=0)
rain = st.slider("Rain", 0.0, 1.0, 0.0, 0.1)

pit_input = st.text_input("Pit laps (comma separated):")
pit_laps = [int(x.strip()) for x in pit_input.split(",") if x.strip()]

if len(pit_laps) != num_stops:
    st.error(f"Expected {num_stops} stops, got {len(pit_laps)}")

# FIXED: Single button + correct variables
if st.button("SIMULATE RACE") and pit_laps:
    total_time, lap_numbers, cumulative_times, fuel_left = race_simulation(
        pit_laps, tire_comp, rain)  # ✅ Fixed variables

    df = pd.DataFrame({
        'Lap': lap_numbers,
        'Fuel Left': fuel_left,
        'Cumulative Time': cumulative_times
    })
    st.write(df)
    st.line_chart(df.set_index('Lap'))

# FIXED: Use correct variables
if st.button("🏆 FIND TOP 5 STRATEGIES") and tire_comp and rain is not None:
    strategies = generate_strategies(num_stops)
    st.info(f"Generated {len(strategies)} {num_stops}-stop strategies")

    results = []
    for strategy in strategies:
        total_time, _, _, _ = race_simulation(strategy, tire_comp, rain)
        results.append({"strategy": strategy, "time": total_time})

    results.sort(key=lambda x: x["time"])
    top_5 = results[:5]

    for i, result in enumerate(top_5, 1):
        gap = result["time"] - top_5[0]['time']
        st.write(
            f"{i}. {result['strategy']} → {result['time']:.1f}s {'(+%.1f s)' % gap if i > 1 else '(BEST)'}")

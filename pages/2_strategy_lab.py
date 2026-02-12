import streamlit as st
import pandas as pd
import os
from utils import race_simulation, generate_strategies
from utils.f1_config import F1_CONFIG, TIRE_MULTIPLIERS
st.header('🔬 Strategy Lab')
num_stops = st.slider("Number of stops", 1, 4, 2)

if 'top_5_strategies' not in st.session_state:
    st.session_state.top_5_strategies = []
st.write("📁 Working folder:", os.getcwd())
st.write("📄 CSV files:", [f for f in os.listdir('.') if f.endswith('.csv')])

tire_comp = st.selectbox(
    "Tire compound:", ["SOFT", "MEDIUM", 'HARD', 'INTERMEDIATE', 'WET'], index=0)
rain = st.slider("Rain", 0.0, 1.0, 0.0, 0.1)

track = st.selectbox("🏁 Track:", list(F1_CONFIG.keys()), index=0)

track_data = F1_CONFIG[track]
st.info(f"""
🏁 {track} Race Config:
• Laps: {track_data['laps']}
• Base lap: {track_data['base_lap']:.1f}s  
• Tire wear: {track_data['tdr']:.1f}x
• Fuel burn: {track_data['fbph']}kg/h
""")

pit_input = st.text_input("Pit laps (comma separated):")
pit_laps = [int(x.strip()) for x in pit_input.split(",") if x.strip()]

if len(pit_laps) != num_stops:
    st.error(f"Expected {num_stops} stops, got {len(pit_laps)}")

if st.button("SIMULATE RACE") and pit_laps:
    total_time, lap_numbers, cumulative_times, fuel_left = race_simulation(
        pit_laps, track, tire_comp, rain)

    df = pd.DataFrame({
        'Lap': lap_numbers,
        'Fuel Left': fuel_left,
        'Cumulative Time': cumulative_times
    })
    st.write(df)
    st.line_chart(df.set_index('Lap'))

if st.button("🏆 FIND TOP 5 STRATEGIES") and tire_comp and rain is not None:
    strategies = generate_strategies(num_stops)
    st.info(f"Generated {len(strategies)} {num_stops}-stop strategies")

    results = []
    for strategy in strategies:
        total_time, _, _, _ = race_simulation(
            strategy, track, tire_comp, rain)
        results.append({"strategy": strategy, "time": total_time})

    results.sort(key=lambda x: x["time"])
    top_5 = results[:5]

    # SHOW RESULTS
    for i, result in enumerate(top_5, 1):
        gap = result["time"] - top_5[0]['time']
        st.write(
            f"{i}. {result['strategy']} → {result['time']:.1f}s {'(+%.1f s)' % gap if i > 1 else '(BEST)'}")

    st.session_state.top_5_strategies = top_5

# SAVE BUTTON
if st.button("💾 SAVE TOP 5"):
    if st.session_state.top_5_strategies:
        for result in st.session_state.top_5_strategies:
            strategy = {
                'track': track,
                'pit_laps': str(result['strategy']),
                'tire_comp': tire_comp,
                'rain': rain,
                'total_time': result['time']
            }
            df_new = pd.DataFrame([strategy])
            if os.path.exists('strategies.csv'):
                try:
                    df_old = pd.read_csv('strategies.csv')
                    df_all = pd.concat([df_old, df_new], ignore_index=True)
                except pd.errors.EmptyDataError:
                    df_all = df_new
            else:
                df_all = df_new
            df_all.to_csv('strategies.csv', index=False)

        st.success("✅ Saved TOP 5!")
        # shows last 5 rows by default
        st.dataframe(pd.read_csv('strategies.csv').tail())
        st.session_state.top_5_strategies = []
    else:
        st.warning("🤷 Run FIND TOP 5 first!")

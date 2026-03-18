import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import fastf1 as f1
from utils import wear, lap_time, race_simulation, safety_car_periods
from utils.f1_config import F1_CONFIG
from qlearning import F1QAgent, run_race_with_ai

st.header('⚡ F1 Lap Simulator')

track = st.selectbox("🏁 Track:", list(F1_CONFIG.keys()))
track_data = F1_CONFIG[track]

lap_no = st.slider('Lap Progress:', 0, track_data['laps'], 20)
compounds = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
tire_comp = st.selectbox("Tire compound:", compounds,
                         index=compounds.index(track_data['default_tire']))
rain = st.slider("Rain intensity", 0.0, 1.0, 0.0, 0.1)

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
                              y="LapTime", title="Verstappen — Monaco 2025")
                st.plotly_chart(fig)
        except Exception as e:
            st.error(f"Using simulation: {e}")
            current_lap_time = lap_time(
                wear(lap_no), tire_comp, rain, track_data['fuel_tank'], track_data)
else:
    current_lap_time = lap_time(
        wear(lap_no), tire_comp, rain, track_data['fuel_tank'], track_data)

st.header("📊 Lap Data")
col1, col2 = st.columns(2)
with col1:
    st.metric("Tire Wear", f"{wear(lap_no):.1f}%")
with col2:
    st.metric("Lap Time", f"{current_lap_time:.2f}s")

st.divider()

# ── Human vs AI Head-to-Head ─────────────────────────────────────────────────
st.header("🆚 Human vs AI")
st.caption("You choose your pit laps. The AI picks its own. Same track, same safety car — best strategy wins.")

total_laps = track_data['laps']

# Generate SC once per track
sc_key = f"sc_{track}"
agent_key = f"ai_agent_{track}"

if sc_key not in st.session_state:
    st.session_state[sc_key] = safety_car_periods(total_laps)

# Train agent eagerly when track is selected — so Race! is instant
if agent_key not in st.session_state:
    episodes_map = {
        "Spa_LongWet":      100_000,
        "Silverstone_Fast": 125_000,
        "Monaco_Street":    175_000,
    }
    EPISODES = episodes_map.get(track, 100_000)
    with st.spinner(f"🧠 Training AI on {track}..."):
        agent = F1QAgent()
        fixed_sc = safety_car_periods(total_laps)
        for episode in range(EPISODES):
            if episode % 10 == 0:
                fixed_sc = safety_car_periods(total_laps)
            run_race_with_ai(agent, track, fixed_sc=fixed_sc)
        st.session_state[agent_key] = agent

col1, col2 = st.columns(2)
with col1:
    human_pit1 = st.number_input(
        "Your pit stop 1 (lap)", min_value=1, max_value=total_laps - 1,
        value=total_laps // 3, key="pit1"
    )
with col2:
    human_pit2 = st.number_input(
        "Your pit stop 2 (lap)", min_value=1, max_value=total_laps - 1,
        value=total_laps * 2 // 3, key="pit2"
    )

if st.button("🏁 Race!", type="primary"):
    # Fresh SC for each new race click
    st.session_state[sc_key] = safety_car_periods(total_laps)
    shared_sc = st.session_state[sc_key]
    human_pits = sorted(set([int(human_pit1), int(human_pit2)]))

    # Snapshot tire_comp and rain at race time — not affected by later slider moves
    snap_tire = tire_comp
    snap_rain = rain

    # ── Human race ───────────────────────────────────────────────────────────
    human_time, human_laps, human_cumulative, _ = race_simulation(
        human_pits, track, tire_comp=snap_tire, rain=snap_rain, fixed_sc=shared_sc
    )

    # ── AI race ──────────────────────────────────────────────────────────────
    agent = st.session_state[agent_key]
    ai_strategy, _, _ = run_race_with_ai(
        agent, track, evaluation_mode=True, fixed_sc=shared_sc
    )
    ai_pits = [lap for lap, comp in ai_strategy]

    ai_time, ai_laps, ai_cumulative, _ = race_simulation(
        ai_pits, track, tire_comp=snap_tire, rain=snap_rain, fixed_sc=shared_sc
    )

    # Store everything — display reads only from here
    st.session_state["race_result"] = {
        "human_time":       human_time,
        "human_laps":       human_laps,
        "human_cumulative": human_cumulative,
        "human_pits":       human_pits,
        "ai_time":          ai_time,
        "ai_laps":          ai_laps,
        "ai_cumulative":    ai_cumulative,
        "ai_pits":          ai_pits,
        "tire":             snap_tire,
        "rain":             snap_rain,
    }

# ── Display results (reads from cache, survives any rerun) ───────────────────
if "race_result" in st.session_state:
    res = st.session_state["race_result"]
    human_time = res["human_time"]
    human_laps = res["human_laps"]
    human_cumulative = res["human_cumulative"]
    human_pits = res["human_pits"]
    ai_time = res["ai_time"]
    ai_laps = res["ai_laps"]
    ai_cumulative = res["ai_cumulative"]
    ai_pits = res["ai_pits"]
    gap = human_time - ai_time

    st.subheader("🏆 Result")
    col1, col2, col3 = st.columns(3)
    col1.metric("👤 You",  f"{human_time:.1f}s", f"Pits: {human_pits}")
    col2.metric("🤖 AI",   f"{ai_time:.1f}s",    f"Pits: {ai_pits}")
    col3.metric("Gap",     f"{abs(gap):.1f}s",
                "AI wins 🤖" if gap > 0 else "You win! 🏆")

    if gap > 0:
        st.error(f"🤖 AI wins by **{gap:.1f}s**")
    elif gap < 0:
        st.success(f"🏆 You beat the AI by **{abs(gap):.1f}s**!")
    else:
        st.info("Dead heat! 🤝")

    st.markdown("**📈 Race Progress — Cumulative Time**")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=human_laps, y=human_cumulative,
        mode="lines", name="👤 You",
        line=dict(color="#4a90e2", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=ai_laps, y=ai_cumulative,
        mode="lines", name="🤖 AI",
        line=dict(color="#e8002d", width=2),
    ))
    for p in human_pits:
        fig.add_vline(x=p, line_dash="dot", line_color="#4a90e2", opacity=0.4)
    for p in ai_pits:
        fig.add_vline(x=p, line_dash="dot", line_color="#e8002d", opacity=0.4)

    fig.update_layout(
        xaxis_title="Lap",
        yaxis_title="Cumulative Time (s)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom",
                    y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Dotted lines = pit stops  |  Blue = you  |  Red = AI")

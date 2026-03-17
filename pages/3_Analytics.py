from qlearning import (
    F1QAgent,
    run_race_with_ai,
    race_standings,
)
from utils import race_simulation, safety_car_periods
from utils.f1_config import F1_CONFIG
from collections import Counter
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


st.header("📊 Analytics")

tab1, tab2 = st.tabs(["🏁 Strategy Leaderboard", "🤖 AI Performance"])

# ── TAB 1: Strategy Leaderboard ─────────────────────────────────────────────
with tab1:
    st.subheader("Track-Specific Strategy Leaderboard")

    if os.path.exists('strategies.csv'):
        df = pd.read_csv('strategies.csv')

        # Clean bad data
        df = df.dropna(subset=['total_time'])
        df = df[np.isfinite(df['total_time'])]

        st.info(f"📊 Loaded {len(df)} strategies")

        if len(df) > 0:
            # Best strategy per track
            track_leaderboard = {}
            for track in df['track'].unique():
                track_df = df[df['track'] == track]
                best_idx = track_df['total_time'].idxmin()
                track_leaderboard[track] = track_df.loc[best_idx]

            if track_leaderboard:
                leaderboard_df = pd.DataFrame(track_leaderboard).T
                st.dataframe(leaderboard_df.sort_values('total_time').head(10))

                col1, col2, col3 = st.columns(3)
                fastest_track = df.groupby(
                    'track')['total_time'].min().idxmin()
                col1.metric("🏁 Fastest Track", fastest_track)
                col2.metric("📊 Total Tracks", df['track'].nunique())
                col3.metric("🎯 Strategies Saved", len(df))
            else:
                st.warning("No valid track data found.")
        else:
            st.warning("No valid strategies found after cleaning.")
    else:
        st.info("💾 Save some strategies in the Strategy Lab first!")


# ── TAB 2: AI Performance ────────────────────────────────────────────────────
with tab2:
    st.subheader("Q-Learning Agent Performance")

    import random
    import plotly.graph_objects as go

    track = st.selectbox("🏁 Track:", list(F1_CONFIG.keys()), key="ai_track")

    # Per-track cache keys
    agent_key = f"ai_agent_{track}"
    results_key = f"ai_results_{track}"
    times_key = f"ai_times_{track}"

    # ── Retrain button ────────────────────────────────────────────────────────
    if st.button("🔄 Retrain Agent"):
        for key in [agent_key, results_key, times_key]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # ── Train if not cached for this track ───────────────────────────────────
    if agent_key not in st.session_state:
        EPISODES = 100_000
        st.info(f"🧠 Training on {track} — runs once per track per session...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        agent = F1QAgent()
        best_time = float('inf')
        best_times = []
        actual_times = []
        fixed_sc = safety_car_periods(F1_CONFIG[track]['laps'])

        for episode in range(EPISODES):
            if episode % 10 == 0:
                fixed_sc = safety_car_periods(F1_CONFIG[track]['laps'])

            strategy, race_time, _ = run_race_with_ai(
                agent, track, fixed_sc=fixed_sc)

            if race_time < best_time:
                best_time = race_time

            if episode % 100 == 0:
                best_times.append(best_time)
                actual_times.append(race_time)

            if episode % 1000 == 0:
                pct = int(episode / EPISODES * 100)
                progress_bar.progress(pct)
                status_text.text(
                    f"Episode {episode:,} / {EPISODES:,} | "
                    f"Best: {best_time:.0f}s | Latest: {race_time:.0f}s"
                )

        progress_bar.progress(100)
        status_text.text(f"✅ Training complete for {track}!")

        st.session_state[agent_key] = agent
        st.session_state[times_key] = {
            "best": best_times, "actual": actual_times}

    # ── Run 500-race championship if not cached for this track ────────────────
    if results_key not in st.session_state:
        agent = st.session_state[agent_key]

        with st.spinner(f"🏎️ Running 500-race championship on {track}..."):
            ai_positions = []
            ai_strategies = []
            eval_times = []
            eval_strategies = []

            for race in range(500):
                race_sc = safety_car_periods(F1_CONFIG[track]['laps'])
                strategy, time, _ = run_race_with_ai(
                    agent, track, evaluation_mode=True, fixed_sc=race_sc)
                sim_pit_laps = [lap for lap, comp in strategy]
                _, positions, _ = race_standings(
                    sim_pit_laps, track=track, fixed_sc=race_sc, ai_time=time)
                ai_positions.append(positions["AI"])
                ai_strategies.append(
                    [f"L{lap}{comp[0]}" for lap, comp in strategy])

            for _ in range(30):
                eval_sc = safety_car_periods(F1_CONFIG[track]['laps'])
                strategy, time, _ = run_race_with_ai(
                    agent, track, evaluation_mode=True, fixed_sc=eval_sc)
                eval_times.append(time)
                eval_strategies.append(
                    [f"L{lap}{comp[0]}" for lap, comp in strategy])

            final_time = np.mean(eval_times)
            final_std = np.std(eval_times)

            strategy_counts = Counter(tuple(s) for s in eval_strategies)
            best_strategy = list(strategy_counts.most_common(1)[0][0])

            # Human baseline — use track's default pit laps
            track_laps = F1_CONFIG[track]['laps']
            human_pit1 = track_laps // 3
            human_pit2 = track_laps * 2 // 3
            human_time, _, _, _ = race_simulation(
                [human_pit1, human_pit2], track, fixed_sc=eval_sc, verbose=False
            )
            gain = human_time - final_time

            st.session_state[results_key] = {
                "win_rate":      sum(1 for p in ai_positions if p == 1) / 500 * 100,
                "avg_position":  float(np.mean(ai_positions)),
                "ai_avg_time":   float(final_time),
                "ai_std":        float(final_std),
                "human_time":    float(human_time),
                "human_pits":    [human_pit1, human_pit2],
                "gain_vs_human": float(gain),
                "best_strategy": best_strategy,
                "all_positions": ai_positions,
            }

    # ── Display results ───────────────────────────────────────────────────────
    if results_key not in st.session_state or times_key not in st.session_state:
        st.stop()

    r = st.session_state[results_key]
    time_data = st.session_state[times_key]
    best_times = time_data["best"]
    actual_times = time_data["actual"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏆 Win Rate",      f"{r['win_rate']:.1f}%")
    col2.metric("🏅 Avg Finish",    f"P{r['avg_position']:.1f}")
    col3.metric("⏱️ AI Avg Time",   f"{r['ai_avg_time']:.0f}s")
    col4.metric("📈 Gain vs Human", f"+{r['gain_vs_human']:.0f}s")

    st.divider()

    st.markdown("**🎯 Most Consistent Strategy (30-race eval)**")
    st.code(f"Pit laps: {r['best_strategy']}")

    col1, col2 = st.columns(2)
    col1.metric("AI Time",    f"{r['ai_avg_time']:.0f}s ± {r['ai_std']:.0f}s")
    col2.metric("Human Time", f"{r['human_time']:.0f}s  {r['human_pits']}")

    st.divider()

    # Training curve
    st.markdown("**📉 Training Curve — Convergence over Episodes**")
    episodes_x = list(range(0, len(best_times) * 100, 100))
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=episodes_x, y=actual_times,
        mode="lines", name="Race Time",
        line=dict(color="#ff6b6b", width=1),
        opacity=0.5,
    ))
    fig1.add_trace(go.Scatter(
        x=episodes_x, y=best_times,
        mode="lines", name="Best Time",
        line=dict(color="#e8002d", width=2.5),
    ))
    fig1.update_layout(
        xaxis_title="Episode",
        yaxis_title="Race Time (s)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom",
                    y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Finish position distribution
    st.markdown("**🏁 500-Race Finish Position Distribution**")
    positions = r['all_positions']
    pos_counts = {str(i): positions.count(i) for i in range(1, 7)}
    fig2 = px.bar(
        x=list(pos_counts.keys()),
        y=list(pos_counts.values()),
        labels={"x": "Finish Position", "y": "Count"},
        color=list(pos_counts.values()),
        color_continuous_scale=["#e8002d", "#ff6b6b", "#ffd700"],
    )
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

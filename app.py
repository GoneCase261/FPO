import streamlit as st
import plotly.graph_objects as go
import numpy as np
import os
from collections import Counter
from utils.f1_config import F1_CONFIG
from utils import race_simulation, safety_car_periods
from qlearning import F1QAgent, run_race_with_ai, race_standings

st.set_page_config(layout="wide", page_title="F1 Pit Strategy AI")

if os.path.exists('strategies.csv'):
    os.remove('strategies.csv')

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;700;900&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Mono', monospace; }

.hero-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 4.2rem; font-weight: 900;
    line-height: 1.05; color: #B4D3D9; margin: 0;
}
.hero-accent { color: #e8002d; }
.hero-sub {
    font-size: 0.7rem; color: #6984A9;
    letter-spacing: 3px; text-transform: uppercase; margin-top: 0.6rem;
}
.hero-value {
    font-size: 0.95rem; color: #8BAFC4; margin-top: 1rem; line-height: 1.6;
}
.scale-stat {
    font-size: 0.82rem; color: #3DC2EC; margin-top: 0.5rem; font-style: italic;
}
.plain-english {
    background: #234C6A; border-left: 6px solid #132440;
    padding: 1.2rem 1.5rem; border-radius: 4px;
    font-size: 0.88rem; color: #bbb; line-height: 2.0; margin: 1.2rem 0;
}
.watch-banner {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.2rem; font-weight: 900; color: #21E6C1;
    text-align: center; padding: 1rem;
    background: #0a1f2a; border: 1px solid #1a4a6a;
    border-radius: 8px; margin: 1rem 0; letter-spacing: 2px;
}
.info-card {
    background: #0f1a2a; border: 1px solid #1e3a5a;
    border-radius: 8px; padding: 1rem 1.4rem; margin: 1rem 0;
    font-size: 0.85rem; color: #7A9AB2; line-height: 2.0;
}
.info-card-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1rem; font-weight: 700;
    color: #3DC2EC; letter-spacing: 1px; margin-bottom: 0.4rem;
}
.stat-block { text-align: center; padding: 1rem 0; }
.stat-number {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 3.5rem; font-weight: 900; color: #21E6C1; line-height: 1;
}
.stat-label {
    font-size: 0.75rem; color: #3DC2EC;
    text-transform: uppercase; letter-spacing: 2px; margin-top: 0.3rem;
}
.stat-sub { font-size: 0.72rem; color: #777; margin-top: 0.2rem; }
.killer-line {
    text-align: center; font-size: 0.8rem; color: #6984A9;
    font-style: italic; margin: 1rem 0; line-height: 1.6;
}
.bridge-line {
    text-align: center; font-size: 0.8rem; color: #5A7A8A;
    font-style: italic; margin: 0.5rem 0; line-height: 1.6;
}
.win-banner {
    text-align: center; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;
    font-family: 'Barlow Condensed', sans-serif; font-size: 2rem; font-weight: 900;
}
.win  { background: #0a1f0a; color: #4caf50; border: 1px solid #2a5a2a; }
.lose { background: #1f0a0a; color: #e8002d; border: 1px solid #5a2a2a; }
.draw { background: #1a1a0a; color: #ffd700; border: 1px solid #5a5a2a; }
.insight {
    background: #0a0a0a; border: 1px solid #1a1a1a;
    border-radius: 6px; padding: 1rem 1.4rem;
    font-size: 0.8rem; color: #999; margin-top: 0.8rem; line-height: 1.7;
}
.ownership-block {
    background: #0f0f0f; border: 1px solid #2a2a2a;
    border-radius: 8px; padding: 1.2rem 1.5rem; margin: 1rem 0;
    font-size: 0.85rem; color: #888; line-height: 2.2;
}
.ownership-title {
    font-family: 'Barlow Condensed', sans-serif; font-size: 1rem; font-weight: 700;
    color: #B4D3D9; letter-spacing: 1px; margin-bottom: 0.5rem;
}
.takeaway-block {
    background: #0f0f1a; border: 1px solid #1a1a3a;
    border-radius: 8px; padding: 1.2rem 1.5rem; margin: 1rem 0;
    font-size: 0.85rem; color: #8888BB; line-height: 2.2;
}
.takeaway-title {
    font-family: 'Barlow Condensed', sans-serif; font-size: 1rem; font-weight: 700;
    color: #B4D3D9; letter-spacing: 1px; margin-bottom: 0.5rem;
}
.tech-stack {
    text-align: center; font-size: 0.65rem; color: #4C5F7A;
    letter-spacing: 2px; text-transform: uppercase; margin-top: 3rem;
    padding-top: 1.5rem; border-top: 1px solid #111;
}
.divider { border: none; border-top: 1px solid #1a1a1a; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-title">
    Can an AI learn to<br>
    <span class="hero-accent">outrace a human</span><br>
    without being told how?
</div>
<div class="hero-sub">Reinforcement Learning · Race Strategy · Built from scratch</div>
<div class="hero-value">
    An AI that learned race strategy through experience —
    trained across 100,000 simulated races without hard-coded rules.
</div>
<div class="scale-stat">
    💡 100,000 simulated races ≈ 8+ years of racing experience — learned in minutes.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="plain-english">
    <b style="color:#fff">Problem:</b> When should an agent act when future conditions are uncertain?<br>
    <b style="color:#fff">Approach:</b> Train an AI through 100,000+ simulated races — learning from wins, losses, and random disruptions.<br>
    <b style="color:#fff">Result:</b> An agent that beats static human strategies by adapting to conditions no rule can predict.
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── TRACK SELECTOR ────────────────────────────────────────────────────────────
st.markdown("### 🏁 Select a Track")

col1, col2 = st.columns([2, 1])
with col1:
    track = st.selectbox("", list(F1_CONFIG.keys()),
                         label_visibility="collapsed")
with col2:
    # Disable button if already training or already trained
    already_trained = f"ai_agent_{track}" in st.session_state
    train_clicked = st.button(
        "✅ Trained!" if already_trained else "🧠 Train AI",
        type="primary",
        use_container_width=True,
        disabled=already_trained or st.session_state.get(
            "training_in_progress", False),
    )

track_data = F1_CONFIG[track]
total_laps = track_data['laps']

agent_key = f"ai_agent_{track}"
results_key = f"ai_results_{track}"
times_key = f"ai_times_{track}"

episodes_map = {
    "Spa_LongWet":      100_000,
    "Silverstone_Fast": 100_000,
}
EPISODES = episodes_map.get(track, 100_000)

if train_clicked:
    st.session_state["training_in_progress"] = True
    for key in [agent_key, results_key, times_key]:
        if key in st.session_state:
            del st.session_state[key]

# ── TRAINING — only if button was clicked ─────────────────────────────────────
if train_clicked or (st.session_state.get("training_in_progress", False) and agent_key not in st.session_state):

    st.markdown('<div class="watch-banner">👀 WATCH THE AI LEARN!</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card">
        <div class="info-card-title">🧭 What's happening</div>
        🎲&nbsp; Simulating thousands of races with random safety cars &amp; tire degradation<br>
        🔁&nbsp; AI learns when to swap tires through trial and error — no rules programmed<br>
        📉&nbsp; Watch the red line drop — every dip = a better strategy discovered
    </div>
    """, unsafe_allow_html=True)

    progress_bar = st.progress(0)
    status = st.empty()
    chart_slot = st.empty()

    agent = F1QAgent()
    best_time = float('inf')
    best_times = []
    actual_times = []
    fixed_sc = safety_car_periods(total_laps)

    for episode in range(EPISODES):
        if episode % 10 == 0:
            fixed_sc = safety_car_periods(total_laps)
        _, race_time, _ = run_race_with_ai(agent, track, fixed_sc=fixed_sc)
        if race_time < best_time:
            best_time = race_time
        if episode % 100 == 0:
            best_times.append(best_time)
            actual_times.append(race_time)
        if episode % 1000 == 0:
            pct = int(episode / EPISODES * 100)
            progress_bar.progress(pct)
            car_pos = int(pct / 100 * 40)
            track_ui = "─" * car_pos + "🏎️" + "─" * (40 - car_pos)
            status.markdown(
                f"`{track_ui}`  **Episode {episode:,} / {EPISODES:,}** — Best: {best_time:.0f}s")
            if len(best_times) > 5:
                x = list(range(0, len(best_times) * 100, 100))
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x, y=actual_times, mode="lines",
                                         name="Race Time", line=dict(color="#ff6b6b", width=1), opacity=0.4))
                fig.add_trace(go.Scatter(x=x, y=best_times, mode="lines",
                                         name="Best Time", line=dict(color="#e8002d", width=2.5)))
                fig.update_layout(
                    height=220, margin=dict(l=0, r=0, t=10, b=0),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    xaxis_title="Episode", yaxis_title="Race Time (s)",
                    legend=dict(orientation="h", y=1.1),
                    font=dict(color="#555", size=10),
                )
                chart_slot.plotly_chart(fig, use_container_width=True)

    progress_bar.progress(100)
    status.markdown(
        f"✅ **Done!** Ran **{EPISODES:,} simulated races** — no rules were programmed.")
    st.session_state[agent_key] = agent
    st.session_state[times_key] = {"best": best_times, "actual": actual_times}
    st.session_state["training_in_progress"] = False
    st.rerun()

# ── 500 RACE CHAMPIONSHIP ─────────────────────────────────────────────────────
if agent_key in st.session_state and results_key not in st.session_state:
    agent = st.session_state[agent_key]
    with st.spinner("🏎️ Running 500-race championship..."):
        ai_positions = []
        eval_times = []
        eval_strategies = []

        for race in range(500):
            race_sc = safety_car_periods(total_laps)
            strategy, time, _ = run_race_with_ai(
                agent, track, evaluation_mode=True, fixed_sc=race_sc)
            sim_pit_laps = [lap for lap, _ in strategy]
            _, positions, _ = race_standings(
                sim_pit_laps, track=track, fixed_sc=race_sc, ai_time=time, evaluation_mode=True)
            ai_positions.append(positions["AI"])

        for _ in range(30):
            eval_sc = safety_car_periods(total_laps)
            strategy, time, _ = run_race_with_ai(
                agent, track, evaluation_mode=True, fixed_sc=eval_sc)
            eval_times.append(time)
            eval_strategies.append(
                [f"L{lap}{comp[0]}" for lap, comp in strategy])

        final_time = np.mean(eval_times)
        final_std = np.std(eval_times)
        strategy_counts = Counter(tuple(s) for s in eval_strategies)
        best_strategy = list(strategy_counts.most_common(1)[0][0])

        t = total_laps
        human_pits = [t // 3, t * 2 // 3]
        human_time, _, _, _ = race_simulation(
            human_pits, track, fixed_sc=eval_sc, verbose=False)
        gain = human_time - final_time

        st.session_state[results_key] = {
            "win_rate":      sum(1 for p in ai_positions if p == 1) / 500 * 100,
            "avg_position":  float(np.mean(ai_positions)),
            "ai_avg_time":   float(final_time),
            "ai_std":        float(final_std),
            "human_time":    float(human_time),
            "human_pits":    human_pits,
            "gain_vs_human": float(gain),
            "best_strategy": best_strategy,
            "all_positions": ai_positions,
        }

# ── RESULTS ───────────────────────────────────────────────────────────────────
if results_key in st.session_state and times_key in st.session_state:
    r = st.session_state[results_key]
    time_data = st.session_state[times_key]
    best_times = time_data["best"]
    actual_times = time_data["actual"]

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("### 📊 Championship Results")

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"""
        <div class="stat-block">
            <div class="stat-number">{r['win_rate']:.1f}%</div>
            <div class="stat-label">Win Rate</div>
            <div class="stat-sub">across 500 races</div>
        </div>""", unsafe_allow_html=True)
    col2.markdown(f"""
        <div class="stat-block">
            <div class="stat-number">P{r['avg_position']:.1f}</div>
            <div class="stat-label">Avg Finish</div>
            <div class="stat-sub">vs 5 opponents</div>
        </div>""", unsafe_allow_html=True)
    col3.markdown(f"""
        <div class="stat-block">
            <div class="stat-number">{r['ai_avg_time']:.0f}s</div>
            <div class="stat-label">AI Race Time</div>
            <div class="stat-sub">±{r['ai_std']:.0f}s</div>
        </div>""", unsafe_allow_html=True)
    col4.markdown(f"""
        <div class="stat-block">
            <div class="stat-number">+{r['gain_vs_human']:.0f}s</div>
            <div class="stat-label">Gained vs Human</div>
            <div class="stat-sub">pits {r['human_pits']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
        <div class="killer-line">
            Unlike brute-force optimization, the agent learns strategies that generalise across unseen conditions.
        </div>
        <div class="bridge-line">
            The same framework applies to finance, robotics, and real-world planning under uncertainty.
        </div>
    """, unsafe_allow_html=True)

    # Training curve
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("### 📈 Training Progress")
    st.caption("Started completely random. The red line shows the AI getting smarter — every dip is a better strategy discovered.")

    x = list(range(0, len(best_times) * 100, 100))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=actual_times, mode="lines",
                             name="Each Race", line=dict(color="#ff6b6b", width=1), opacity=0.35))
    fig.add_trace(go.Scatter(x=x, y=best_times, mode="lines",
                             name="Best So Far", line=dict(color="#e8002d", width=2.5)))
    fig.update_layout(
        height=280, margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Episode", yaxis_title="Race Time (s)",
        legend=dict(orientation="h", y=1.1),
        font=dict(color="#666", size=11),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Position distribution
    st.markdown("### 🏁 500-Race Finish Distribution")
    positions = r['all_positions']
    pos_counts = [positions.count(i) for i in range(1, 7)]
    pos_labels = ["P1 🏆", "P2", "P3", "P4", "P5", "P6"]
    colors = ["#0B2D72", "#0992C2", "#0AC4E0", "#F6E7BC", "#444", "#333"]
    fig2 = go.Figure(go.Bar(
        x=pos_labels, y=pos_counts, marker_color=colors,
        text=pos_counts, textposition="outside",
        textfont=dict(color="#E9E9E9", size=11),
    ))
    fig2.update_layout(
        height=260, margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=False, showticklabels=False),
        xaxis=dict(showgrid=False),
        font=dict(color="#666", size=11), showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Technical expander
    with st.expander("🔬 Behind the Scenes — Technical Details"):
        st.markdown("""
**Algorithm:** Tabular Q-Learning

**State:** lap number · tire wear · safety car · pit count · fuel level

**Actions:** Pit on SOFT / MEDIUM / HARD / Stay out

**Reward:** finishing position vs 5 opponents + race time delta

**Physics:** tire degradation · fuel burn · safety car periods · pit stop cost

**Why RL?** Future conditions are uncertain — fixed rules can't adapt. The agent learns which decisions pay off across thousands of variable scenarios.
        """)

    # Engineering challenges — SHORT
    st.markdown("""
        <div class="info-card">
            <div class="info-card-title">⚙️ Engineering Challenges</div>
            🎲&nbsp; Random safety cars — no two races are identical<br>
            🧠&nbsp; Must generalise, not memorise — tested on 500 unseen scenarios<br>
            📊&nbsp; Learned policy vs brute-force — agent competes against optimal search
        </div>
    """, unsafe_allow_html=True)

    # ── HUMAN vs AI ───────────────────────────────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("### 🆚 Now Race It Yourself")
    st.caption(
        "Pick when to swap tires. The AI picks its own. Same track, same random conditions — best decision wins.")

    sc_key = f"sc_{track}"
    if sc_key not in st.session_state:
        st.session_state[sc_key] = safety_car_periods(total_laps)

    col1, col2 = st.columns(2)
    with col1:
        human_pit1 = st.number_input("Your tire swap 1 (lap)",
                                     min_value=1, max_value=total_laps - 1, value=total_laps // 3, key="pit1")
    with col2:
        human_pit2 = st.number_input("Your tire swap 2 (lap)",
                                     min_value=1, max_value=total_laps - 1, value=total_laps * 2 // 3, key="pit2")

    if st.button("🏁 Race!", type="primary"):
        st.session_state[sc_key] = safety_car_periods(total_laps)
        shared_sc = st.session_state[sc_key]
        human_pits = sorted(set([int(human_pit1), int(human_pit2)]))
        snap_tire = track_data['default_tire']

        human_time_r, human_laps, human_cumulative, _ = race_simulation(
            human_pits, track, tire_comp=snap_tire, fixed_sc=shared_sc)

        agent = st.session_state[agent_key]
        ai_strategy, _, _ = run_race_with_ai(
            agent, track, evaluation_mode=True, fixed_sc=shared_sc)
        ai_pits = [lap for lap, _ in ai_strategy]
        ai_time_r, ai_laps, ai_cumulative, _ = race_simulation(
            ai_pits, track, tire_comp=snap_tire, fixed_sc=shared_sc)

        gap = human_time_r - ai_time_r

        st.session_state["race_result"] = {
            "human_time":       human_time_r,
            "human_laps":       human_laps,
            "human_cumulative": human_cumulative,
            "human_pits":       human_pits,
            "ai_time":          ai_time_r,
            "ai_laps":          ai_laps,
            "ai_cumulative":    ai_cumulative,
            "ai_pits":          ai_pits,
            "gap":              gap,
            "sc_laps":          sorted(list(shared_sc)),
            "human_stint2":     total_laps - human_pits[-1],
            "ai_stint2":        total_laps - ai_pits[-1] if ai_pits else 0,
        }

    if "race_result" in st.session_state:
        res = st.session_state["race_result"]
        gap = res["gap"]
        gap_abs = abs(gap)

        col1, col2, col3 = st.columns(3)
        col1.metric("👤 You",  f"{res['human_time']:.1f}s",
                    f"Swaps: {res['human_pits']}")
        col2.metric("🤖 AI",   f"{res['ai_time']:.1f}s",
                    f"Swaps: {res['ai_pits']}")
        col3.metric("Gap",     f"{gap_abs:.1f}s",
                    "You win! 🏆" if gap < 0 else "AI wins 🤖")

        if gap < 0:
            st.markdown(
                '<div class="win-banner win">🏆 You beat the AI!</div>', unsafe_allow_html=True)
        elif gap > 0:
            st.markdown(
                '<div class="win-banner lose">🤖 AI wins — it learned this on its own.</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="win-banner draw">🤝 Dead heat!</div>', unsafe_allow_html=True)

        sc_laps = res["sc_laps"]
        h_stint2 = res["human_stint2"]
        ai_stint2 = res["ai_stint2"]

        if sc_laps:
            sc_story = f"Safety car on lap {sc_laps[0]} — the AI was trained on thousands of races with exactly these disruptions."
        else:
            sc_story = "No safety car — pure strategy decided it."

        if ai_stint2 > h_stint2:
            stint_story = f"AI ran final tires {ai_stint2 - h_stint2} laps longer — it learned holding out pays off."
        elif ai_stint2 < h_stint2:
            stint_story = f"You ran final tires {h_stint2 - ai_stint2} laps longer — degradation cost you in the closing laps."
        else:
            stint_story = "Identical tire runs — gap came down to precise swap timing."

        if gap_abs < 5:
            gap_story = "Incredibly close — fractions of a second across the whole race."
        elif gap_abs < 30:
            gap_story = f"{gap_abs:.0f}s gap — roughly {gap_abs / track_data['base_lap']:.1f} laps of time lost to strategy."
        else:
            gap_story = f"Dominant {gap_abs:.0f}s gap — race-winning margin in real motorsport."

        st.markdown(f"""
            <div class="insight">
                🎲 <b style="color:#ccc">Conditions:</b> {sc_story}<br><br>
                🔄 <b style="color:#ccc">Strategy:</b> {stint_story}<br><br>
                ⏱️ <b style="color:#ccc">The gap:</b> {gap_story}
            </div>
        """, unsafe_allow_html=True)

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=res["human_laps"], y=res["human_cumulative"],
                                  mode="lines", name="👤 You", line=dict(color="#4a90e2", width=2)))
        fig3.add_trace(go.Scatter(x=res["ai_laps"], y=res["ai_cumulative"],
                                  mode="lines", name="🤖 AI", line=dict(color="#e8002d", width=2)))
        for p in res["human_pits"]:
            fig3.add_vline(x=p, line_dash="dot",
                           line_color="#4a90e2", opacity=0.4)
        for p in res["ai_pits"]:
            fig3.add_vline(x=p, line_dash="dot",
                           line_color="#e8002d", opacity=0.4)
        fig3.update_layout(
            height=280, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Lap", yaxis_title="Cumulative Time (s)",
            legend=dict(orientation="h", y=1.1),
            font=dict(color="#666", size=11),
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("Dotted lines = tire swap laps  |  Blue = you  |  Red = AI")

    # ── OWNERSHIP + TAKEAWAY ──────────────────────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class="ownership-block">
                <div class="ownership-title">🛠️ Designed & Implemented</div>
                ✔&nbsp; Custom race physics simulator<br>
                ✔&nbsp; RL training loop from scratch<br>
                ✔&nbsp; 500-race evaluation framework<br>
                ✔&nbsp; Interactive deployment
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="takeaway-block">
                <div class="takeaway-title">💡 What this demonstrates</div>
                🏗️&nbsp; Simulation design from scratch<br>
                🧠&nbsp; RL agent training without libraries<br>
                📊&nbsp; Learned vs optimal strategy evaluation<br>
                🌐&nbsp; Complex ML as interactive system
            </div>
        """, unsafe_allow_html=True)

# ── TECH STACK ────────────────────────────────────────────────────────────────
st.markdown("""
    <div class="tech-stack">
        Python &nbsp;·&nbsp; Streamlit &nbsp;·&nbsp; Q-Learning &nbsp;·&nbsp;
        Plotly &nbsp;·&nbsp; FastF1 &nbsp;·&nbsp; NumPy
    </div>
""", unsafe_allow_html=True)

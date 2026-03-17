# 🏎️ F1 Pit Optimizer

A reinforcement learning-powered F1 race strategy simulator built with Streamlit and Q-learning.

---

## 📁 Project Structure

```
FPO/
├── app.py                  # Home page — summary metrics
├── qlearning.py            # Q-learning agent — training & evaluation logic
├── strategies.csv          # Saved strategy results (auto-generated)
├── README.md
│
├── pages/
│   ├── 1_simulator.py      # Lap-by-lap simulator with real F1 data toggle
│   ├── 2_strategy_lab.py   # Brute-force strategy ranker + CSV saver
│   └── 3_analytics.py      # Strategy leaderboard + live AI performance charts
│
└── utils/
    ├── __init__.py         # Core physics: wear, lap time, race simulation
    └── f1_config.py        # Track configs + tire multipliers
```

---

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install streamlit plotly fastf1 numpy pandas
```

### 2. Run the app
```bash
streamlit run app.py
```

No pre-training needed. The AI trains live in the browser when you open the Analytics page.

---

## 🏁 Tracks

| Track            | Laps | Base Lap | Tire Wear |
|------------------|------|----------|-----------|
| Monaco_Street    | 78   | 78.5s    | High      |
| Silverstone_Fast | 52   | 85.2s    | Medium    |
| Spa_LongWet      | 44   | 96.1s    | Medium    |

---

## 🧠 How the AI Works

The Q-learning agent learns pit stop timing by:
- **State**: lap number, tire wear, compound, pit count, fuel level, safety car status
- **Actions**: pit on SOFT / MEDIUM / HARD / no pit
- **Reward**: combination of lap time, finishing position vs 5 opponents, tire management
- **Training**: 100,000 episodes with ε-greedy exploration and decaying learning rate

The agent trains fresh each session directly in the browser with a live progress bar.
Results are cached in session state — switching tabs won't re-trigger training.
Hit **🔄 Retrain Agent** on the Analytics page to start a new training run.

---

## 📊 Pages

- **Simulator** — adjust lap, compound, rain and see simulated vs real Verstappen lap times
- **Strategy Lab** — brute-force all pit strategies for a track, rank by total race time, save top 5
- **Analytics** — two tabs:
  - 🏁 **Strategy Leaderboard** — best saved strategies per track from `strategies.csv`
  - 🤖 **AI Performance** — live training curve, 500-race championship results, win rate, AI vs human comparison
# 🏎️ F1 Pit Strategy Optimizer

🚀 **Live Demo:** https://fpogit-rjrdclu4kzda6dbjuqh24u.streamlit.app/

A reinforcement learning agent that learns to outrace human strategies through 100,000+ simulated races — built entirely from scratch.

---

## 🧠 What is this?

**Problem:** When should an agent act when future conditions are uncertain?

**Approach:** Train an AI through thousands of simulated races, learning from wins, losses, and random disruptions like safety cars.

**Result:** An agent that beats static human strategies by adapting to conditions no rule can predict.

---
## 📈 Learning Behavior

The agent improves through reinforcement learning across 100,000+ races.

### Training Curve
<img width="938" height="730" alt="Screenshot 2026-03-26 164314" src="https://github.com/user-attachments/assets/7ad539ac-0449-468c-80d0-a8ad6dc6a3d1" />
## 🏆 Results

- ✅ Trained over 100,000 simulated races
- 🏁 AI win rate: 75-85% vs fixed strategies (500-race evaluation)
- 📉 Stable convergence after ε-decay phase

<img width="884" height="594" alt="image" src="https://github.com/user-attachments/assets/4b2f911f-1eac-4d57-a59f-3b32b2488f7f" />


## 📁 Project Structure

```
FPO/
├── app.py           # Entire project — one page, full story
├── qlearning.py     # Q-Learning agent — training & evaluation
├── requirements.txt
├── .gitignore
├── README.md
└── utils/
    ├── __init__.py  # Core physics: tire wear, lap time, race simulation
    └── f1_config.py # Track configs + tire multipliers
```

---

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. How to use
- Select a track
- Hit **🧠 Train AI** — watch it learn live with a training curve
- See championship results — win rate, avg finish, AI vs human time
- Hit **🏁 Race!** — pick your own pit laps and race the AI head-to-head

---

## 🏁 Tracks

| Track            | Laps | Base Lap | Tire Wear | Default Tire |
|------------------|------|----------|-----------|--------------|
| Silverstone_Fast | 52   | 85.2s    | Medium    | MEDIUM       |
| Spa_LongWet      | 44   | 96.1s    | Medium    | MEDIUM       |

---

## 🧠 How the AI Works

- **State**: lap number, tire wear, compound, pit count, fuel level, safety car status
- **Actions**: pit on SOFT / MEDIUM / HARD / don't pit
- **Reward**: lap time performance + finishing position vs 5 opponents + tire management
- **Training**: ε-greedy exploration with decaying learning rate over 100,000 episodes
- **Evaluation**: 500-race championship against 5 fixed opponents with random safety car events

The agent learned this strategy on its own — no pit rules were programmed.

---

## ⚙️ Tech Stack

Python · Streamlit · Q-Learning · Plotly · FastF1 · NumPy

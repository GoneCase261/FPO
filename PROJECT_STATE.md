F1 discrete lap strategy simulator (single car).

Goal: realistic pit timing + SC modeling + future RL.

Structure
app.py (Streamlit UI)

pages/
   1_simulator.py
   2_strategy_lab.py
   3_Analytics.py

utils/
  __init__.py
      wear()
      lap_time()
      safety_car_effect()
      race_simulation()
      generate_strategies()
  f1_config.py
Core Mechanics
strategies.csv

Lap-by-lap simulation

Tire wear increases each lap (track tdr × compound multiplier)

Fuel burns each lap (fbph / 60)

Lap time = base + fuel penalty + wear penalty

SC/VSC multiplies lap time (1.15 / 1.25)

Pit Logic

Pit time = 25s

During SC:

delta = base_laptime × (slowdown − 1)

effective_pit = max(pit_time − delta, FLOOR)

Tire wear reset

Fuel currently reset (not realistic F1)

Simplifications

No traffic

No rivals

SC lasts 1 lap only

Refueling allowed (non-F1 realistic)

Pit discount tied to own lap time

Current Focus

Improving realism + preparing for Q-learning.
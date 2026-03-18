import json
import random
import numpy as np
from collections import Counter
from utils import (
    F1_CONFIG,
    race_simulation,
    safety_car_periods,
    simulate_one_lap,
    safety_car_effect,
)

NO_PIT = 3
POSITION_REWARD = {1: 500, 2: 300, 3: 200, 4: 120, 5: 60, 6: -100}


class F1QAgent:
    def __init__(self):
        self.q_table = {}
        self.alpha = 0.2
        self.initial_alpha = 0.2
        self.alpha_min = 0.02
        self.alpha_decay = 0.995
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.9997

    def get_state(self, lap, tire_wear, current_compound="SOFT", pit_count=0, fuel=110, sc_active=False):
        lap_bucket = lap // 3
        tire_bucket = min(int(tire_wear // 25), 3)
        fuel_bucket = int(fuel // 25)
        sc_bucket = 1 if sc_active else 0
        return f"{lap_bucket}:{tire_bucket}:{current_compound[0]}:{pit_count}:{fuel_bucket}:{sc_bucket}"

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choices([0, 1, 2, 3], weights=[0.2, 0.4, 0.2, 0.2])[0]
        if state in self.q_table:
            q_vals = self.q_table[state]
            best_val = max(q_vals.values())
            best_acts = [a for a, v in q_vals.items() if v >= best_val - 0.1]
            return random.choice(best_acts)
        return 1  # default: MEDIUM

    def update_q(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}
        if next_state not in self.q_table:
            self.q_table[next_state] = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}

        current_q = self.q_table[state][action]
        next_max = max(self.q_table[next_state].values())
        self.q_table[state][action] = current_q + self.alpha * (
            reward + self.gamma * next_max - current_q
        )


def calculate_reward(position, actual_time, tire_wear, pit_laps, track, pos_score):
    track_data = F1_CONFIG[track]
    base_lap = track_data['base_lap']
    track_laps = track_data['laps']
    avg_lap_time = actual_time / track_laps

    time_reward = (base_lap - avg_lap_time) * 50
    pos_reward = POSITION_REWARD.get(position, 0) * 8
    pos_score_reward = pos_score * 1500
    tire_bonus = (100 - tire_wear) * 0.2
    pit_penalty = len(pit_laps) * 3
    wear_penalty = tire_wear * 0.1

    return time_reward + pos_reward + pos_score_reward + tire_bonus - pit_penalty - wear_penalty


def simulate_opponent(pit_plan, compound, track, fixed_sc):
    """Simulates an opponent with basic SC awareness using identical physics to run_race_with_ai."""
    track_data = F1_CONFIG[track]
    tire_wear = 0
    fuel = track_data['fuel_tank']
    total_time = 0
    pits_done = 0
    planned_pits = sorted(pit_plan)

    for lap in range(1, track_data['laps'] + 1):
        slowdown = safety_car_effect(lap, fixed_sc)
        sc_active = slowdown > 1.0

        tire_wear_next, fuel_next, lap_time_val = simulate_one_lap(
            lap, tire_wear, compound, fuel, track_data, fixed_sc, rain=0.0
        )
        total_time += lap_time_val

        should_pit = False
        if pits_done < len(planned_pits) and lap == planned_pits[pits_done]:
            should_pit = True
        elif (
            sc_active
            and pits_done < len(planned_pits)
            and tire_wear > 40
            and abs(lap - planned_pits[pits_done]) <= 4
            and lap > 15
        ):
            should_pit = True

        if should_pit:
            tire_wear_next = 0
            pits_done += 1
            if slowdown > 1.0:
                delta = track_data['base_lap'] * (slowdown - 1)
                effective_pit = max(track_data['pit_time'] - delta, 12.0)
            else:
                effective_pit = track_data['pit_time']
            total_time += effective_pit

        tire_wear = tire_wear_next
        fuel = fuel_next

    return total_time


def race_standings(pit_strategies, track="Silverstone_Fast", fixed_sc=None, ai_compound="MEDIUM", ai_time=None, evaluation_mode=False):
    compounds = ["SOFT", "MEDIUM", "HARD"]

    if evaluation_mode:
        # Fixed opponents for fair championship evaluation
        opponents = {
            "RedBull":  {"pits": [20, 38], "compound": "HARD"},
            "Ferrari":  {"pits": [16, 32], "compound": "SOFT"},
            "McLaren":  {"pits": [22, 40], "compound": "MEDIUM"},
            "Mercedes": {"pits": [19, 36], "compound": "HARD"},
            "Aston":    {"pits": [25, 42], "compound": "MEDIUM"},
        }
    else:
        # Randomized opponents during training for generalization
        base = {
            "RedBull":  {"pits": [20, 38], "compound": "HARD"},
            "Ferrari":  {"pits": [16, 32], "compound": "SOFT"},
            "McLaren":  {"pits": [22, 40], "compound": "MEDIUM"},
            "Mercedes": {"pits": [19, 36], "compound": "HARD"},
            "Aston":    {"pits": [25, 42], "compound": "MEDIUM"},
        }
        opponents = {
            team: {
                "pits": [max(10, p + random.randint(-3, 3)) for p in data["pits"]],
                "compound": random.choice(compounds)
            }
            for team, data in base.items()
        }

    if ai_time is not None:
        all_times = {"AI": ai_time}
    else:
        all_times = {"AI": race_simulation(
            pit_strategies, track,
            tire_comp=ai_compound,
            fixed_sc=fixed_sc,
            verbose=False,
        )[0]}

    for team, data in opponents.items():
        all_times[team] = simulate_opponent(
            data["pits"], data["compound"], track, fixed_sc)

    standings = sorted(all_times.items(), key=lambda x: x[1])
    positions = {team: i + 1 for i, (team, _) in enumerate(standings)}
    num_cars = len(all_times)
    pos_score = (num_cars - positions["AI"]) / (num_cars - 1)

    return standings, positions, pos_score


def run_race_with_ai(agent, track="Silverstone_Fast", evaluation_mode=False, fixed_sc=None):
    track_data = F1_CONFIG[track]
    total_laps = track_data['laps']
    PIT_WINDOW_START = max(15, total_laps // 5)       # ~20% into race
    PIT_WINDOW_END = total_laps - 15                # 15 laps before end
    pit_laps = []
    tire_wear = 0
    fuel = track_data['fuel_tank']
    current_compound = track_data['default_tire']
    total_race_time = 0

    if fixed_sc is None:
        fixed_sc = safety_car_periods(track_data['laps'])

    original_epsilon = agent.epsilon
    if evaluation_mode:
        agent.epsilon = 0.0

    for lap in range(1, track_data['laps'] + 1):
        slowdown = safety_car_effect(lap, fixed_sc)
        sc_active = slowdown > 1.0

        state = agent.get_state(lap, tire_wear, current_compound, len(
            pit_laps), fuel, sc_active=sc_active)
        action = agent.choose_action(
            state) if PIT_WINDOW_START <= lap <= PIT_WINDOW_END else NO_PIT

        compounds = ["SOFT", "MEDIUM", "HARD"]
        can_pit = (
            PIT_WINDOW_START <= lap <= PIT_WINDOW_END
            and len(pit_laps) < 2
            and (len(pit_laps) == 0 or lap - pit_laps[-1][0] > 15)
            and not (len(pit_laps) == 0 and lap < 18)
        )

        tire_wear_next, fuel_next, lap_time_val = simulate_one_lap(
            lap, tire_wear, current_compound, fuel, track_data, fixed_sc, rain=0.0
        )
        total_race_time += lap_time_val

        compound_next = current_compound
        pit_count_next = len(pit_laps)
        step_reward = -(lap_time_val - track_data['base_lap'])

        if action in [0, 1, 2] and can_pit:
            if lap < 18:
                step_reward -= 25
            elif lap < 19:
                step_reward -= 10
            if sc_active:
                step_reward += 35
            if compounds[action] == "MEDIUM":
                step_reward += 15
            elif compounds[action] == "SOFT":
                step_reward += 5
            elif compounds[action] == "HARD":
                step_reward -= 10
            if compounds[action] == current_compound:
                step_reward -= 20

            step_reward += 8 if tire_wear > 65 else -8
            stint_length = lap - (pit_laps[-1][0] if pit_laps else 0)
            if stint_length < 15:
                step_reward -= 20

            tire_wear_next = 0
            compound_next = compounds[action]
            pit_count_next += 1
            pit_laps.append((lap, compound_next))

            if slowdown > 1.0:
                delta = track_data['base_lap'] * (slowdown - 1)
                effective_pit = max(track_data['pit_time'] - delta, 12.0)
            else:
                effective_pit = track_data['pit_time']
            total_race_time += effective_pit

        next_slowdown = safety_car_effect(lap + 1, fixed_sc)
        next_sc_active = next_slowdown > 1.0
        next_state = agent.get_state(
            lap + 1, tire_wear_next, compound_next, pit_count_next, fuel_next,
            sc_active=next_sc_active,
        )

        if not evaluation_mode:
            agent.update_q(state, action, step_reward, next_state)

        tire_wear = tire_wear_next
        fuel = fuel_next
        current_compound = compound_next

    sim_pit_laps = [lap for lap, comp in pit_laps]
    first_compound = pit_laps[0][1] if pit_laps else current_compound

    _, positions, pos_score = race_standings(
        sim_pit_laps, track,
        fixed_sc=fixed_sc,
        ai_compound=first_compound,
        ai_time=total_race_time,
        evaluation_mode=evaluation_mode,
    )

    final_reward = calculate_reward(
        positions["AI"], total_race_time, tire_wear,
        sim_pit_laps, track, pos_score,
    )

    if not evaluation_mode:
        agent.update_q(state, NO_PIT, final_reward, next_state)

    agent.epsilon = original_epsilon
    if not evaluation_mode:
        agent.epsilon = max(agent.epsilon_min,
                            agent.epsilon * agent.epsilon_decay)
        agent.alpha = max(agent.alpha_min,   agent.alpha * agent.alpha_decay)

    return pit_laps, total_race_time, final_reward


def train_ai(episodes=100000):
    agent = F1QAgent()
    best_times = {track: float('inf') for track in F1_CONFIG}
    best_strategy = []
    episode_times = []
    qtable_sizes = []

    tracks = list(F1_CONFIG.keys())
    print("🧠 Training AI Strategist across all tracks...")

    for episode in range(episodes):
        # Rotate tracks randomly each episode
        track = random.choice(tracks)

        if episode % 10 == 0:
            fixed_sc = safety_car_periods(F1_CONFIG[track]['laps'])

        strategy, race_time, _ = run_race_with_ai(
            agent, track, fixed_sc=fixed_sc)
        sim_pit_laps = [lap for lap, comp in strategy]
        _, positions, pos_score = race_standings(
            sim_pit_laps, track=track, fixed_sc=fixed_sc, evaluation_mode=False)

        if episode % 10000 == 0:
            strat_display = [f"L{lap}{comp[0]}" for lap, comp in strategy]
            print(
                f"Ep {episode} [{track}]: P{positions['AI']} | Score={pos_score:.2f} | {strat_display}")

        if race_time < best_times[track]:
            best_times[track] = race_time
            best_strategy = strategy

        # Track overall best (Silverstone as reference)
        episode_times.append(best_times.get("Silverstone_Fast", race_time))

        # Track Q-table growth every 100 episodes
        if episode % 100 == 0:
            qtable_sizes.append(len(agent.q_table))

    return agent, best_strategy, episode_times, qtable_sizes


if __name__ == "__main__":
    ai_agent, _, episode_times, _ = train_ai(100000)

    ai_positions = []
    ai_times = []
    ai_strategies = []

    print("🏎️  Running 500-race championship...")
    for race in range(500):
        race_sc = safety_car_periods(F1_CONFIG["Silverstone_Fast"]['laps'])
        strategy, time, _ = run_race_with_ai(
            ai_agent, evaluation_mode=True, fixed_sc=race_sc)
        sim_pit_laps = [lap for lap, comp in strategy]
        standings, positions, _ = race_standings(
            sim_pit_laps, fixed_sc=race_sc, ai_time=time)

        ai_positions.append(positions["AI"])
        ai_times.append(time)
        ai_strategies.append([f"L{lap}{comp[0]}" for lap, comp in strategy])

        if race % 100 == 0:
            win_rate = sum(1 for p in ai_positions if p == 1) / \
                len(ai_positions) * 100
            print(
                f"Race {race}: Win Rate={win_rate:.0f}% | Latest: P{positions['AI']}")

    # 30-race evaluation
    eval_times = []
    eval_strategies = []
    for _ in range(30):
        eval_sc = safety_car_periods(F1_CONFIG["Silverstone_Fast"]['laps'])
        strategy, time, _ = run_race_with_ai(
            ai_agent, evaluation_mode=True, fixed_sc=eval_sc)
        eval_times.append(time)
        eval_strategies.append([f"L{lap}{comp[0]}" for lap, comp in strategy])

    final_time = np.mean(eval_times)
    final_std = np.std(eval_times)

    strategy_counts = Counter(tuple(s) for s in eval_strategies)
    best_strategy = list(strategy_counts.most_common(1)[0][0])

    human_time, _, _, _ = race_simulation(
        [20, 35], "Silverstone_Fast", fixed_sc=eval_sc, verbose=False)
    gain = human_time - final_time

    eval_standings, eval_positions, eval_pos_score = race_standings(
        [18, 34], fixed_sc=eval_sc, ai_time=final_time, evaluation_mode=True
    )

    wins = sum(1 for p in ai_positions if p == 1)
    podiums = sum(1 for p in ai_positions if p <= 3)

    print(f"\n🏆 500-RACE SUMMARY")
    print(f"AI Wins:    {wins}/500 ({wins/500*100:.1f}%)")
    print(f"Podiums:    {podiums}/500")
    print(f"Avg finish: P{np.mean(ai_positions):.1f}")
    print(f"AI strategy: {best_strategy}")
    print(f"AI avg time: {final_time:.0f}s ± {final_std:.0f}s")
    print(f"Human time:  {human_time:.0f}s")
    print(f"AI gain:     {gain:.0f}s ({gain/human_time*100:.1f}%)")

    # ── Save results for Analytics page ──────────────────────────────────────
    results = {
        "win_rate":      wins / 500 * 100,
        "avg_position":  float(np.mean(ai_positions)),
        "ai_avg_time":   float(final_time),
        "ai_std":        float(final_std),
        "human_time":    float(human_time),
        "gain_vs_human": float(gain),
        "best_strategy": best_strategy,
        "all_positions": ai_positions,
        # Every 100th ep to keep file small
        "episode_times": episode_times[::100],
    }

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n✅ Saved results.json — open the Analytics page to view charts.")

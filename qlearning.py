import matplotlib.pyplot as plt
import random
import numpy as np
from utils import race_simulation, F1_CONFIG, TIRE_MULTIPLIERS, safety_car_periods

base_lap_time = 85.2  # frm f1-config


class F1QAgent:
    def __init__(self):
        # q's empty dictionary
        self.q_table = {}  # "lap:tire:fuel": {0:points,1:points}
        self.initial_alpha = 0.1
        self.alpha = 0.1   # Learning speed
        self.gamma = 0.95  # Future reward value
        self.epsilon = 1.0  # 100% exploration
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.997  # decay per episode

    def get_state(self, lap, tire_wear, fuel, current_compound="SOFT", pit_count=0):
        tire_bucket = min(int(tire_wear // 10), 9)
        fuel_bucket = min(int(fuel // 5), 12)
        return f"{lap}:{tire_bucket}:{fuel_bucket}:{current_compound[0]}:{pit_count}"

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice([0, 1, 2, 3])

        if state in self.q_table:
            # Exploit: best
            q_vals = self.q_table[state]
            best_vals = max(q_vals.values())

            best_action = [a for a, v in q_vals.items() if v >
                           best_vals - 0.05]
            return random.choice(best_action) if best_action else 3
        return 3  # Default: stay

    def update_q(self, state, action, reward, next_state):
        if state not in self.q_table:
            # initializing if memory missing
            self.q_table[state] = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}
        if next_state not in self.q_table:
            self.q_table[next_state] = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}

        current_q = self.q_table[state][action]
        next_max = max(self.q_table[next_state].values())

        # New value = Old value + Learning rate × (Target − Old value)
        # target = reward + gamma * (best future val)
        self.q_table[state][action] = current_q + self.alpha * (
            reward + self.gamma * next_max - current_q
        )


def run_race_with_ai(agent, track="Silverstone_Fast", evaluation_mode=False, fixed_sc=None):
    """One complete race using AI decisions"""
    track_data = F1_CONFIG[track]

    pit_laps = []
    tire_wear = 0
    fuel = track_data['fuel_tank']
    current_compound = "SOFT"
    total_episode_reward = 0
    episode_memory = []

    # Simulate lap-by-lap decisions
    original_epsilon = agent.epsilon
    if evaluation_mode:
        agent.epsilon = 0.0
    for lap in range(1, track_data['laps'] + 1):
        # Current state
        state = agent.get_state(lap, tire_wear, fuel,
                                current_compound, len(pit_laps))

        # AI decides: pit (0) or continue (1)?
        action = agent.choose_action(state)
        episode_memory.append((state, action))

        # Simulate this lap
        tire_mult = TIRE_MULTIPLIERS.get(current_compound, 1.0)
        tire_wear = min(tire_wear + track_data['tdr'] * tire_mult, 100)
        fuel -= track_data['fbph'] / 60
        fuel = max(fuel, 0)

        # Good pit!
        compounds = ["SOFT", "MEDIUM", "HARD"]
        if (action in [0, 1, 2] and tire_wear > 70 and len(pit_laps) < 2 and lap > 15):
            new_compound = compounds[action]
            pit_laps.append((lap, new_compound))
            tire_wear = 0
            current_compound = new_compound  # tires switched at pit

        # HYBRID REWARDS: Small shaping + final race objective
        wear_penalty = tire_wear * 0.002  # Gentle wear guidance
        pit_penalty = 0.05 if action in [0, 1, 2] else 0  # Discourage bad pits
        reward = -wear_penalty - pit_penalty
        total_episode_reward += reward

        next_state = agent.get_state(
            lap + 1, tire_wear, fuel, current_compound, len(pit_laps))
        if not evaluation_mode:
            agent.update_q(state, action, reward, next_state)

    # Final race time (using real simulator)
    sim_pit_laps = [lap for lap, comp in pit_laps]
    actual_time = race_simulation(
        sim_pit_laps, track, verbose=False, fixed_sc=fixed_sc)[0]

    final_reward = -actual_time / 1000  # Lower time = higher reward

    final_state = agent.get_state(
        track_data["laps"], tire_wear, fuel, current_compound, len(pit_laps))

    if len(pit_laps) > 2:
        final_reward -= 300  # penalty for too many stops

    if not evaluation_mode:
        # UNIFORM BACKPROP: Q-table learns BEST strategy (L16S,L33S)
        backprop_reward = final_reward / len(episode_memory)

        # Backprop through trajectory (proper next states)
        states = [s for s, a in episode_memory] + [final_state]
        for i, (state, action) in enumerate(episode_memory):
            next_state = states[i+1]  # Proper next state!
            agent.update_q(state, action, backprop_reward, next_state)

    agent.epsilon = original_epsilon
    if not evaluation_mode:  # Decay only during training episodes
        agent.epsilon = max(agent.epsilon_min,
                            agent.epsilon * agent.epsilon_decay)

    return pit_laps, actual_time, final_reward


def train_ai(episodes=2000):
    agent = F1QAgent()
    best_time = float('inf')  # initialize best time as infinity
    best_strategy = []

    # LEARNING CURVE
    episode_times = []
    epsilon_history = []

    print("🧠 Training AI Strategist...")

    for episode in range(episodes):
        agent.alpha = max(0.02, 0.1 * (0.995 ** episode))
        strategy, race_time, reward = run_race_with_ai(agent)

        if race_time < best_time:
            best_time = race_time
            best_strategy = strategy

        episode_times.append(best_time)
        epsilon_history.append(agent.epsilon)

        if episode % 200 == 0:
            strategy_display = [
                f"L{lap}{comp[0]}" for lap, comp in best_strategy]
            print(f"Ep {episode}: ε={agent.epsilon:.3f} | Best={best_time:.0f}s| "
                  f"Strategy={strategy_display} | "
                  f"Q-Table={len(agent.q_table)}")

    return agent, best_strategy, best_time, episode_times, epsilon_history


# 🏁 LAUNCH AI TRAINING!
if __name__ == "__main__":
    ai_agent, best_strategy, best_time, episode_times, epsilon_history = train_ai(
        2000)

    def moving_average(data, window=50):
        return np.convolve(data, np.ones(window)/window, mode='valid')

    # PLOT LEARNING CURVE
    plt.figure(figsize=(12, 4))

    plt.subplot(1, 2, 1)
    smoothed_times = moving_average(episode_times, 50)
    plt.plot(episode_times, alpha=0.3, color='lightblue', label="Raw Episodes")
    plt.plot(range(49, len(smoothed_times)+49), smoothed_times,
             linewidth=3, color='darkblue', label="Smoothed Trend")
    plt.title('Learning Curve')
    plt.ylabel('Best Race Time (s)')
    plt.xlabel('Episode')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    plt.plot(epsilon_history, linewidth=2, color='green')
    plt.title('Epsilon Decay')
    plt.ylabel('Epsilon')
    plt.xlabel('Episode')
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('week22_learning_curve.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("📈 Learning curve saved: week22_learning_curve.png")

    # Compare Q vs human
    human_time, _, _, _ = race_simulation(
        [20, 35], "Silverstone_Fast", verbose=False)

   # PAIRED EVALUATION - SAME ENVIRONMENT
print("\n" + "="*70)
print("🔬 PAIRED EVALUATION: Identical Race Conditions")
print("="*70)

fixed_sc = safety_car_periods(F1_CONFIG["Silverstone_Fast"]['laps'])

# AI in FIXED environment (30 runs)
eval_times = []
eval_strategies = []
for _ in range(30):
    strategy, time, _ = run_race_with_ai(
        ai_agent, evaluation_mode=True, fixed_sc=fixed_sc)
    eval_times.append(time)
    eval_strategies.append([f"L{lap}{comp[0]}" for lap, comp in strategy])

final_time = np.mean(eval_times)
final_std = np.std(eval_times)
final_strategy = max(set(tuple(s) for s in eval_strategies), key=[
                     tuple(s) for s in eval_strategies].count)[0]

# Human in SAME FIXED environment
human_time, _, _, _ = race_simulation(
    [20, 35], "Silverstone_Fast", fixed_sc=fixed_sc, verbose=False)

print(
    f"🤖 TRAINED AI:     {final_strategy} → {final_time:.0f}s ±{final_std:.0f}s")
print(f"👨  Human:         [20,35] → {human_time:.0f}s")
gain = human_time - final_time
print(f"🎯 AI GAINS:       {gain:.0f}s ({gain/human_time*100:.1f}%)")
print("="*70)

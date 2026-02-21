import random
from .f1_config import F1_CONFIG, TIRE_MULTIPLIERS


# 1. TIRE WEAR CALCULATOR - How tires degrade lap-by-lap
def wear(lap_no):
    """FIXED: Realistic tire wear progression"""
    if lap_no <= 20:
        return lap_no * 1.5      # 1.5% per lap early
    elif lap_no <= 40:
        return 30 + (lap_no-20) * 2.5  # Accelerates
    else:
        return min(95 + (lap_no-40) * 1.0, 100)  # Caps at 100%


# 2. LAP TIME CALCULATOR - Single lap speed
def lap_time(wear_pct, tire_comp, rain, fuel_kg, track_data):
    """w = tire wear % (0-100). Returns lap time in SECONDS"""
    # BASE LAP TIME (track-specific)
    base_time = track_data['base_lap']

    # FUEL PENALTY (heavy car = slow)
    fuel_penalty = fuel_kg * 0.03  # 110kg = +3.3s, 50kg = +1.5s
    lap_time = base_time + fuel_penalty  # Start with base + fuel

    # TIRE WEAR PENALTY
    if 0 <= wear_pct <= 30:
        pass  # Fresh tires = no penalty
    elif 30 < wear_pct <= 70:
        penalty = (wear_pct - 30) * 0.1  # 50% wear = +2s
        lap_time += penalty
    else:  # >70% wear
        base_penalty = 4   # 70% wear penalty
        extra_penalty = (wear_pct - 70) * 0.3  # 90% = +7s total
        lap_time += base_penalty + extra_penalty

    # TIRE COMPOUND FACTORS
    if tire_comp == "SOFT":
        lap_time -= 0.5    # Fastest but wears quick
    elif tire_comp == "HARD":
        lap_time += 0.5    # Slower but durable
    elif tire_comp == "INTERMEDIATE":
        lap_time += 1.0    # Wet track tires
    elif tire_comp == "WET":
        lap_time += 2.0    # Heavy rain tires

    # RAIN EFFECTS
    if tire_comp in ['SOFT', 'MEDIUM', 'HARD']:  # Wrong tires in rain
        lap_time += rain * 4  # 0.5 rain = +2s
    elif tire_comp in ['INTERMEDIATE', 'WET'] and rain < 0.3:
        # Wet tires on drying track
        lap_time += (0.3 - rain) * 3
    return lap_time


#   SAFETY CAR
def safety_car_periods(total_laps):
    """Creates 0-2 realistic SC periods (3-6 laps each)
    Real F1: 85s lap → SC = 115-125s lap
    115 ÷ 85 = 1.35x, 125 ÷ 85 = 1.47x
    We use 1.40x = PERFECT middle"""
    sc_events = []
    num_sc = random.randint(0, 2)  # 0, 1, or 2 SC periods per race

    for _ in range(num_sc):
        start_lap = random.randint(10, total_laps - 8)  # Anywhere lap 10+
        duration = random.randint(3, 6)  # Real SC = 3-6 laps
        sc_events.extend(range(start_lap, min(
            start_lap + duration, total_laps)))

    return set(sc_events)  # Unique SC laps


def safety_car_effect(lap, sc_periods):
    """Returns slowdown factor for THIS lap"""
    if lap in sc_periods:
        return 1.40  # Full SC = 40% slower (real F1)
    return 1.0  # Green flag


# 3. FULL RACE SIMULATOR - Complete race with pits
def race_simulation(pit_laps, track_name, tire_comp="SOFT", rain=0.0, verbose=0):
    """
    pit_laps = [18, 37]  # Pit on lap 18 + 37
    Returns: (total_race_time, lap_numbers, cumulative_times, fuel_history)
    """
    track_data = F1_CONFIG[track_name]
    total_laps = track_data['laps']

    # Generate random SC periods for THIS race
    sc_periods = safety_car_periods(total_laps)
    if verbose:
        print(f"SC periods: {sorted(list(sc_periods))}")

    total_time = 0
    tire_wear = 0        # Resets on pit stops
    fuel = track_data['fuel_tank']
    lap_numbers = []
    cumulative_times = []
    fuel_history = []

    # Simulate every lap
    for lap in range(1, track_data['laps'] + 1):
        # TIRE WEAR (lap-by-lap degradation)
        tire_mult = TIRE_MULTIPLIERS.get(tire_comp, 1.0)
        track_wear_rate = track_data['tdr'] * tire_mult  # Track-specific
        tire_wear = min(tire_wear + track_wear_rate, 100)

        # FUEL CONSUMPTION - Real F1 (SC saves fuel)
        """SC laps = lift throttle + low RPM = 40% less fuel
        1.0     kg/lap → 0.6 kg/lap during SC"""
        slowdown = safety_car_effect(lap, sc_periods)
        fuel_save = 0.6 if slowdown > 1.0 else 1.0  # SC = 40% less fuel burn
        fuel -= (track_data['fbph'] / 60) * fuel_save
        fuel = max(fuel, 0)

        # RECORD FUEL (clean display)
        fuel_history.append(max(fuel, 0))  # No negative fuel

        # CALCULATE LAP TIME
        base_laptime = lap_time(tire_wear, tire_comp, rain, fuel, track_data)
        laptime = base_laptime*slowdown  # Start with green flag lap
        total_time += laptime

        # PIT STOP

        if lap in pit_laps:
            tire_wear = 0
            pit_time = track_data['pit_time']  # Always 25s - real physics

            """track_data['base_lap'] = 85s (Silverstone record)
                slowdown = 1.40 (SC)
                delta = 85 * 0.40 = 34s (field extra time)
                pit_time = 25s
                effective_pit = max(25 - 34, 12.0) = 12.0s """
            if slowdown > 1.0:
                # REAL F1: Use track base lap (not worn lap)
                track_base = track_data['base_lap']  # 85s Silverstone
                delta = track_base * (slowdown - 1)  # 85 * 0.40 = 34s
                # safety clamp
                effective_pit = max(pit_time - delta, 12.0)
                total_time += effective_pit
                if verbose:
                    print(
                        f"Lap {lap}: SC PIT ({pit_time}s → {effective_pit:.1f}s)")
            else:
                total_time += pit_time
                if verbose:
                    print(f"Lap {lap}: Normal PIT ({pit_time}s)")

        # RECORD THIS LAP
        lap_numbers.append(lap)
        cumulative_times.append(total_time)

    return total_time, lap_numbers, cumulative_times, fuel_history


# 4. STRATEGY GENERATOR - All possible pit combinations
def generate_strategies(num_stops):
    """
    num_stops=2 → Returns 300+ strategies: [[15,32], [16,33], [15,33], ...]
    Realistic ranges only (no lap 1 pits, min 12 laps between stops)
    """
    strategies = []

    if num_stops == 1:
        for pit1 in range(25, 46):
            strategies.append([pit1])
    elif num_stops == 2:
        for pit1 in range(15, 31):      # First pit lap 15-30
            for pit2 in range(pit1+15, 51):  # Second pit 15+ laps later
                strategies.append([pit1, pit2])
    elif num_stops == 3:
        for pit1 in range(12, 26):
            for pit2 in range(pit1+12, 41):
                for pit3 in range(pit2+12, 56):
                    strategies.append([pit1, pit2, pit3])
    elif num_stops == 4:
        for pit1 in range(10, 22):
            for pit2 in range(pit1+10, 35):
                for pit3 in range(pit2+10, 48):
                    for pit4 in range(pit3+10, 56):
                        strategies.append([pit1, pit2, pit3, pit4])

    return strategies

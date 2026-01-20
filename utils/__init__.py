import streamlit as st


def wear(l):
    tw = st.session_state.tire_wear
    if 0 < l <= 45:
        if l > 30:
            tw = min(l*2+l-30, 100)
        else:
            tw = min(l*2, 100)
    elif l > 45 and l <= 60:
        # extra wear added after lap 30
        tw = min(l*2+l-30, 100)
    return tw


def lap_time(w, tc, r, f):
    base_time = 90
    fuel_penalty = f * 0.03  # 0.03-> fuel factor(0.3/10)seconds per kg
    # About 0.25–0.35 seconds per 10 kg of fuel per lap.
    if 0 <= w <= 30:
        lt = base_time
    elif 30 < w <= 70:
        penalty = (w - 30)*0.1
        lt = base_time+penalty
    else:
        penalty = 4  # 70-30 * 0.1 for penalty at 70
        extra = (w-70)*0.3
        lt = base_time+penalty+extra
    lt += fuel_penalty

# BASE TIME FOR EACH TYRE TYPE (WITHOUT RAIN)
    if tc == "SOFT":  # tire compound factor
        lt = lt-0.5
    elif tc == "MEDIUM":
        lt += 0
    elif tc == "HARD":
        lt += 0.5
    elif tc == "INTERMEDIATE":
        lt += 1.0
    elif tc == "WET":
        lt += 2.0
    # RAIN FACTOR EFFECTS
    if tc in ['SOFT', 'MEDIUM', 'HARD']:
        lt += r*4
    elif tc in ['INTERMEDIATE', 'WET']:
        if r < 0.3:  # self set rain threshold
            dry_penalty = (0.3-r)*3
        elif r >= 0.3:
            dry_penalty = 0
        lt += dry_penalty

    return lt


def race_simulation(pit_laps, tire_comp="SOFT", rain=0.0):
    total_time = 0
    w = 0  # fresh tyres at every new race simulation
    fuel = 110  # (kg)
    time_record = []
    lap_n = []
    fuel_left = []
    for lap in range(1, 61):
        # purely linear wear increase, not based on wear function
        w = min(w+2, 100)
        fuel -= 110/60
        fuel_left.append(fuel)

        laptime = lap_time(w, tire_comp, rain, fuel)
        total_time += laptime

        if lap in pit_laps:
            w = 0
            total_time += 25

        lap_n.append(lap)
        time_record.append(total_time)
    # cummulative time after every lap
    return total_time, lap_n, time_record, fuel_left


def generate_strategies(num_stops):
    strategies = []

    if num_stops == 1:
        for pit1 in range(25, 46):
            strategies.append([pit1])
    elif num_stops == 2:
        for pit1 in range(15, 31):
            for pit2 in range(pit1+15, 51):
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

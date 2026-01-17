import streamlit as st
import pandas as pd

# st.set_page_config(layout="wide")

if "tire_wear" not in st.session_state:
    st.session_state.tire_wear = 0

st.title('🏎️ F1 Pit Optimizer v1.0 - Week 11')
lap_no = st.slider('Lap Progress:', 0, 60, 0)
num_stops = st.slider("Number of stops", 1, 4, 2)
pit_input = st.text_input("Pit laps(comma separated):")
pit_laps = [int(x.strip()) for x in pit_input.split(",") if x.strip()]
if len(pit_laps) != num_stops:
    st.error(f"Expected {num_stops} stops, got {len(pit_laps)}")
with open('canvas.html', 'r', encoding='utf-8') as c:
    code = c.read()
    code = code.replace('{lap_no}', str(lap_no))

if lap_no > 45 and lap_no != 60:
    st.warning("🛞 Tires CRITICAL! Consider Pitting Soon.")
    if st.button('🛑 PIT STOP'):
        st.session_state.tire_wear = 0
        st.success("🔧 Pitted! New tyres fitted, you’re ready to push again!")
elif lap_no == 60:
    if st.button("🏁 Finish Race!"):
        st.balloons()
        st.success("🏆 Race Complete! Great job!")
else:
    pass


st.components.v1.html(code, height=220)

# ------FUNCTIONS--------


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


st.metric("Tire Wear:", f"{wear(lap_no)}%")  # realtime based on slider
tire_comp = st.selectbox(
    "Tire compound:", ["SOFT", "MEDIUM", 'HARD', 'INTERMEDIATE', 'WET'], index=0)
rain = st.slider("Rain", 0.0, 1.0, 0.0, 0.1)


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


# realtime based on slider
st.metric("LAP TIME:", f"{lap_time(wear(lap_no), tire_comp, rain, 110)} s")

# Slider + metrics showing “current lap” wear/time.
# Selectbox controlling pit lap for the full‑race simulation and chart


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


if st.button("SIMULATE RACE") and pit_laps:
    total_time, lap_numbers, cumulative_times, fuel_left = race_simulation(
        pit_laps, tire_comp, rain)

    df = pd.DataFrame({
        'Lap': lap_numbers,
        'Fuel Left': fuel_left,
        'Cumulative Time': cumulative_times
    })
    st.write(df)
    st.line_chart(df.set_index('Lap'))


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


if st.button("🏆 FIND TOP 5 STRATEGIES") and (tire_comp, rain):
    strategies = generate_strategies(num_stops)
    st.info(f"Generated {len(strategies)} {num_stops}-stop strategies")

    results = []
    for strategy in strategies:
        total_time, lap_numbers, cumulative_times, fuel_left = race_simulation(
            strategy, tire_comp, rain)
        results.append({"strategy": strategy, "time": total_time})

    # SORT BY TIME
    results.sort(key=lambda x: x["time"])
    top_5 = results[:5]

    for i, result in enumerate(top_5, 1):
        gap = result["time"] - top_5[0]['time']
        st.write(
            f"{i}. {result['strategy']} → {result['time']:.1f}s {'(+%.1f s)' % gap if i > 1 else '(BEST)'}")

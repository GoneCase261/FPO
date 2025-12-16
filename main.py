import streamlit as st

# st.set_page_config(layout="wide")

if "tire_wear" not in st.session_state:
    st.session_state.tire_wear = 0

st.title('🏎️ F1 Pit Optimizer v2.0 - Week 7')
lap_no = st.slider('Lap Progress:', 0, 60, 0)

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
    "Tire compound:", ["SOFT", "MEDIUM", 'HARD'], index=0)
rain = st.slider("Rain", 0.0, 1.0, 0.0, 0.1)


def lap_time(w, tc, r):
    base_time = 90
    if 0 <= w <= 30:
        lt = base_time
    elif 30 < w <= 70:
        penalty = (w - 30)*0.1
        lt = base_time+penalty
    else:
        penalty = 4  # 70-30 * 0.1 for penalty at 70
        extra = (w-70)*0.3
        lt = base_time+penalty+extra

    if tc == "SOFT":  # tire compound factor
        lt = lt-0.5
    elif tc == "MEDIUM":
        lt += 0
    elif tc == "HARD":
        lt += 0.5

    lt += r*3  # rain factor

    return lt


# realtime based on slider
st.metric("LAP TIME:", f"{lap_time(wear(lap_no), tire_comp, rain)} s")

# Slider + metrics showing “current lap” wear/time.
# Selectbox controlling pit lap for the full‑race simulation and chart


def race_simulation(p1, p2, pit_penalty=25):
    total_time = 0
    w = 0  # fresh tyres at every new race simulation
    time_record = []
    lap_n = []
    for lap in range(1, 61):
        # purely linear wear increase, not based on wear function
        w = min(w+2, 100)
        laptime = lap_time(w, tire_comp, rain)
        total_time += laptime
        if p1 == p2 and p1 != 0:
            if p1 == lap:
                w = 0
                total_time += pit_penalty
        else:
            if lap == p1 and p1 != 0:
                w = 0
                total_time += pit_penalty

            if lap == p2 and p2 != 0:
                w = 0
                total_time += pit_penalty

        lap_n.append(lap)
        time_record.append(total_time)
    return total_time, lap_n, time_record  # cummulative time after every lap


pits = []
time = []
for pit1 in range(0, 61):
    for pit2 in range(0, 61):
        t, ln, tr = race_simulation(pit1, pit2)
        pits.append(f"({pit1}, {pit2})")
        time.append(t)

a = min(time)
c = max(time)
b = pits[time.index(a)]
d = pits[time.index(c)]
st.write(f"Overall best pit strategy is : {b} (total {a:.2f} s). ")
st.write(f"This is {c-a:.2f} s faster than pit at {d}.")

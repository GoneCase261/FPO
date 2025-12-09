import streamlit as st
import pandas as pd

if "tire_wear" not in st.session_state:
    st.session_state.tire_wear = 0

st.title('🏎️ F1 Pit Optimizer v0.1 - Week 1')
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


def lap_time(w):
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
    return lt


# realtime based on slider
st.metric("LAP TIME:", f"{lap_time(wear(lap_no))} s")

"""THE RACE SIMULATION IS FOR ENTIRE RACE, WHERE AS METRIC AND THE SLIDER IS FOR PER LAP TIRE WEAR"""


def race_simulation(pit_lap, pit_penalty=25):
    total_time = 0
    w = 0
    time_record = []
    lap_n = []
    for lap in range(1, 61):
        # purely linear wear increase, not based on wear function
        w = min(w+2, 100)
        laptime = lap_time(w)
        total_time += laptime
        if lap == pit_lap:
            w = 0
            total_time += pit_penalty
        lap_n.append(lap)
        time_record.append(total_time)
    return total_time, lap_n, time_record  # cummulative time after every lap


# lets u select which lap to pit in, in the UI
pit_lap = st.selectbox("Pit lap:", list(range(1, 61)), index=1)

t1, ln1, tr1 = race_simulation(pit_lap)
st.write(f"{t1:.2f}s")
st.write(f"{ln1}")
st.write(f"{tr1}")

# data converted into tabular form
df = pd.DataFrame({
    'time': tr1,
    'lap': ln1
})

st.line_chart(df, x='lap', y='time')

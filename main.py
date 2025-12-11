import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

if "tire_wear" not in st.session_state:
    st.session_state.tire_wear = 0

st.title('🏎️ F1 Pit Optimizer v1.0 - Week 6')
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
        laptime = lap_time(w)
        total_time += laptime
        if p1 == p2:
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


# lets u select which lap to pit in, in the UI itself
# index is the default selected val
c1, c2 = st.columns(2)
with c1:
    p1 = st.selectbox("Pit 1:", list(range(0, 61)), index=0)
with c2:
    p2 = st.selectbox("Pit 2:", list(range(0, 61)), index=0)
# pit_lapA = st.selectbox("Pit lap A:", list(range(1, 61)), index=0)
# pit_lapB = st.selectbox("Pit lap B:", list(range(1, 61)), index=0)

t1, ln1, tr1 = race_simulation(p1, p2)
st.write(f"total time:{t1}s")
# t2, ln2, tr2 = race_simulation(pit_lapB)
# pits = []
# time_pits = []
# for p1, p2 in range(1, 61):
#     t, ln, tr = race_simulation(p1, p2)
#     pits.append(p)
#     time_pits.append(t)

# a = min(time_pits)
# c = max(time_pits)
# b = pits[time_pits.index(a)]
# d = pits[time_pits.index(c)]
# st.write(f"Overall best single pit lap: {b} (total {a:.2f} s). ")
# st.write(f"This is {c-a:.2f} s faster than pit at {d}.")


# if t1 > t2:
#     st.write(f"Best: pit at lap {pit_lapB} ({t2} s)")
#     st.write(f"{t1-t2} s faster.")
# else:
#     st.write(f"Best: pit at lap {pit_lapA} ({t1} s)")
#     st.write(f"{t2-t1} s faster.")


# -----GRAPH-------
# data converted into tabular form
# df = pd.DataFrame({
#     'Lap no': ln1,
#     f"Time pit {pit_lapA}": tr1,
#     f"Time pit {pit_lapB}": tr2
# })
# # line graph
# st.line_chart(df.set_index('Lap no'))

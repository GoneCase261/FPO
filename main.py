import streamlit as st
if "tire_wear" not in st.session_state:
    st.session_state.tire_wear = 0
st.title('🏎️ F1 Pit Optimizer v0.1 - Week 1')
lap_no = st.slider('Lap Progress:', 0, 60, 0)

with open('canvas.html', 'r', encoding='utf-8') as c:
    code = c.read()
    code = code.replace('{lap_no}', str(lap_no))

st.components.v1.html(code, height=220)

if 0 < lap_no <= 45:
    if lap_no > 30:
        st.session_state.tire_wear = min(lap_no*2+lap_no-30, 100)
    else:
        st.session_state.tire_wear = min(lap_no*2, 100)
elif lap_no > 45 and lap_no != 60:
    # extra wear added after lap 30
    st.session_state.tire_wear = min(lap_no*2+lap_no-30, 100)
    st.warning("🛞 Tires CRITICAL! Consider Pitting Soon.")
    if st.button('🛑 PIT STOP'):
        st.session_state.tire_wear = 0
        st.success("🔧 Pitted! New tyres fitted, you’re ready to push again!")
elif lap_no == 60:
    st.session_state.tire_wear = min(lap_no*2+lap_no-30, 100)
    if st.button("🏁 Finish Race!"):
        st.balloons()
        st.success("🏆 Race Complete! Great job!")
else:
    pass
st.metric("Tire Wear:", f"{st.session_state.tire_wear}%")


def lap_time(wear):
    base_time = 90
    if 0 <= wear <= 30:
        lt = base_time
    elif 30 < wear <= 70:
        penalty = (wear - 30)*0.1
        lt = base_time+penalty
    else:
        penalty = 4  # 70-30 * 0.1 for penalty at 70
        extra = (wear-70)*0.3
        lt = base_time+penalty+extra
    return lt


st.metric("LAP TIME:", f"{lap_time(st.session_state.tire_wear)} s")

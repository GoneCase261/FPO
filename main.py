import streamlit as st
st.title('🏎️ F1 Pit Optimizer v0.1 - Week 1')
lap_no = st.slider('Lap Progress:', 0, 60, 0)

with open('canvas.html', 'r', encoding='utf-8') as c:
    code = c.read()
    code = code.replace('{lap_no}', str(lap_no))
st.components.v1.html(code, height=220)
if lap_no > 45 and lap_no != 60:
    st.warning("🛞 Tires CRITICAL! Consider Pitting Soon.")
elif lap_no == 60:
    if st.button("🏁 Finish Race!"):
        st.balloons()
        st.success("🏆 Race Complete! Great job!")
else:
    pass

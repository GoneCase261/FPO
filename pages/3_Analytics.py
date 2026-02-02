import streamlit as st
import pandas as pd
import os

st.header("🏆 Strategy Leaderboard")

if os.path.exists('strategies.csv'):
    df = pd.read_csv('strategies.csv')
    st.dataframe(df.sort_values('total_time').head(10))

    col1, col2 = st.columns(2)
    col1.metric("🏁 Best Time", f"{df['total_time'].min():.1f}s")
    col2.metric("📊 Total Strategies", len(df))
else:
    st.info("💾 Save strategies in Lab first!")

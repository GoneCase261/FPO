import streamlit as st
import pandas as pd
import os

st.header("🏁 Track-Specific Strategy Leaderboard")

if os.path.exists('strategies.csv'):
    df = pd.read_csv('strategies.csv')

    # Group by track and show best strategy PER TRACK
    track_leaderboard = {}
    for track in df['track'].unique():
        track_df = df[df['track'] == track]
        best = track_df.loc[track_df['total_time'].idxmin()]
        track_leaderboard[track] = best

    # Display track-by-track winners
    leaderboard_df = pd.DataFrame(track_leaderboard).T
    st.dataframe(leaderboard_df.sort_values('total_time').head(10))

    # Track-specific metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("🏁 Fastest Track", df.groupby(
        'track')['total_time'].min().idxmin())
    col2.metric("📊 Total Tracks", df['track'].nunique())
    col3.metric("🎯 Strategies Tested", len(df))

else:
    st.info("💾 Save strategies in Lab first!")

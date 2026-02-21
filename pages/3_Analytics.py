import streamlit as st
import pandas as pd
import os
import numpy as np

st.header("🏁 Track-Specific Strategy Leaderboard")

if os.path.exists('strategies.csv'):
    df = pd.read_csv('strategies.csv')

    # 🛡️ CLEAN BAD DATA FIRST (NaN, infinite)
    df = df.dropna(subset=['total_time'])
    df = df[np.isfinite(df['total_time'])]

    st.info(f"📊 Loaded {len(df)} CLEAN strategies")

    if len(df) > 0:
        # ✅ SAFE: Group by track and find best
        track_leaderboard = {}
        for track in df['track'].unique():
            track_df = df[df['track'] == track]
            if len(track_df) > 0:
                best_idx = track_df['total_time'].idxmin()
                best = track_df.loc[best_idx]
                track_leaderboard[track] = best

        # Display leaderboard
        if track_leaderboard:
            leaderboard_df = pd.DataFrame(track_leaderboard).T
            st.dataframe(leaderboard_df.sort_values('total_time').head(10))

            # Metrics (SAFE)
            col1, col2, col3 = st.columns(3)
            fastest_track = df.groupby('track')['total_time'].min().idxmin()
            col1.metric("🏁 Fastest Track", fastest_track)
            col2.metric("📊 Total Tracks", df['track'].nunique())
            col3.metric("🎯 Strategies", len(df))
        else:
            st.warning("No valid track data!")
    else:
        st.warning("No valid strategies found!")
else:
    st.info("💾 Save strategies in Strategy Lab first!")

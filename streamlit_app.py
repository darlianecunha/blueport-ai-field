# BluePort AI — Field Dashboard (Streamlit)
# Run:
#   pip install -r requirements_dashboard.txt
#   streamlit run streamlit_app.py
#
# Expects cleaned CSV logs under data/logs/*.csv with columns:
#   timestamp_utc, location, class, confidence, feedback_correct
# Optional: assets/locations.csv with columns: location, lat, lon

import os, glob
import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
from datetime import datetime, timezone

st.set_page_config(page_title="BluePort AI — Field Dashboard", page_icon="🌊", layout="wide")

st.title("🌊 BluePort AI — Field Dashboard")
st.caption("Mobile photo testing → quick KPIs & hotspots")

# --- Load logs ---
def load_logs():
    files = sorted(glob.glob("data/logs/*.csv"))
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            dfs.append(df)
        except Exception as e:
            st.warning(f"Failed to read {f}: {e}")
    if not dfs:
        return pd.DataFrame(columns=["timestamp_utc","location","class","confidence","feedback_correct"])
    df = pd.concat(dfs, ignore_index=True)
    # normalize
    if "timestamp_utc" in df.columns:
        df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], errors="coerce", utc=True)
    else:
        df["timestamp_utc"] = pd.NaT
    if "confidence" in df.columns:
        df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce")
    if "feedback_correct" in df.columns:
        df["feedback_correct"] = pd.to_numeric(df["feedback_correct"], errors="coerce").astype("float")
    return df

df = load_logs()

# sidebar filters
st.sidebar.header("Filters")
if not df.empty:
    min_date = df["timestamp_utc"].min().date() if df["timestamp_utc"].notna().any() else None
    max_date = df["timestamp_utc"].max().date() if df["timestamp_utc"].notna().any() else None
else:
    min_date = max_date = None

date_range = st.sidebar.date_input("Date range", value=(min_date, max_date)) if min_date and max_date else None
classes = sorted(df["class"].dropna().unique().tolist()) if not df.empty else []
class_sel = st.sidebar.multiselect("Classes", classes, default=classes[:5] if len(classes)>5 else classes)

locs = sorted(df["location"].dropna().unique().tolist()) if not df.empty else []
loc_sel = st.sidebar.multiselect("Locations", locs, default=locs)

def apply_filters(df):
    if df.empty: 
        return df
    out = df.copy()
    if date_range and isinstance(date_range, (list, tuple)) and len(date_range)==2 and date_range[0] and date_range[1]:
        start = pd.to_datetime(date_range[0]).tz_localize("UTC")
        end = pd.to_datetime(date_range[1]).tz_localize("UTC") + pd.Timedelta(days=1)
        out = out[(out["timestamp_utc"] >= start) & (out["timestamp_utc"] < end)]
    if class_sel:
        out = out[out["class"].isin(class_sel)]
    if loc_sel:
        out = out[out["location"].isin(loc_sel)]
    return out

df_f = apply_filters(df)

# --- KPIs ---
c1, c2, c3, c4 = st.columns(4)
total = len(df_f)
uniq_locations = df_f["location"].nunique() if not df_f.empty else 0
acc = df_f["feedback_correct"].mean()*100 if "feedback_correct" in df_f.columns and df_f["feedback_correct"].notna().any() else None
avg_conf = df_f["confidence"].mean()*100 if "confidence" in df_f.columns and df_f["confidence"].notna().any() else None

c1.metric("Photos Logged", f"{total}")
c2.metric("Locations", f"{uniq_locations}")
c3.metric("Avg Confidence", f"{avg_conf:.1f}%" if avg_conf is not None else "—")
c4.metric("Accuracy (feedback)", f"{acc:.1f}%" if acc is not None else "—")

st.markdown("---")

# --- Time series ---
if not df_f.empty and df_f["timestamp_utc"].notna().any():
    daily = df_f.set_index("timestamp_utc").groupby(pd.Grouper(freq="D")).size().rename("count").reset_index()
    st.subheader("Daily count")
    st.line_chart(daily.set_index("timestamp_utc"))

# --- Class distribution ---
st.subheader("Class distribution")
if not df_f.empty and df_f["class"].notna().any():
    dist = df_f["class"].value_counts().rename_axis("class").reset_index(name="count")
    st.bar_chart(dist.set_index("class"))
else:
    st.info("No data yet. Add logs in data/logs/.")

# --- Map (if locations.csv exists) ---
st.subheader("Hotspots map")
loc_path = "assets/locations.csv"
if os.path.exists(loc_path):
    loc_df = pd.read_csv(loc_path)
    # normalize
    loc_df["location"] = loc_df["location"].astype(str)
    # join
    if not df_f.empty:
        g = df_f.groupby("location").size().rename("count").reset_index()
        m = loc_df.merge(g, on="location", how="left").fillna({"count":0})
    else:
        m = loc_df.copy()
        m["count"] = 0
    m = m.dropna(subset=["lat","lon"])
    st.map(m.rename(columns={"lat":"latitude","lon":"longitude"}))
    st.caption("Tip: edit assets/locations.csv to add your pier/berth/channel coordinates.")
else:
    st.info("To enable the map, create assets/locations.csv with columns: location, lat, lon")

# --- Raw table preview ---
st.subheader("Raw logs (filtered)")
st.dataframe(df_f.tail(200), use_container_width=True)

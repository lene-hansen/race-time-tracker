import pandas as pd
import streamlit as st
import altair as alt

from utils.db_utils import init_db
from utils.date_utils import convert_date_to_age
from column_names import (
    NAME,
    BIRTH_DATE,
    MEMBERS,
    ID,
    RACETIME,
    RUNNER_ID,
    RACE_DISTANCE,
    RACE_TIME,
    RACE_LOCATION,
)

st.set_page_config(page_title="Personlige tider", page_icon=":material/directions_run:")

# --- Setup
supabase = init_db()

def get_members():
    return supabase.table(MEMBERS).select(ID, NAME, BIRTH_DATE).execute()

def get_racetimes():
    return supabase.table(RACETIME).select(RUNNER_ID, RACE_DISTANCE, RACE_TIME, RACE_LOCATION).execute()

# --- Load data
members = get_members()
racetimes = get_racetimes()

if not members or not members.data:
    st.warning("Ingen løbere fundet.")
    st.stop()

members_df = pd.DataFrame(members.data)
members_df["Alder"] = members_df[BIRTH_DATE].apply(convert_date_to_age)

racetimes_df = pd.DataFrame(racetimes.data)
valid_distances = ["5K", "10K", "Half Marathon", "Marathon"]
racetimes_df = racetimes_df[racetimes_df[RACE_DISTANCE].isin(valid_distances)]

# --- Merge
merged_df = pd.merge(
    racetimes_df,
    members_df[[ID, NAME, "Alder"]],
    left_on=RUNNER_ID,
    right_on=ID,
    how="left",
)

# --- Rename for display
display_df = merged_df.rename(
    columns={
        NAME: "Navn",
        "Alder": "Alder",
        RACE_LOCATION: "Løb",
        RACE_DISTANCE: "Distance",
        RACE_TIME: "Tid",
    }
)[["Navn", "Alder", "Løb", "Distance", "Tid"]]

# --- UI
st.title("Tider per person")

selected_name = st.selectbox("Vælg person", sorted(display_df["Navn"].unique()), index=None)

if selected_name is None:
    st.info("Vælg person i dropdown-menuen for at se tider.")
else:
    runner_df = display_df[display_df["Navn"] == selected_name]
    st.subheader(f"Resultater for {selected_name}")

    distance_order = ["5K", "10K", "Half Marathon", "Marathon"]

    for distance in distance_order:
        distance_df = runner_df[runner_df["Distance"] == distance]
        if distance_df.empty:
            continue

        st.markdown(f"### {distance}")
        st.dataframe(distance_df[["Løb", "Tid"]].sort_values("Tid"), use_container_width=True, hide_index=True)



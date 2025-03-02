import datetime
import streamlit as st

from db_utils import init_connection
from column_names import (
    ID,
    NAME,
    BIRTH_DATE,
    GENDER,
    MEMBERS,
    RACETIME,
    RUNNER_ID,
    RACE_DISTANCE,
    RACE_TIME,
    RACE_DATE,
)
st.subheader("Indtast en ny løbstid")

name_input = st.text_input("Navn", placeholder="Morten Westergaard")
birth_date_input = st.date_input("Fødselsdag", value=datetime.date(2000, 1, 1))
gender_input = st.selectbox("Køn", ["Mand", "Kvinde"])

distance_input = st.selectbox("Løbsdistance", ["5k", "10k", "Half Marathon", "Marathon"])
time_input = st.text_input("Indtast race-tid (HH:MM:SS)", placeholder="00:00:00")
race_date_input = st.date_input("Dato for løb")

if st.button("Indsend tid"):
    # Parse race time
    try:
        race_time = datetime.datetime.strptime(time_input, "%H:%M:%S").time()
    except ValueError:
        st.error("Forkert tidsformat. Indtast venligst tid i HH:MM:SS format.")
        race_time = None

    if race_time:
        supabase = init_connection()

        existing_runner = (
            supabase.table(MEMBERS).select(ID).eq(NAME, name_input).execute()
        )

        if existing_runner.data:
            runner_id = existing_runner.data[0][ID]
        else:
            runner_data = {
                NAME: name_input,
                BIRTH_DATE: str(birth_date_input),
                GENDER: gender_input,
            }
            new_runner = supabase.table(MEMBERS).insert(runner_data).execute()
            runner_id = new_runner.data[0]["id"]

        # Insert or update the race time
        race_data = {
            RUNNER_ID: runner_id,
            RACE_DISTANCE: distance_input,
            RACE_TIME: time_input,
            RACE_DATE: str(race_date_input),
        }
        supabase.table(RACETIME).insert(race_data).execute()

        st.success(f"Race time for {name_input} added successfully!")
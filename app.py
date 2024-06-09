from typing import List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from datetime import datetime, timedelta


 # List of tuples (datetime, amount_in_ml_finished) where `amount_in_ml_finished` is not None if the carton was finished
def get_milks(dt: datetime) -> List[Tuple[datetime, Optional[int]]]:
    return [(datetime(2021, 1, 1), 10), (datetime(2021, 1, 2), 20), (datetime(2021, 1, 3), 30)]

def enter_milk():
    date_milk_was_drunk = st.date_input("Date milk was drunk")
    time_milk_was_drunk = st.time_input("Time milk was drunk")
    datetime_milk_was_drunk = datetime.combine(date_milk_was_drunk, time_milk_was_drunk)

    num_glasses = st.number_input("Number of glasses", min_value=1)
    carton_finished = st.checkbox("Carton finished?")
    if carton_finished:
        ml_in_carton = st.number_input("Amount of milk in carton (mL)", value=1000)
    else:
        ml_in_carton = None


    if st.button("Submit"):
        st.write("Submitted!")
    print((date_milk_was_drunk, carton_finished, ml_in_carton))


st.set_page_config(page_title="Milk Tracker", page_icon="🥛", layout="wide", initial_sidebar_state="collapsed")
st.title("Milk Tracker")

with st.sidebar:
    if st.text_input("Password", type="password") == st.secrets["SECRET_PASSWORD"]:
        enter_milk()
milks = get_milks(datetime.now() - timedelta(days=7))

def format_time(num_seconds: float) -> str:
    if num_seconds < 60:
        return f"{int(num_seconds)} seconds ago"
    elif num_seconds < 3600:
        return f"{int(num_seconds // 60)} minutes ago"
    elif num_seconds < 86400:
        return f"{int(num_seconds // 3600)} hours ago"
    else:
        return f"{int(num_seconds // 86400)} days ago"

columns = st.columns(2)
with columns[0]:
    last_milk = max([x[0] for x in milks])
    time_since_last_milk = datetime.now() - last_milk
    formatted = format_time(time_since_last_milk.total_seconds())
    st.header("Time since last milk")
    st.subheader(formatted)

with columns[1]:
    st.header("Milk consumption in the last month")
    x = [x[0] for x in milks]
    y = np.cumsum([x[1] for x in milks if x[1] is not None]) / 1000
    fig = plt.figure()
    plt.plot(x, y)
    plt.xticks(rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Cumulative milk consumption (L)")
    st.write(fig)

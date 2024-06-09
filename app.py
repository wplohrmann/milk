import json
from google.cloud import firestore

from typing import List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
from datetime import timezone
import arrow

@st.cache_resource
def get_firestore_client():
    service_account = json.loads(st.secrets["SERVICE_ACCOUNT"])
    return firestore.Client.from_service_account_info(service_account)


 # List of tuples (datetime, amount_in_ml_finished) where `amount_in_ml_finished` is not None if the carton was finished
def get_milks(dt: datetime) -> List[Tuple[datetime, Optional[int]]]:
    client = get_firestore_client()
    documents = client.collection('milks').where('datetime', '>', dt).get()
    milks = []
    for doc in documents:
        doc_dict=  doc.to_dict()
        milks.append((doc_dict["datetime"], doc_dict["ml_in_carton"]))
    return milks

def enter_milk():
    date_milk_was_drunk = st.date_input("Date milk was drunk")
    time_milk_was_drunk = st.time_input("Time milk was drunk")
    datetime_milk_was_drunk = datetime.combine(date_milk_was_drunk, time_milk_was_drunk, tzinfo=arrow.now().tzinfo)

    carton_finished = st.checkbox("Carton finished?")
    if carton_finished:
        ml_in_carton = st.number_input("Amount of milk in carton (mL)", value=1000)
    else:
        ml_in_carton = None


    if st.button("Submit"):
        client = get_firestore_client()
        client.collection('milks').add({
            "datetime": datetime_milk_was_drunk,
            "ml_in_carton": ml_in_carton
        })
        st.write("Submitted!")


st.set_page_config(page_title="Milk Tracker", page_icon="🥛", layout="wide", initial_sidebar_state="collapsed")
st.title("Milk Tracker")

with st.sidebar:
    if st.text_input("Password", type="password") == st.secrets["SECRET_PASSWORD"]:
        enter_milk()
t0  = (arrow.now() - timedelta(days=31)).datetime
milks = get_milks(t0)

if len(milks) == 0:
    st.write("No milk data found in the last month 😢")
    st.stop()

def format_time(num_seconds: float) -> str:
    if num_seconds < 60:
        return f"{int(num_seconds)} seconds ago"
    elif num_seconds < 3600:
        return f"{int(num_seconds // 60)} minutes ago"
    elif num_seconds < 86400:
        return f"{int(num_seconds // 3600)} hours, {int((num_seconds % 3600) // 60)} minutes ago"
    else:
        return f"{int(num_seconds // 86400)} days ago"
columns = st.columns(2)
with columns[0]:
    last_milk = max([x[0] for x in milks])
    time_since_last_milk = arrow.now() - last_milk
    formatted = format_time(time_since_last_milk.total_seconds())
    st.header("Time since last milk")
    st.subheader(formatted)

with columns[1]:
    st.header("Milk consumption in the last month")
    x = [x[0] for x in milks]
    x.insert(0, t0)
    y_l = np.cumsum([x[1] if x[1] else 0 for x in milks]) / 1000
    y_l = np.insert(y_l, 0, 0)
    y_glasses = np.cumsum([1 for x in milks])
    y_glasses = np.insert(y_glasses, 0, 0)
    fig = plt.figure()
    plt.plot(x, y_l, "-o", label="Litres consumed")
    plt.plot(x, y_glasses, "-o", label="Glasses consumed")
    plt.xticks(rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Cumulative milk consumption (L)")
    st.write(fig)

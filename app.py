import json
from google.cloud import firestore

from typing import List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, tzinfo
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
    time_milk_was_drunk = st.time_input("Time milk was drunk", value=arrow.now(tz="Europe/London").time())
    datetime_milk_was_drunk = datetime.combine(date_milk_was_drunk, time_milk_was_drunk, tzinfo=tzinfo("Europe/London"))

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
    x = [t0]
    y_l = [0]
    y_glasses = [0]
    for milk in milks:
        x.append(milk[0] - timedelta(seconds=1))
        x.append(milk[0])
        y_l.append(y_l[-1])
        y_l.append(y_l[-1] + (milk[1] / 1000 if milk[1] is not None else 0))
        y_glasses.append(y_glasses[-1])
        y_glasses.append(y_glasses[-1] + 1)

    fig, axes = plt.subplots(2, 1, sharex=True)
    axes[0].plot(x, y_glasses, label="Glasses consumed")
    axes[1].plot(x, y_l, label="Litres consumed")
    axes[0].set_xlabel("Date")
    axes[0].set_ylabel("Glasses consumed")
    axes[1].set_ylabel("Litres consumed")
    plt.xticks(rotation=45)
    axes[0].legend()
    axes[1].legend()
    plt.legend()
    st.write(fig)

milk_df = pd.DataFrame([{"Datetime": x[0], "Amount (if carton finished) / mL": x[1] or ""} for x in milks])
st.subheader("Raw milk data (No UHT)")
st.dataframe(milk_df, use_container_width=True, hide_index=True)

""""""

import streamlit as st
import pandas as pd
from streamlit_extras.switch_page_button import switch_page
from io import StringIO


if "go" not in st.session_state:
    st.session_state["go"] = False

st.title("17lands Event History Analysis")

st.markdown(
    """
    Please paste your 17lands event history data in the text box below, and press submit.
    The application will attempt to parse the data. **Note:** this application does not save
    data between sessions.
"""
)
# TODO: include an image with the "copyable" box checked

txt = st.text_area(
    label="Event History, text input", placeholder="Paste your event history"
)
go = st.button("Submit")
# demo = st.button("Demo")
demo = False

if go:
    try:
        dat = pd.read_csv(StringIO(txt), delimiter="\t")
        dat = dat[~(dat.Date.str.contains("Deck") | dat.Date.str.contains("Details"))]
        dat.Date = pd.to_datetime(dat.Date)

        dat[["W", "L"]] = dat["W/L"].str.split(" - ", expand=True)
        dat.W = dat.W.astype(int)
        dat.L = dat.L.astype(int)
        dat = dat[["Date", "Set", "Trophy", "Colors", "W", "L", "Format"]]

    except pd.errors.EmptyDataError as err:
        st.error(err)
        st.stop()

    except AttributeError as err:
        st.error(err)
        st.warning(
            "It might be that your data is missing column names, or you've passed data in"
            " an unexpected format."
        )
        st.stop()

    except Exception as err:
        st.error(err)
        st.warning(
            'Unable to parse incoming data, please use the "copyable" option from the '
            "17lands event history."
        )
        st.stop()

    st.session_state["dat"] = dat
    st.session_state["go"] = True
    switch_page("Event_History")

if demo:
    dat = pd.read_csv("./app/util/sample_data.tsv", delimiter="\t")
    dat = dat[~(dat.Date.str.contains("Deck") | dat.Date.str.contains("Details"))]
    dat.Date = pd.to_datetime(dat.Date)

    dat[["W", "L"]] = dat["W/L"].str.split(" - ", expand=True)
    dat.W = dat.W.astype(int)
    dat.L = dat.L.astype(int)
    dat = dat[["Date", "Set", "Trophy", "Colors", "W", "L", "Format"]]

    st.session_state["dat"] = dat
    st.session_state["go"] = True
    switch_page("Event_History")

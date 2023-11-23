"""Compute statistics within a given set"""

import streamlit as st
import pandas as pd
import altair as alt
from streamlit_extras.switch_page_button import switch_page

if st.session_state.get("go") is None:
    st.session_state["go"] = False

if not st.session_state["go"]:
    switch_page("Upload")

if st.session_state.get("dat") is None:
    switch_page("Upload")

dat = st.session_state.get("dat")

#### Sidebar/Filters ####

st.sidebar.markdown("### Format Performance")
selected_set = st.sidebar.selectbox(label="Set", options=dat.Set.unique())

st.sidebar.markdown("### Color Performance")
selected_fmt = st.sidebar.selectbox(
    label="Format",
    options=dat[dat.Set == selected_set].Format.value_counts().index.to_list(),
)

#### Content ####

st.title("Set Statistics")

st.markdown("## Events by Set")

by_release_dt = st.toggle(label="Sort by set release date")

if by_release_dt:
    dts = dat.groupby("Set").Date.min().reset_index()
    dts = dts.merge(dat[["Set"]], how="left", on="Set")
    counts = dts.groupby(["Set", "Date"]).value_counts().reset_index()
    counts = counts.sort_values("Date")

    st.altair_chart(
        alt.Chart(counts)
        .mark_bar()
        .encode(
            x=alt.X("Set:N", sort=counts.Set.to_list()),
            y="count:Q",
            # order="Date:T"
        ),
        use_container_width=True,
    )

else:
    counts = pd.DataFrame(dat.value_counts("Set")).reset_index()

    st.altair_chart(
        alt.Chart(counts).mark_bar().encode(x=alt.X("Set", sort=None), y="count"),
        use_container_width=True,
    )

st.markdown(f"## {selected_set}, Format Performance")

event_perf = dat[dat.Set == selected_set].groupby("Format")[["W", "L"]].sum()
event_perf["Total"] = event_perf.W + event_perf.L
event_overall = pd.DataFrame(event_perf.sum().to_dict(), index=["Overall"])

event_perf = pd.concat([event_overall, event_perf])
event_perf["MW%"] = round(event_perf.W / event_perf.Total * 100, 2)
event_perf["Match Share (%)"] = round(
    event_perf.Total / event_perf.Total.max() * 100, 2
)
event_perf = event_perf[["Total", "Match Share (%)", "W", "L", "MW%"]]
event_perf = event_perf.rename({"Total": "Total Matches"}, axis="columns")
event_perf = event_perf.sort_values("Total Matches", ascending=False)

st.write(event_perf)

#### Color Performance (by set) ####

st.markdown(f"## {selected_set}, Color Performance: {selected_fmt}")

color_perf = (
    dat[(dat.Set == selected_set) & (dat.Format == selected_fmt)]
    .groupby(["Colors"])[["W", "L"]]
    .sum()
)
color_perf["Total"] = color_perf.W + color_perf.L
color_overall = pd.DataFrame(color_perf.sum().to_dict(), index=["Overall"])

color_perf = pd.concat([color_overall, color_perf])

color_perf["MW%"] = round(color_perf.W / color_perf.Total * 100, 2)
color_perf["Match Share (%)"] = round(
    color_perf.Total / color_perf.Total.max() * 100, 2
)
color_perf = color_perf[["Total", "Match Share (%)", "W", "L", "MW%"]]
color_perf = color_perf.rename({"Total": "Total Matches"}, axis="columns")
color_perf = color_perf.sort_values(["Total Matches", "MW%"], ascending=False)
st.write(color_perf)

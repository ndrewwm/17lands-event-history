import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from datetime import datetime


if "go" not in st.session_state:
    st.session_state["go"] = False

if not st.session_state["go"]:
    switch_page("Upload")

if st.session_state.get("dat") is None:
    switch_page("Upload")

dat = st.session_state.get("dat")

#### Sidebar & Filtering ####

# FIXME: may not be possible currently 😭
# Could ask another service to run the code on the app's behalf?
# st.sidebar.text_input(label="Profile Link", placeholder="17lands profile URL")
# st.sidebar.button(label="Go")

st.sidebar.markdown("# Filters")

s_col1, s_col2 = st.sidebar.columns(2)

mindt = s_col1.date_input(
    label="Min. date",
    value=dat.Date.min(),
    min_value=dat.Date.min(),
    max_value=dat.Date.max(),
)
maxdt = s_col2.date_input(
    label="Max. date", value=dat.Date.max(), min_value=mindt, max_value=dat.Date.max()
)

mtgset = st.sidebar.multiselect("Set", dat.Set.unique())
colors = st.sidebar.multiselect("Colors", dat.Colors.unique())
mtgfmt = st.sidebar.multiselect("Format", dat.Format.unique())

f = dat.copy()
f = f[(mindt <= f.Date.dt.date) & (f.Date.dt.date <= maxdt)]

if mtgset:
    f = f[f.Set.isin(mtgset)]

if colors:
    f = f[f.Colors.isin(colors)]

if mtgfmt:
    f = f[f.Format.isin(mtgfmt)]

# Do we have data from last year?
cyear = datetime.today().year
lyear = cyear - 1
has_lyear = lyear in f.Date.dt.year.to_list()

#### Results ####


def overall_metrics(f: pd.DataFrame) -> dict:
    """Calculate overall match metrics"""

    return {
        "total_matches": sum(f.W + f.L),
        "total_w": sum(f.W),
        "total_l": sum(f.L),
        "win_pct": round(sum(f.W) / sum(f.W + f.L) * 100, 1),
        "total_e": len(f),
        "total_t": sum(f.Trophy == "x"),
    }


plot_df = f.copy()
plot_df = plot_df[["Date", "W", "L"]].sort_values(by="Date", ascending=True)
plot_df["cum_w"] = plot_df.W.cumsum()
plot_df["cum_t"] = (plot_df.W + plot_df.L).cumsum()
plot_df["cum_p"] = plot_df.cum_w / plot_df.cum_t

#### Content ####

st.title("17lands Event History")

st.markdown("## Overall summary")

fmet = overall_metrics(f)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Match Record", value=f"{fmet['total_w']} - {fmet['total_l']}")
col2.metric("Win %", value=f"{fmet['win_pct']}%")
col3.metric("Events", value=f"{fmet['total_e']}")
col4.metric(
    "Trophies (trophy rate)",
    value=f"{fmet['total_t']} ({round(fmet['total_t'] / fmet['total_e'] * 100, 1)}%)",
)

if has_lyear:
    f_cyr = f[f.Date.dt.year == cyear]
    f_lyr = f[f.Date.dt.year == lyear]

    fmet_cyr = overall_metrics(f_cyr)
    fmet_lyr = overall_metrics(f_lyr)

    w_diff = fmet_cyr["total_w"] - fmet_lyr["total_w"]
    l_diff = fmet_cyr["total_l"] - fmet_lyr["total_l"]
    e_diff = fmet_cyr["total_e"] - fmet_lyr["total_e"]
    t_diff = fmet_cyr["total_t"] - fmet_lyr["total_t"]
    mw_diff = round(fmet_cyr["win_pct"] - fmet_lyr["win_pct"], 1)

    st.markdown("## Current year")
    st.markdown(
        f"({cyear} *vs.* {lyear}) Metric deltas reflect the difference between current values "
        "and the prior year's."
    )

    cyr1, cyr2, cyr3, cyr4 = st.columns(4)
    cyr1.metric(
        "Match Record",
        value=f"{fmet_cyr['total_w']} - {fmet_cyr['total_l']}",
        delta=f"{w_diff} - {l_diff}",
    )
    cyr2.metric("Win %", value=f"{fmet_cyr['win_pct']}%", delta=mw_diff)
    cyr3.metric("Events", value=fmet_cyr["total_e"], delta=e_diff)
    cyr4.metric(
        "Trophies (trophy rate)",
        value=f"{fmet_cyr['total_t']} ({round(fmet_cyr['total_t'] / fmet_cyr['total_e'] * 100, 1)}%)",
        delta=t_diff,
    )

st.markdown("## Performance over time")
st.line_chart(data=plot_df, x="Date", y="cum_p")

st.markdown("## Event History")

st.write(f)

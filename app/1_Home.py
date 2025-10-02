# app/1_Home.py
import streamlit as st
import requests
import pandas as pd
import altair as alt
from utils.regions import REGIONS, states_for_regions


API = "http://api_service:8000"

# ================= Helper Function =================
def fetch_json(url, **kwargs):
    """Fetch JSON from API with basic error handling."""
    r = requests.get(url, timeout=10, **kwargs)
    if not r.ok:
        st.error(f"{url} → {r.status_code}")
        st.code(r.text[:800])  # show first ~800 chars of error page/body
        st.stop()
    return r.json()

# ================= Main Page =================

st.title("FAA Kit Aircraft Database")

st.subheader("View the Data Source")
if st.link_button(
    "FAA Website",
    "https://www.faa.gov/licenses_certificates/aircraft_certification/aircraft_registry/releasable_aircraft_download",
    type="primary",
):
    st.write(" ")
st.markdown("----")

# ================= Region Selector =================
st.subheader("Dataset Stats")
st.markdown("#### Select Region(s)")

REGIONS = ["All", "North", "South", "East", "West"]

# --- initialize toggle state once ---
if "region_toggles" not in st.session_state:
    st.session_state.region_toggles = {
        "All": True, "North": False, "South": False, "East": False, "West": False
    }

# --- render toggles in a single row ---
cols = st.columns(len(REGIONS))
for i, name in enumerate(REGIONS):
    st.session_state.region_toggles[name] = cols[i].toggle(
        name,
        value=st.session_state.region_toggles[name],
        key=f"toggle_{name.lower()}",
        help="Select one or more regions. 'All' turns off automatically when any specific region is chosen."
    )

# --- normalization logic ---
tog = st.session_state.region_toggles

# Case 1: If 'All' is on, turn everything else off
if tog["All"]:
    tog["North"] = tog["South"] = tog["East"] = tog["West"] = False

# Case 2: If all four regions are selected, collapse to 'All'
elif all([tog["North"], tog["South"], tog["East"], tog["West"]]):
    tog["All"] = True
    tog["North"] = tog["South"] = tog["East"] = tog["West"] = False

# Case 3: If any region is selected, turn 'All' off
elif any([tog["North"], tog["South"], tog["East"], tog["West"]]):
    tog["All"] = False

# Case 4: If nothing is selected, turn 'All' back on
elif not any([tog["North"], tog["South"], tog["East"], tog["West"], tog["All"]]):
    tog["All"] = True

# --- derive selected regions ---
selected_regions = ["All"] if tog["All"] else [
    r for r in ["North", "South", "East", "West"] if tog[r]
]

st.caption(f"**Selected Regions:** {', '.join(selected_regions)}")

# --- convert region → states ---
states_list = states_for_regions(selected_regions)
params_for_agg = {}
if states_list:  # empty means All
    params_for_agg["states"] = ",".join(states_list)


# || ================= Manufacturer Charts ================= ||
by_kitmfg = fetch_json(f"{API}/kits/agg/by_kitmfg", params=params_for_agg)
st.subheader("Top Kit Aircraft Manufacturers by Count")

df_mfg = (
    pd.DataFrame(by_kitmfg)
      .rename(columns={"kitmfg": "Manufacturer", "count": "Count"})
      .sort_values("Count", ascending=False)
      .head(10)
)
# Identify top manufacturer
top_mfg = df_mfg.iloc[0]["Manufacturer"]

base = (
    alt.Chart(df_mfg)
      .encode(
          x=alt.X("Manufacturer:N", sort="-y", title="Manufacturer"),
          y=alt.Y("Count:Q", title="Aircraft Count"),
          color=alt.condition(
              alt.datum.Manufacturer == top_mfg,
              alt.value("#CCFF00"),      # highlight top
              alt.value("#87CEFA")       # default blue
          )
      )
      .properties(height=420)
)

bars = base.mark_bar()

# Chart Text
labels = base.mark_text(
    baseline="top",
    dy=-14,
    fontWeight="bold",
    fontSize=12,
    color="#B8CDFF"
).encode(
    text=alt.Text("Count:Q", format=",")
)

st.altair_chart(bars + labels, use_container_width=True)

# || ================= Donut: Vans vs Others ================= ||
VANS_NAME = "VANS AIRCRAFT INC"

total_mfg = sum(d["count"] for d in by_kitmfg if d.get("kitmfg"))
vans_count = next(
    (d["count"] for d in by_kitmfg if (d.get("kitmfg") or "").strip().upper() == VANS_NAME),
    0,
)
other_count = max(total_mfg - vans_count, 0)

st.caption("Proportion of Vans Aircraft to all other manufacturers.")
df_donut = pd.DataFrame(
    {
        "Group": ["VANS AIRCRAFT INC", "Other Manufacturers"],
        "Count": [vans_count, other_count],
    }
)
df_donut["Share"] = df_donut["Count"] / df_donut["Count"].sum() if df_donut["Count"].sum() else 0

# custom color scale — highlight Vans Aircraft in orange (#FF5F15)
color_scale = alt.Scale(
    domain=["VANS AIRCRAFT INC", "Other Manufacturers"],
    range=["#FF5F15", "#87CEFA"]  # orange for Vans, light blue for others
)

donut = (
    alt.Chart(df_donut)
    .mark_arc(innerRadius=70)
    .encode(
        theta=alt.Theta("Count:Q", stack=True),
        color=alt.Color("Group:N", scale=color_scale, legend=alt.Legend(title="")),
        tooltip=[
            alt.Tooltip("Group:N"),
            alt.Tooltip("Count:Q"),
            alt.Tooltip("Share:Q", format=".1%")
        ],
    )
    .properties(height=260)
)

# Center text showing Vans % in same orange
center_text = (
    alt.Chart(pd.DataFrame({"label": [f"{(df_donut.loc[0,'Share'] if total_mfg else 0):.1%}"]}))
    .mark_text(
        fontSize=32,
        fontWeight="bold",
        color="#FF5F15"   # match Vans segment
    )
    .encode(text="label:N")
)

st.altair_chart(donut + center_text, use_container_width=True)

st.markdown("----")
# || ================= State chart (horizontal, top 10) ================= ||
by_state = fetch_json(f"{API}/kits/agg/by_state", params=params_for_agg)

# Build dataframe, drop blanks
df_states = (
    pd.DataFrame(by_state)
      .rename(columns={"state": "State", "count": "Count"})
)
df_states = df_states[df_states["State"].notna() & (df_states["State"] != "")]

# Enforce region filter on the client too (belt & suspenders)
if states_list:
    df_states = df_states[df_states["State"].isin(states_list)]

# Top-N within the selected region(s)
TOP_N = 10
df_top = df_states.sort_values("Count", ascending=False).head(TOP_N)

region_label = ", ".join(selected_regions) if selected_regions else "All"
st.subheader(f"Top {min(TOP_N, len(df_states))} States by Aircraft Count — {region_label}")

if df_top.empty:
    st.info("No state-level data available for the selected region(s).")
else:
    # mark the row with the maximum count
    top_state = df_top.loc[df_top["Count"].idxmax(), "State"]
    df_top = df_top.assign(Highlight=df_top["State"].eq(top_state))

    base = alt.Chart(df_top).encode(
        x=alt.X("Count:Q", title="Aircraft Count"),
        y=alt.Y("State:N", sort="-x", title="State"),
        tooltip=["State", "Count"]
    )

    # color the max state #40FF15, others a neutral bar color
    bars = base.mark_bar().encode(
        color=alt.Color(
            "Highlight:N",
            scale=alt.Scale(domain=[True, False], range=["#40FF15", "#87CEFA"]),
            legend=None
        )
    )

    # value labels at the end of each bar
    labels = base.mark_text(
        align="left",
        baseline="middle",
        dx=5,
        fontSize=14,
        fontWeight="bold",
        color="#B8CDFF"
    ).encode(
        text=alt.Text("Count:Q", format=",")
    )

    chart = (bars + labels).properties(
        height=28 * len(df_top) + 20
    )
    st.altair_chart(chart, use_container_width=True)

# || ================= State KPI ================= ||

# City count (API returns either {"city_count": N} or {"count": N})
city_payload = fetch_json(f"{API}/kits/metrics/city_count", params=params_for_agg)
city_count = city_payload.get("city_count", city_payload.get("count", 0))

# Engine types represented (count distinct engcat that are non-empty)
eng_agg = fetch_json(f"{API}/kits/agg/by_engcat", params=params_for_agg)
engine_types_count = len([d for d in eng_agg if (d.get("engcat") or "").strip()])

# Optional: light “card” styling to match your existing look
st.markdown("""
<style>
.metric-card{
  border:1px solid rgba(255,255,255,.15);
  padding:1rem 1.25rem;
  border-radius:0.75rem;
  background:rgba(255,255,255,.03);
}
.metric-label{
  color:rgba(255,255,255,.75);
  font-size:.95rem;
  margin-bottom:.25rem;
}
.metric-value{
  font-size:2rem;
  font-weight:700;
  line-height:1.2;
}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"<div class='metric-card'>"
        f"  <div class='metric-label'>Number of cities represented</div>"
        f"  <div class='metric-value'>{city_count:,}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"<div class='metric-card'>"
        f"  <div class='metric-label'>Engine types represented</div>"
        f"  <div class='metric-value'>{engine_types_count:,}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.divider()
# || ================= Engine Categories ================= ||
by_engcat = fetch_json(f"{API}/kits/agg/by_engcat", params=params_for_agg)

# Build dataframe
df_eng = (
    pd.DataFrame(by_engcat)
      .rename(columns={"engcat": "Engine Type", "count": "Count"})
)
df_eng = df_eng[df_eng["Engine Type"].notna() & (df_eng["Engine Type"] != "")]

# Sort and identify top engine type
df_eng = df_eng.sort_values("Count", ascending=False)
top_engine = df_eng.iloc[0]["Engine Type"]

st.subheader("Aircraft Count by Engine Type")

base = alt.Chart(df_eng).encode(
    x=alt.X("Engine Type:N", sort="-y", title="Engine Type"),
    y=alt.Y("Count:Q", title="Aircraft Count"),
    tooltip=["Engine Type", "Count"]
)

# Highlight top bar
bars = base.mark_bar().encode(
    color=alt.condition(
        alt.datum["Engine Type"] == top_engine,
        alt.value("#15FFD4"),   # top = teal-green highlight
        alt.value("#87CEFA")    # default = light blue
    )
)

# Add text labels at the top of bars
labels = base.mark_text(
    baseline="top",
    dy=-14,
    fontWeight="bold",
    fontSize=14,
    color="#B8CDFF"
).encode(
    text=alt.Text("Count:Q", format=",")
)

st.altair_chart(bars + labels, use_container_width=True)


# || ================= Made In Texas tagline ================= ||
st.divider()
st.markdown("<p style='text-align:center; font-weight:500;'>Made in Texas 🇨🇱</p>", unsafe_allow_html=True)
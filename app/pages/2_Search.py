# app/pages/2_Search.py
import streamlit as st
import pandas as pd
import requests

from utils.regions import REGIONS, states_for_regions  # REGIONS = ["All","North","South","East","West"]

API = "http://api_service:8000"

st.title("Search")

# <<|| ======================= Full page reset ======================= ||>>
def reset_search_state():
    # Region toggles & pagination
    st.session_state.region_toggles = {"All": True, "North": False, "South": False, "East": False, "West": False}
    st.session_state.page_num = 1

    # Sidebar widgets
    for k in [
        "search_states",       # multiselect
        "search_kitmfg",       # kit manufacturer selectbox
        "search_kitmdl",       # model selectbox
        "search_page_size",    # page size slider
        "search_sort_col",     # sort selectbox
        "search_sort_dir",     # ascending toggle
    ]:
        st.session_state.pop(k, None)

    # The individual toggle widget keys
    for k in ["search_toggle_all","search_toggle_north","search_toggle_south","search_toggle_east","search_toggle_west"]:
        st.session_state.pop(k, None)

    st.rerun()

# Header text only — no top reset button
st.caption("Use filters in the sidebar to narrow results.")

# <<|| ======================= Helpers ======================= ||>>
def fetch_json(url, **kwargs):
    r = requests.get(url, timeout=15, **kwargs)
    if not r.ok:
        st.error(f"{url} → {r.status_code}")
        st.code(r.text[:800])
        st.stop()
    return r.json()

def normalize_region_toggles():
    """Keep 'All' logic consistent with Home."""
    tog = st.session_state.region_toggles
    if tog["All"]:
        tog["North"] = tog["South"] = tog["East"] = tog["West"] = False
    elif all([tog["North"], tog["South"], tog["East"], tog["West"]]):
        tog["All"] = True
        tog["North"] = tog["South"] = tog["East"] = tog["West"] = False
    elif any([tog["North"], tog["South"], tog["East"], tog["West"]]):
        tog["All"] = False
    elif not any([tog["All"], tog["North"], tog["South"], tog["East"], tog["West"]]):
        tog["All"] = True

def current_regions():
    tog = st.session_state.region_toggles
    return ["All"] if tog["All"] else [r for r in ["North","South","East","West"] if tog[r]]

def build_params(page_size, page_num, kitmfg, kitmdl, states_csv):
    params = {
        "limit": page_size,
        "offset": (page_num - 1) * page_size,
    }
    if kitmfg: params["kitmfg"] = kitmfg
    if kitmdl: params["kitmdl"] = kitmdl
    if states_csv: params["states"] = states_csv
    return params

# ---------- state ----------
if "region_toggles" not in st.session_state:
    st.session_state.region_toggles = {"All": True, "North": False, "South": False, "East": False, "West": False}

if "page_num" not in st.session_state:
    st.session_state.page_num = 1

# ---------- sidebar filters ----------
with st.sidebar:
    st.header("Filters")

    # Region toggles
    st.caption("Scope by region(s)")
    cols = st.columns(len(REGIONS))
    for i, name in enumerate(REGIONS):
        st.session_state.region_toggles[name] = cols[i].toggle(
            name,
            value=st.session_state.region_toggles[name],
            key=f"search_toggle_{name.lower()}",   # <-- key added
        )
    normalize_region_toggles()
    selected_regions = current_regions()
    st.caption(f"Selected Regions: {', '.join(selected_regions)}")

    # Region → states CSV (optional)
    states_list = states_for_regions(selected_regions)
    states_csv = ",".join(states_list) if states_list else ""

    # Extra state picker (refines the region)
    all_states = fetch_json(f"{API}/kits/filters/states")
    picked_states = st.multiselect("States (optional)", options=sorted(all_states), key="search_states")
    if picked_states:
        states_csv = ",".join(picked_states)  # explicit selection wins

    st.divider()

    # Kit manufacturer + dependent model
    kitmfgs = fetch_json(f"{API}/kits/filters/kitmfgs")
    kitmfg = st.selectbox("Kit Manufacturer", [""] + kitmfgs, key="search_kitmfg")

    if kitmfg:
        models = fetch_json(f"{API}/kits/filters/kitmdls", params={"kitmfg": kitmfg})
        kitmdl = st.selectbox("Model", [""] + (models if isinstance(models, list) else []), key="search_kitmdl")
    else:
        kitmdl = ""
        st.selectbox("Model", [""], disabled=True, key="search_kitmdl")

    st.divider()

    # --- Page size + reset buttons ---
    page_size = st.slider(
        "Rows per page",
        10,
        2000,
        50,
        step=10,
        key="search_page_size"
    )

# Add Reset Pagination + Full Reset buttons side-by-side
st.divider()
if st.button("🔄 Full Reset", type="primary", use_container_width=True, key="search_full_reset_bottom"):
    reset_search_state()
st.divider()

# ---------- results header ----------
left, right = st.columns([1,1])
with left:
    st.subheader("Results")

with right:
    # pagination buttons
    c1, c2, c3 = st.columns([1,1,2])
    if c1.button("◀ Prev", use_container_width=True) and st.session_state.page_num > 1:
        st.session_state.page_num -= 1
    c2.button("Next ▶", use_container_width=True, on_click=lambda: st.session_state.update(page_num=st.session_state.page_num + 1))
    c3.metric("Page", st.session_state.page_num)

# ---------- fetch & render ----------
params = build_params(page_size, st.session_state.page_num, kitmfg, kitmdl, states_csv)
rows = fetch_json(f"{API}/kits", params=params)

df = pd.DataFrame(rows)

# Client-side sort (optional; avoids extra API work)
sort_col = st.selectbox(
    "Sort by",
    ([""] + list(df.columns)) if not df.empty else [""],
    key="search_sort_col"
)
if sort_col:
    asc = st.toggle("Ascending", value=False, key="search_sort_dir")
    df = df.sort_values(sort_col, ascending=asc)
# Download current page
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV (this page)", csv, file_name="kits_page.csv", mime="text/csv")

# Show table
st.caption(f"Rows on this page: {len(df)}")
st.dataframe(df, use_container_width=True, height=520)

# ---------- notes ----------
st.caption(
    "Tip: Region toggles build a state filter for the API. "
    "Use the sidebar **States** picker to narrow further or override the region’s state list."
)
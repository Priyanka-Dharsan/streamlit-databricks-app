import time
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Sales Explorer", page_icon="📊", layout="wide")


# ---------- 1. CACHE: slow data load runs only once ----------
@st.cache_data
def load_data() -> pd.DataFrame:
    time.sleep(2)  # fake slow query
    rng = np.random.default_rng(42)
    dates = pd.date_range("2026-01-01", "2026-10-31", freq="D")
    rows = []
    for d in dates:
        for region in ["North", "South", "East", "West"]:
            for product in ["Laptop", "Phone", "Tablet"]:
                rows.append({
                    "date": d,
                    "region": region,
                    "product": product,
                    "units": int(rng.integers(1, 50)),
                    "price": float(rng.integers(200, 1200)),
                })
    df = pd.DataFrame(rows)
    df["revenue"] = df["units"] * df["price"]
    return df


with st.spinner("Loading data (only slow the first time)..."):
    df = load_data()

# ---------- 2. SESSION STATE ----------
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "run_count" not in st.session_state:
    st.session_state.run_count = 0
st.session_state.run_count += 1

st.title("📊 Sales Explorer (mock data)")

# ---------- 3. SIDEBAR (widgets) ----------
st.sidebar.header("Filters")
regions = st.sidebar.multiselect(
    "Region",
    ["North", "South", "East", "West"],
    default=["North", "South", "East", "West"],
)
product = st.sidebar.selectbox("Product", ["All", "Laptop", "Phone", "Tablet"])
min_units = st.sidebar.slider("Minimum units sold", 0, 50, 10)
show_details = st.sidebar.checkbox("Show details box", value=True)
st.sidebar.caption(f"Script has rerun {st.session_state.run_count} times")

# ---------- 4. FILTER THE DATA ----------
filtered = df[df["region"].isin(regions)]
if product != "All":
    filtered = filtered[filtered["product"] == product]
filtered = filtered[filtered["units"] >= min_units]

# ---------- 5. COLUMNS: KPI cards ----------
c1, c2, c3 = st.columns(3)
c1.metric("Total revenue", f"${filtered['revenue'].sum():,.0f}")
c2.metric("Units sold", f"{filtered['units'].sum():,}")
c3.metric("Rows", f"{len(filtered):,}")

st.divider()

# ---------- 6. COLUMNS with different widths ----------
left, right = st.columns([4, 1])

with left:
    st.subheader("Left side (wide)")
    st.write("Selected regions:", regions)

with right:
    st.subheader("Right side (narrow)")
    st.write("Product:", product)

# ---------- 7. TABS ----------
tab_chart, tab_table, tab_fav = st.tabs(["Chart", "Table", "Favorites"])

with tab_chart:
    monthly = (
        filtered.set_index("date")
        .groupby([pd.Grouper(freq="MS"), "region"])["revenue"]
        .sum()
        .unstack(fill_value=0)
    )
    st.line_chart(monthly)

with tab_table:
    st.dataframe(filtered.head(200), width="stretch")

with tab_fav:
    choice = st.selectbox("Pick a region to favorite", ["North", "South", "East", "West"])

    if st.button("⭐ Add to favorites"):
        if choice not in st.session_state.favorites:
            st.session_state.favorites.append(choice)

    st.write("Your favorites:", st.session_state.favorites or "none yet")

    if st.button("Clear favorites"):
        st.session_state.favorites = []
        st.rerun()

# ---------- 8. EXPANDER ----------
if show_details:
    with st.expander("Click to see details"):
        st.write("An expander hides extra information until the user opens it.")
        st.write("It keeps the page clean.")
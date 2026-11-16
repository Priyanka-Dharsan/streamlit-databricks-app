import streamlit as st
import data

st.set_page_config(page_title="IT Asset Tracker v0.1", page_icon="💻", layout="wide")
st.title("💻 IT Asset Tracker v0.1")

if not data.WAREHOUSE_ID:
    st.error("DATABRICKS_WAREHOUSE_ID is not set. Check the app resource and app.yaml.")
    st.stop()

st.sidebar.header("Filters")
asset_type = st.sidebar.selectbox("Asset type", ["All", "Laptop", "Monitor", "Phone"])
status = st.sidebar.selectbox("Status", ["All", "Available", "Assigned", "Repair", "Retired"])
row_limit = st.sidebar.slider("Max rows", 10, 500, 100, 10)
if st.sidebar.button("Refresh data"):
    st.cache_data.clear()
    st.rerun()

try:
    assets_df = data.list_assets(asset_type, status, row_limit)
    holders_df = data.current_holders(asset_type, row_limit)
    dept_df = data.assets_by_department()
    recover_df = data.inactive_holders()
except Exception as e:
    st.error(f"Query failed: {e}")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Assets shown", len(assets_df))
c2.metric("Currently held", len(holders_df))
c3.metric("Departments", len(dept_df))
c4.metric("To recover", len(recover_df))

t1, t2, t3, t4 = st.tabs(["Assets", "Who holds what", "By department", "To recover"])
with t1:
    if assets_df.empty:
        st.info("No assets match these filters.")
    st.dataframe(assets_df, use_container_width=True)
with t2:
    st.dataframe(holders_df, use_container_width=True)
with t3:
    st.bar_chart(dept_df.set_index("department"))
with t4:
    st.dataframe(recover_df, use_container_width=True)
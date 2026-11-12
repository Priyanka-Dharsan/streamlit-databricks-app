import os

import pandas as pd
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config

st.set_page_config(page_title="IT Asset Tracker", page_icon="💻", layout="wide")

# ---------- 1. Warehouse ID comes from app.yaml (valueFrom) or your local `set` command ----------
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID")
if not WAREHOUSE_ID:
    st.error("DATABRICKS_WAREHOUSE_ID is not set. Check the app resource and app.yaml.")
    st.stop()

cfg = Config()  # app identity when deployed, your CLI profile locally


# ---------- 2. One helper that runs a parameterized query ----------
@st.cache_data(ttl=60, show_spinner="Querying the warehouse...")
def run_query(query: str, params: dict | None = None) -> pd.DataFrame:
    with sql.connect(
        server_hostname=cfg.host,
        http_path=f"/sql/1.0/warehouses/{WAREHOUSE_ID}",
        credentials_provider=lambda: cfg.authenticate,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall_arrow().to_pandas()


# ---------- 3. Sidebar widgets (these become query parameters) ----------
st.title("💻 IT Asset Tracker (live Unity Catalog data)")

st.sidebar.header("Filters")
asset_type = st.sidebar.selectbox("Asset type", ["All", "Laptop", "Monitor", "Phone"])
status = st.sidebar.selectbox("Status", ["All", "Available", "Assigned", "Repair", "Retired"])
row_limit = st.sidebar.slider("Max rows", min_value=10, max_value=500, value=100, step=10)
if st.sidebar.button("Refresh data"):
    st.cache_data.clear()
    st.rerun()

# ---------- 4. Queries (no SELECT *, with parameters and LIMIT) ----------
ASSETS_SQL = """
SELECT asset_id, asset_type, model, status, purchase_date, warranty_end
FROM workspace.it_capstone.assets
WHERE (:asset_type = 'All' OR asset_type = :asset_type)
  AND (:status = 'All' OR status = :status)
ORDER BY asset_id
LIMIT :row_limit
"""

HOLDERS_SQL = """
SELECT
  a.asset_id,
  a.asset_type,
  a.model,
  e.full_name,
  e.department,
  h.action_date AS assigned_on
FROM workspace.it_capstone.v_current_holdings h
JOIN workspace.it_capstone.assets a ON a.asset_id = h.asset_id
JOIN workspace.it_capstone.employees e ON e.employee_id = h.employee_id
WHERE (:asset_type = 'All' OR a.asset_type = :asset_type)
ORDER BY e.full_name
LIMIT :row_limit
"""

DEPT_SQL = """
SELECT
  e.department,
  COUNT(h.asset_id) AS assets_held
FROM workspace.it_capstone.employees e
LEFT JOIN workspace.it_capstone.v_current_holdings h
  ON h.employee_id = e.employee_id
GROUP BY e.department
ORDER BY assets_held DESC
LIMIT :row_limit
"""

# ---------- 5. Run the queries ----------
try:
    assets_df = run_query(
        ASSETS_SQL,
        {"asset_type": asset_type, "status": status, "row_limit": row_limit},
    )
    holders_df = run_query(HOLDERS_SQL, {"asset_type": asset_type, "row_limit": row_limit})
    dept_df = run_query(DEPT_SQL, {"row_limit": row_limit})
except Exception as e:
    st.error(f"Query failed: {e}")
    st.stop()

# ---------- 6. Show the results ----------
c1, c2, c3 = st.columns(3)
c1.metric("Assets shown", len(assets_df))
c2.metric("Currently held", len(holders_df))
c3.metric("Departments", len(dept_df))

tab_assets, tab_holders, tab_dept = st.tabs(["Assets", "Who holds what", "By department"])

with tab_assets:
    st.dataframe(assets_df, use_container_width=True)

with tab_holders:
    st.dataframe(holders_df, use_container_width=True)

with tab_dept:
    st.bar_chart(dept_df.set_index("department"))
    st.dataframe(dept_df, use_container_width=True)


# ===================== SESSION 8: App auth vs user auth =====================
st.divider()
st.header("🔐 App auth vs user auth")

mode = st.radio(
    "Run the query as:",
    ["App (service principal)", "User (forwarded token)"],
    horizontal=True,
)

AUTH_SQL = """
SELECT employee_id, full_name, department, location, current_user() AS running_as
FROM workspace.it_capstone.employees
ORDER BY employee_id
LIMIT :row_limit
"""

def run_query_as_user(query: str, params: dict, token: str) -> pd.DataFrame:
    # No st.cache_data here: a shared cache would show one user's rows to another user.
    with sql.connect(
        server_hostname=cfg.host,
        http_path=f"/sql/1.0/warehouses/{WAREHOUSE_ID}",
        access_token=token,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall_arrow().to_pandas()


try:
    if mode.startswith("App"):
        auth_df = run_query(AUTH_SQL, {"row_limit": 100})
    else:
        user_token = st.context.headers.get("x-forwarded-access-token")
        if not user_token:
            st.warning(
                "No user token found. This works only in the deployed app, "
                "with the 'sql' scope added in Settings > User authorization."
            )
            st.stop()
        auth_df = run_query_as_user(AUTH_SQL, {"row_limit": 100}, user_token)

    st.metric("Rows returned", len(auth_df))
    if not auth_df.empty:
        st.caption(f"Query ran as: {auth_df['running_as'].iloc[0]}")
    st.dataframe(auth_df, use_container_width=True)
except Exception as e:
    st.error(f"Query failed: {e}")
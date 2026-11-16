import os

import pandas as pd
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config

WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID")
_cfg = Config()  # IDENTITY MODE: app authorization (service principal)

MAX_ROWS = 500


def _limit(n: int) -> int:
    return max(1, min(int(n), MAX_ROWS))


@st.cache_data(ttl=600, show_spinner=False)
def _run(query: str, params: dict) -> pd.DataFrame:
    with sql.connect(
        server_hostname=_cfg.host,
        http_path=f"/sql/1.0/warehouses/{WAREHOUSE_ID}",
        credentials_provider=lambda: _cfg.authenticate,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall_arrow().to_pandas()


def list_assets(asset_type="All", status="All", limit=100) -> pd.DataFrame:
    return _run(
        """
        SELECT asset_id, asset_type, model, status, purchase_date, warranty_end
        FROM workspace.it_capstone.assets
        WHERE (:asset_type = 'All' OR asset_type = :asset_type)
          AND (:status = 'All' OR status = :status)
        ORDER BY asset_id
        LIMIT :row_limit
        """,
        {"asset_type": asset_type, "status": status, "row_limit": _limit(limit)},
    )


def current_holders(asset_type="All", limit=100) -> pd.DataFrame:
    return _run(
        """
        SELECT a.asset_id, a.asset_type, a.model, e.full_name, e.department,
               h.action_date AS assigned_on
        FROM workspace.it_capstone.v_current_holdings h
        JOIN workspace.it_capstone.assets a ON a.asset_id = h.asset_id
        JOIN workspace.it_capstone.employees e ON e.employee_id = h.employee_id
        WHERE (:asset_type = 'All' OR a.asset_type = :asset_type)
        ORDER BY e.full_name
        LIMIT :row_limit
        """,
        {"asset_type": asset_type, "row_limit": _limit(limit)},
    )


def assets_by_department(limit=50) -> pd.DataFrame:
    return _run(
        """
        SELECT e.department, COUNT(h.asset_id) AS assets_held
        FROM workspace.it_capstone.employees e
        LEFT JOIN workspace.it_capstone.v_current_holdings h
          ON h.employee_id = e.employee_id
        GROUP BY e.department
        ORDER BY assets_held DESC
        LIMIT :row_limit
        """,
        {"row_limit": _limit(limit)},
    )


def inactive_holders(limit=100) -> pd.DataFrame:
    return _run(
        """
        SELECT a.asset_id, a.model, e.full_name, e.department,
               h.action_date AS assigned_on
        FROM workspace.it_capstone.v_current_holdings h
        JOIN workspace.it_capstone.assets a ON a.asset_id = h.asset_id
        JOIN workspace.it_capstone.employees e ON e.employee_id = h.employee_id
        WHERE e.is_active = false
        ORDER BY h.action_date
        LIMIT :row_limit
        """,
        {"row_limit": _limit(limit)},
    )
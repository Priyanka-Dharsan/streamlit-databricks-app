# Streamlit App on Databricks

Live URL: https://my-streamlit-app-7474644567946385.aws.databricksapps.com

## Versions

* Python 3.11
* Node.js v24.21.0
* Databricks CLI v1.22.1

## Commands

Pin Python:

```
uv python pin 3.11
```

Login:

```
databricks auth login --host https://dbc-345cc8cc-d9ef.cloud.databricks.com --profile freeedition
```

Run locally:

```
uv run streamlit run app.py
```

Deploy:

```
databricks apps create my-streamlit-app
databricks sync . /Workspace/Users/<your-email>/my-streamlit-app
databricks apps deploy my-streamlit-app --source-code-path /Workspace/Users/<your-email>/my-streamlit-app
```

Read logs:

```
databricks apps logs my-streamlit-app
```



## Session 6 - Environment map

| Item          | Value                           | 
|---------------|---------------------------------|
| Platform      | Databricks Free Edition         | 
| Catalog       | workspace                       | 
| Schema        | workspace.it_capstone           |  
| SQL Warehouse | Serverless Starter Warehouse    |  
| Volume        | workspace.it_capstone.raw_files |  
| App Framework | Streamlit                       |  


### Tables and views

| Object | Type | Read / Write | Purpose |
|---|---|---|---|
| `employees` | Table | Read | Employee list (sample data) |
| `assets` | Table | Read | Asset inventory |
| `asset_assignments` | Table | Write | Log of assign and return events |
| `v_current_holdings` | View | Read | Latest assignment per asset |
| `v_available_laptops` | View | Read | Laptops with status Available |
| `asset\\\_assignments` | Table | Write | Log of assign and return events |
| `v\\\_current\\\_holdings` | View | Read | Latest assignment per asset |
| `v\\\_available\\\_laptops` | View | Read | Laptops with status Available |


### Queries (`sql/queries.sql`)

1\. Available laptops

2\. Current holder of each asset

3\. Asset count by type and status

4\. Assets held per department

5\. Assets still held by inactive employees



## Session 7: Live data from Unity Catalog

\- SQL warehouse attached as an app resource (key: `sql-warehouse`)

\- `app.yaml` reads it with `valueFrom` into `DATABRICKS\_WAREHOUSE\_ID`

\- `app.py` uses databricks-sql-connector with parameterized queries (`:name`) and a `LIMIT` on every query

\- App service principal has USE CATALOG, USE SCHEMA and SELECT on `workspace.it\_capstone`

\- Deployed Streamlit is older than my local one, so I use `use\_container\_width=True`, which works on both


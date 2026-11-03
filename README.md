# Streamlit App on Databricks

Live URL: https://my-streamlit-app-7474644567946385.aws.databricksapps.com

## Versions

- Python 3.11
- Node.js v24.21.0
- Databricks CLI v1.22.1

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

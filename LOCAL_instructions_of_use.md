# Local Setup Guide — databricks_genai_demo

This guide explains how to get the project from GitHub, configure your Databricks credentials locally, and run the demo notebooks (`TOOLS_CONTEXT_5/`, `RAG_APPLICATION_C/`, etc.) directly from VS Code, without going through the Databricks UI.

File roles in this project:

- **`.env_duplicate`** — a non-secret example file, committed to the repo. It shows which variables are needed, with placeholder values.
- **`.env`** — your real, private credentials file. It is git-ignored and must never be committed. The notebooks load this file via `load_dotenv()`.

## 1. Prerequisites

- A GitHub account with access to the repo.
- A Databricks workspace (Free Edition is enough) with an active SQL Warehouse.
- [Visual Studio Code](https://code.visualstudio.com/) with the **Python** and **Jupyter** extensions (Microsoft).
- Python 3.10+ installed locally.
- Git installed locally.

## 2. Clone the project

```bash
git clone https://github.com/<your-org>/databricks_genai_demo.git
cd databricks_genai_demo
```

Open the folder in VS Code (`File > Open Folder...`).

## 3. Install the Python dependencies

Create a dedicated virtual environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Two packages used in the notebooks (`python-dotenv` and `tiktoken`) are not listed in `requirements.txt` — install them separately:

```bash
pip install python-dotenv tiktoken
```

In VS Code, select this environment as the Python interpreter (`Ctrl+Shift+P` / `Cmd+Shift+P` → *Python: Select Interpreter* → choose `.venv`).

## 4. Create your `.env` file from the template

Copy the example file and fill it in with your own credentials:

```bash
cp .env_duplicate .env          # on Windows: copy .env_duplicate .env
```

`.env` is git-ignored, so your credentials stay local.

## 5. Retrieve your Databricks credentials

You need 4 values, all available from your Databricks workspace.

| Variable | Where to find it |
|---|---|
| `DATABRICKS_HOST` | Your workspace URL, e.g. `https://<workspace>.cloud.databricks.com` (no trailing `/`) |
| `DATABRICKS_TOKEN` | Settings (gear icon in the left sidebar) → **Developer** → **Access tokens** → **Manage** → **Generate new token**. Copy the token right away — it won't be shown again. |
| `SQL_WAREHOUSE_ID` | **SQL Warehouses** (left sidebar) → open your warehouse (e.g. *Serverless Starter Warehouse*) → on the **Overview** tab, the ID is shown in parentheses next to the warehouse name, e.g. `Serverless Starter Warehouse (ID: e47e3ffb19761b63)` |
| `MLFLOW_TRACKING_URI` | Use the literal value `databricks` — MLflow will then use `DATABRICKS_HOST`/`DATABRICKS_TOKEN` to reach the Databricks-managed tracking server |

If the UI has changed since this guide was written, the official Databricks documentation remains the source of truth for generating tokens and finding a SQL Warehouse ID.

Fill in `.env`:

```
DATABRICKS_HOST=https://<workspace>.cloud.databricks.com
DATABRICKS_TOKEN=dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXX
MLFLOW_TRACKING_URI=databricks
SQL_WAREHOUSE_ID=e47e3ffb19761b63
```

## 6. Run the notebooks in VS Code

1. Open a notebook, e.g. `TOOLS_CONTEXT_5/context_pruning_3.ipynb`.
2. Select the `.venv` Python kernel (top right of the notebook).
3. Run the setup cell (`load_dotenv()` + assertions on the environment variables) — it should pass without errors, since `load_dotenv()` reads `.env` by default.
4. **Before running the rest of the notebook**, look for lines like:

```python
mlflow.set_experiment("/Users/oliver@mlops-media.com/context_pruning_3")
```

   and replace the email with your own Databricks username (shown in the top-right corner of your workspace) — otherwise `mlflow.set_experiment` will fail due to lack of permissions on someone else's home folder.

5. Run the remaining cells normally — they call the Databricks API (`WorkspaceClient`, `ChatDatabricks`, SQL queries via the warehouse) directly from your machine, using the credentials loaded from `.env`.

## 7. Quick verification

To validate the whole chain without running a full notebook, run this in a terminal (with `.venv` activated):

```bash
python -c "
from dotenv import load_dotenv
load_dotenv()
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
print('Connected to:', w.config.host)
print(w.current_user.me().user_name)
"
```

If your Databricks username is printed, the setup is correct.

## Troubleshooting

- **`AssertionError: DATABRICKS_HOST not set`** — `.env` is missing or wasn't created from `.env_duplicate`. Make sure the file is named exactly `.env` and sits at the project root, then restart the Jupyter kernel.
- **Permission error on `mlflow.set_experiment`** — replace the `/Users/<demo-author-email>/...` path with your own Databricks email.
- **`ModuleNotFoundError: dotenv` or `tiktoken`** — go back to step 3, these packages aren't in `requirements.txt`.
- **Kernel doesn't pick up new variables** — restart the Jupyter kernel after editing `.env`.

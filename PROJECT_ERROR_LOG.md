# 🐛 Project Error & Mistake Log

> **Project:** Telco Customer Churn — End-to-End Machine Learning Project  
> **Purpose:** Document mistakes, errors, debugging steps, root causes, solutions, and lessons learned.

---

# Error Log

## ERR-001 — Python Version Incompatible with Dependency

**Stage:** Environment Setup  
**Severity:** 🔴 High  
**Status:** ✅ Resolved

### Error

```text
No solution found when resolving dependencies.

The current Python version (3.10) does not satisfy Python>=3.11,
and contourpy==1.3.3 depends on Python>=3.11.
```

### Root Cause

The virtual environment was created with Python 3.10, while `contourpy==1.3.3` requires Python 3.11 or newer.

### Solution

```powershell
py -3.11 -m venv project_env
.\project_env\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

### Lesson

Always verify the project's required Python version before creating the virtual environment.

---

## ERR-002 — `uv` Command Not Recognized

**Stage:** Environment Setup  
**Severity:** 🟡 Medium  
**Status:** ✅ Resolved

### Error

```text
The term 'uv' is not recognized as the name of a cmdlet,
function, script file, or operable program.
```

### Root Cause

`uv` was not installed or was not available in PATH.

### Solution

```powershell
pip install uv
uv --version
uv pip install -r requirements.txt
```

### Lesson

Creating a virtual environment does not automatically install `uv`.

---

## ERR-003 — MLflow Windows File URI Error

**Stage:** MLflow  
**Severity:** 🔴 High  
**Status:** ✅ Resolved

### Error

```text
MlflowException:
file://F:\resume project\Telco chun customer end to end project/mlruns
is not a valid remote uri.
```

### Root Cause

A Windows filesystem path was manually constructed as a `file://` URI.

### Solution

```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MLRUNS_DIR = PROJECT_ROOT / "mlruns"

mlflow.set_tracking_uri(MLRUNS_DIR.as_uri())
```

### Lesson

Use `pathlib` to create cross-platform filesystem paths and URIs instead of manually constructing `file://` strings.

---

## ERR-004 — Virtual Environment Should Not Be Committed

**Stage:** Git  
**Severity:** 🟡 Medium  
**Status:** ✅ Resolved

### Mistake

I considered pushing `project_env/` to GitHub.

### Solution

Added:

```gitignore
project_env/
venv/
env/
.venv/
```

to `.gitignore`.

The reproducible dependency information is stored in:

```text
requirements.txt
```

### Lesson

Git should track the instructions needed to recreate the environment, not the environment itself.

---

## ERR-005 — MLflow Generated Artifacts Should Not Be Committed

**Stage:** Git / MLflow  
**Severity:** 🟢 Low  
**Status:** ✅ Resolved

### Problem

MLflow generates:

```text
mlruns/
artifacts/
```

### Solution

Added:

```gitignore
mlruns/
artifacts/
```

to `.gitignore`.

### Lesson

Generated experiment data should normally be separated from source code.

---

## ERR-006 — Windows Path / Directory Creation Error

**Stage:** Data Preparation  
**Severity:** 🟡 Medium  
**Status:** ✅ Resolved

### Error

```text
OSError: [WinError 123] The filename, directory name,
or volume label syntax is incorrect
```

### Root Cause

A Windows path was used as a normal Python string, where backslashes can represent escape sequences.

There was also confusion between `os.mkdir()` and `pathlib.Path.mkdir()`.

### Solution

Use:

```python
OUT = PROJECT_ROOT / "data" / "processed"

OUT.mkdir(parents=True, exist_ok=True)
```

For saving the CSV:

```python
output_file = OUT / "processed_data.csv"
df_processed.to_csv(output_file, index=False)
```

### Lesson

Use `pathlib` for project paths and distinguish between an output directory and an output file.

---

## ERR-007 — MLflow Tracking URI Error in Pipeline Script

**Stage:** Pipeline / MLflow  
**Severity:** 🔴 High  
**Status:** ✅ Resolved

### Error

```text
MlflowException:
file://F:\resume project\Telco chun customer end to end project/mlruns
is not a valid remote uri.
```

### Root Cause

The MLflow tracking URI in the pipeline script used the same invalid Windows `file://` construction.

### Solution

```python
from pathlib import Path
import mlflow

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MLRUNS_DIR = PROJECT_ROOT / "mlruns"

mlflow.set_tracking_uri(MLRUNS_DIR.as_uri())
```

### Lesson

Fixing configuration in a notebook does not automatically fix configuration in a separate pipeline script.

---

## ERR-008 — Great Expectations API / Version Mismatch

**Stage:** Data Validation  
**Severity:** 🔴 High  
**Status:** ✅ Resolved

### Error

```text
AttributeError:
module 'great_expectations' has no attribute 'dataset'
```

### Root Cause

The validation code used the older:

```python
ge.dataset.PandasDataset(df)
```

API, while the environment had:

```text
Great Expectations 1.5.8
```

### Solution

Updated `validate_data.py` to use the Great Expectations 1.5.x workflow while preserving the validation rules.

### Lesson

A dependency installing successfully does not guarantee that the application's code matches its API. Package versions and application code must be compatible.

---

## ERR-009 — `ModuleNotFoundError: No module named 'utils'`

**Stage:** Python Package / Project Structure  
**Severity:** 🟡 Medium  
**Status:** ✅ Resolved

### Error

```text
ModuleNotFoundError: No module named 'utils'
```

### Project Structure

```text
src/
└── utils/
    └── validate_data.py
```

### Root Cause

When executing the pipeline script directly, Python did not automatically include the project's `src/` directory in its module search path.

### Solution

Before importing project modules:

```python
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from utils.validate_data import validate_telco_data
```

### Lesson

A good `src/` project structure still requires Python to know where the source package is located when scripts are executed directly.

---

## ERR-010 — String vs Float Comparison in `TotalCharges`

**Stage:** Preprocessing / Validation  
**Severity:** 🔴 High  
**Status:** ✅ Resolved

### Error

```text
TypeError: '>=' not supported between instances of 'str' and 'float'
```

### Failing Logic

```python
total_charges >= monthly_charges
```

### Root Cause

`TotalCharges` was still a string/object column when validation was executed, while `MonthlyCharges` was numeric.

Python was effectively trying to compare:

```python
"500.0" >= 50.0
```

### Investigation

The preprocessing function already contains:

```python
df["TotalCharges"] = pd.to_numeric(
    df["TotalCharges"],
    errors="coerce"
)
```

Therefore, the issue was the order of operations.

### Correct Pipeline Order

```text
Raw CSV
   ↓
Preprocessing
   ↓
Validation
   ↓
Feature Engineering
   ↓
Model Training
```

### Lesson

Preprocessing makes data usable; validation checks whether the cleaned data is acceptable.

---

## ERR-011 — XGBoost Rejected Categorical `object` Columns

**Date:** 2026-08-09  
**Stage:** Feature Engineering / Modeling  
**Severity:** 🔴 High  
**Status:** ✅ Resolved  

### What I Was Trying To Do
Train XGBoost model in Phase 2 modeling script (`scripts/test_pipeline_phase2_modeling.py`).

### Error
```text
ValueError: DataFrame.dtypes for data must be int, float, bool or category.
  Unsafe target type for target column 'Churn'
```

### Root Cause
1. `Churn` target column was string (`'No'`, `'Yes'`) instead of numeric `0`/`1`.
2. Categorical features were raw strings (`object` dtype) instead of one-hot encoded numeric features or boolean columns converted to `int`.

### Solution
Applied feature engineering pipeline `build_features` to encode categorical variables into numeric columns and mapped target `Churn` to `0`/`1`:
```python
if df["Churn"].dtype == "object":
    df["Churn"] = df["Churn"].str.strip().map({"No": 0, "Yes": 1})

df = build_features(df, target_col="Churn")

bool_cols = df.select_dtypes(include=["bool"]).columns
if len(bool_cols) > 0:
    df[bool_cols] = df[bool_cols].astype(int)
```

### What I Learned
XGBoost requires all input features and target labels to be numeric (`int`, `float`) or explicitly converted boolean/category dtypes.

### How To Avoid This
Always pass features through `build_features()` and explicitly convert boolean/categorical columns before model training.

---

## ERR-012 — Cannot find module `xgboost` (Python Interpreter Mismatch)

**Date:** 2026-08-09  
**Stage:** Local Execution / IDE Setup  
**Severity:** 🟡 Medium  
**Status:** ✅ Resolved  

### What I Was Trying To Do
Run `python scripts/test_pipeline_phase2_modeling.py` from VS Code / shell.

### Error
```text
Cannot find module `xgboost`
Looked in these locations:
Site package path queried from interpreter: ["C:\Users\Tamil\AppData\Local\Programs\Python\Python311\..."]
```

### Root Cause
VS Code / Pylance was configured to use the global system Python interpreter (`C:\Users\Tamil\AppData\Local\Programs\Python\Python311`), which did not have `xgboost` installed. `xgboost` (v3.0.3) was installed inside `project_env`.

### Solution
Created `.vscode/settings.json` to lock the workspace interpreter path:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/project_env/Scripts/python.exe",
    "python.analysis.extraPaths": [
        "${workspaceFolder}"
    ]
}
```

### What I Learned
IDE analysis servers and terminal execution must be pointed explicitly to the active virtual environment (`project_env`).

### How To Avoid This
Always create a workspace `.vscode/settings.json` file when initializing Python virtual environments.

---

## ERR-013 — Web Browser Cannot Load `http://0.0.0.0:8000/`

**Date:** 2026-08-09  
**Stage:** Web Application Serving  
**Severity:** 🟡 Medium  
**Status:** ✅ Resolved  

### What I Was Trying To Do
Access the FastAPI + Gradio application in a Windows web browser after running `python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000`.

### Error
```text
The webpage at http://0.0.0.0:8000/ might be temporarily down or it may have moved permanently to a new web address.
```

### Root Cause
`0.0.0.0` is a wildcard bind address for network interfaces, not a navigable IP address for Windows web browsers. Additionally, `/` returned raw JSON (`{"status": "ok"}`) instead of opening the UI.

### Solution
1. Configured local Uvicorn execution to bind to `127.0.0.1`:
```powershell
python -m uvicorn src.app.main:app --host 127.0.0.1 --port 8000
```
2. Added `RedirectResponse(url="/ui")` at the `/` endpoint in `src/app/main.py` so root browser requests automatically load the Gradio interface.

### What I Learned
Use `127.0.0.1` or `localhost` for local Windows browser access. Reserve `0.0.0.0` for Docker container execution.

### How To Avoid This
Redirect root `/` routes to interactive web UIs `/ui` and maintain `/health` for load balancers.

---

## ERR-014 — Matplotlib Font Cache Lock Permission Denied on Windows

**Date:** 2026-08-09  
**Stage:** Serving / Gradio Integration  
**Severity:** 🟡 Medium  
**Status:** ✅ Resolved  

### What I Was Trying To Do
Serve the Gradio UI using Uvicorn.

### Error
```text
Could not save font_manager cache [Errno 13] Permission denied: 'C:\Users\Tamil\.matplotlib\fontlist-v390.json.matplotlib-lock'
```

### Root Cause
Matplotlib (imported internally by Gradio) tried to write a font cache lock file to the user home directory `C:\Users\Tamil\.matplotlib` while a concurrent process held a file lock.

### Solution
Set `MPLCONFIGDIR` to a system temporary directory before importing Gradio/Matplotlib at the top of `main.py` and `app.py`:
```python
import os
import tempfile

os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib"))
```

### What I Learned
Matplotlib requires a dedicated writable configuration directory in multi-process or web serving environments.

### How To Avoid This
Set `MPLCONFIGDIR` to a temp directory at the entry point of all web applications.

---

## ERR-015 — `ModuleNotFoundError: No module named 'gradio_client.serializing'` in GitHub Actions

**Date:** 2026-08-09  
**Stage:** CI/CD Workflow  
**Severity:** 🔴 High  
**Status:** ✅ Resolved  

### What I Was Trying To Do
Run automated tests in GitHub Actions CI workflow using `pip install -r requirements.txt`.

### Error
```text
File ".../site-packages/gradio/components/annotated_image.py", line 9, in <module>
    from gradio_client.serializing import JSONSerializable
ModuleNotFoundError: No module named 'gradio_client.serializing'
```

### Root Cause
`requirements.txt` had `gradio` unpinned and missing `gradio_client`, causing `pip` in the GitHub Actions Linux runner to install mismatched versions of Gradio and Gradio Client.

### Solution
Pinned exact compatible versions in `requirements.txt`:
```text
gradio==6.22.0
gradio_client==2.6.0
```

### What I Learned
High-level framework libraries like Gradio require their companion libraries (`gradio_client`) to be pinned together.

### How To Avoid This
Never leave core framework requirements unpinned in production `requirements.txt`.

---

## ERR-016 — `Failed to load model: No model found in local mlruns` in GitHub Actions

**Date:** 2026-08-09  
**Stage:** CI/CD / Serving  
**Severity:** 🔴 High  
**Status:** ✅ Resolved  

### What I Was Trying To Do
Execute `scripts/test_fastapi.py` during the `test` stage of GitHub Actions.

### Error
```text
Exception: Failed to load model: No model found in local mlruns
```

### Root Cause
`mlruns/` is in `.gitignore`, so it does not exist on a fresh GitHub runner checkout. `inference.py` only searched `./mlruns/*/*/artifacts/model` and did not search `src/serving/model/` (which is tracked in Git).

### Solution
Updated `src/serving/inference.py` to search both Git-tracked production model paths and local `mlruns`:
```python
local_model_paths = (
    glob.glob("./src/serving/model/**/artifacts/model", recursive=True) +
    glob.glob("./mlruns/**/artifacts/model", recursive=True)
)
```

### What I Learned
Inference loading logic must be able to discover model artifacts regardless of whether the environment is Docker (`/app/model`), Git checkout (`src/serving/model`), or local runs (`mlruns`).

### How To Avoid This
Always test fallback artifact paths against clean repository checkouts.

---

## ERR-017 — Docker Hub Push Access Denied (`insufficient_scope` / Namespace Mismatch)

**Date:** 2026-08-09  
**Stage:** Docker Build & Push / CI/CD Deployment  
**Severity:** 🔴 High  
**Status:** ✅ Resolved  

### What I Was Trying To Do
Push built Docker image to Docker Hub from GitHub Actions (`docker/build-push-action@v5`).

### Error
```text
ERROR: failed to solve: failed to push ***23/telco-fastapi:latest: push access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
```

### Root Cause
The GitHub Actions workflow specified `tamilnilavank23/telco-fastapi`, but the authenticating Docker Hub user account handle was `tamilnilavank`. Docker Hub denied push permissions to a non-owned namespace.

### Solution
Updated `.github/workflows/ci.yml` image repository tag to `tamilnilavank/telco-fastapi` and set `DOCKERHUB_USERNAME` secret to `tamilnilavank` with Read & Write access token.

### What I Learned
Docker Hub image repository namespaces must match the exact Docker Hub account handle associated with the access token.

### How To Avoid This
Verify Docker Hub account handle before defining image tags in CI/CD manifests.

---

# 🧠 General Debugging Checklist

Whenever I encounter a new error:

## 1. Read the entire traceback

Identify:

```text
Exception Type
↓
Error Message
↓
My project file
↓
Line number
↓
Actual failing operation
```

## 2. Identify the layer

```text
[ ] Python
[ ] Virtual environment
[ ] Dependency
[ ] File/path
[ ] Git
[ ] Data loading
[ ] Preprocessing
[ ] Validation
[ ] Feature engineering
[ ] Model training
[ ] MLflow
[ ] Optuna
[ ] API
[ ] Docker
[ ] Deployment
```

## 3. Check data types before model operations

```python
print(df.dtypes)
```

```python
print(df.head())
```

```python
print(df.isna().sum())
```

For a specific column:

```python
print(df["TotalCharges"].dtype)
```

## 4. Check the pipeline order

```text
Load
 ↓
Preprocess
 ↓
Validate
 ↓
Feature Engineer
 ↓
Split
 ↓
Train
 ↓
Evaluate
 ↓
Log
```

---

# 📊 Error Summary

| ID | Problem | Stage | Severity | Status |
|---|---|---|---|---|
| ERR-001 | Python 3.10 incompatible with dependency | Environment | 🔴 High | ✅ Resolved |
| ERR-002 | `uv` command not recognized | Environment | 🟡 Medium | ✅ Resolved |
| ERR-003 | MLflow Windows file URI | MLflow | 🔴 High | ✅ Resolved |
| ERR-004 | Virtual environment and Git | Git | 🟡 Medium | ✅ Resolved |
| ERR-005 | MLflow artifacts and Git | Git / MLflow | 🟢 Low | ✅ Resolved |
| ERR-006 | Windows path / directory creation | Data Preparation | 🟡 Medium | ✅ Resolved |
| ERR-007 | MLflow URI in pipeline script | MLflow | 🔴 High | ✅ Resolved |
| ERR-008 | Great Expectations API mismatch | Validation | 🔴 High | ✅ Resolved |
| ERR-009 | Python cannot find `utils` | Project Structure | 🟡 Medium | ✅ Resolved |
| ERR-010 | String vs float comparison | Preprocessing / Validation | 🔴 High | ✅ Resolved |
| ERR-011 | XGBoost rejected categorical `object` columns | Feature Engineering / Modeling | 🔴 High | ✅ Resolved |
| ERR-012 | Cannot find module `xgboost` (Python interpreter mismatch) | IDE / Execution | 🟡 Medium | ✅ Resolved |
| ERR-013 | Browser error loading `http://0.0.0.0:8000/` | Serving / Web UI | 🟡 Medium | ✅ Resolved |
| ERR-014 | Matplotlib font cache lock permission denied on Windows | Serving / Gradio | 🟡 Medium | ✅ Resolved |
| ERR-015 | `ModuleNotFoundError: No module named 'gradio_client.serializing'` in CI | CI/CD / Dependencies | 🔴 High | ✅ Resolved |
| ERR-016 | `Failed to load model: No model found in local mlruns` in CI | CI/CD / Inference | 🔴 High | ✅ Resolved |
| ERR-017 | Docker Hub Push Access Denied (`insufficient_scope` / namespace mismatch) | Docker / CI/CD | 🔴 High | ✅ Resolved |

---

# 💡 Key Lessons Learned So Far

### Environment

- Check the required Python version before creating a virtual environment.
- Dependencies can have their own Python-version requirements.
- Virtual environments should not be committed to Git.

### Data

- CSV values that look numeric may still be loaded as strings.
- Always inspect `df.dtypes`.
- Missing-value handling is a data-processing/modeling decision and should be documented.

### Pipeline Architecture

```text
Preprocessing
      ↓
Validation
      ↓
Feature Engineering
      ↓
Model Training
```

Each stage should have a clear responsibility.

### ML Engineering

- Use `pathlib` for cross-platform paths.
- Keep generated MLflow artifacts outside Git.
- Match application code with the installed library API.
- Encode categorical variables before passing them to models that require numerical input.

---

# 🚀 Future Errors

Continue adding new problems below this line.

---

## ERR-018 — [Short Problem Name]

**Date:**  
**Stage:**  
**Severity:**  
**Status:** 🟡 Investigating / ✅ Resolved

### What I Was Trying To Do

### Error

```text
Paste error here
```

### Root Cause

### Solution

### What I Learned

### How To Avoid This

---

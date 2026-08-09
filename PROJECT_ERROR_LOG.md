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
| ERR-011 | XGBoost rejected categorical `object` columns | Feature Engineering / Modeling | 🔴 High | 🟡 Investigating |

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

## ERR-XXX — [Short Problem Name]

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

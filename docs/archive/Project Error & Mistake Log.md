# 🐛 Project Error & Mistake Log

> **Project:** Telco Customer Churn — End-to-End Machine Learning Project  
> **Purpose:** Document mistakes, errors, debugging steps, root causes, and solutions encountered during project development.

---

## 📌 Why Maintain This Log?

This document records problems encountered during the development of the project.

For every error, try to document:

1. What I was trying to do
2. What went wrong
3. Error message
4. Root cause
5. How I fixed it
6. What I learned
7. How to avoid it in future

The goal is not only to fix the current problem but to build a personal debugging knowledge base.

---

# Error Log

## ERR-001 — Python Version Incompatible with Dependency

**Date:** 2026-08-08  
**Stage:** Environment Setup  
**Severity:** 🔴 High  
**Status:** ✅ Resolved

### What I Was Trying To Do

Install the project dependencies using:

```bash
uv pip install -r requirements.txt
```

### Error

```text
No solution found when resolving dependencies:

Because the current Python version (3.10) does not satisfy
Python>=3.11 and contourpy==1.3.3 depends on Python>=3.11,
we can conclude that contourpy==1.3.3 cannot be used.

And because you require contourpy==1.3.3,
we can conclude that your requirements are unsatisfiable.
```

### What Was My Mistake?

I created the virtual environment using Python 3.10:

```bash
python -m venv project_env
```

However, the project's dependency configuration required Python 3.11 because:

```text
contourpy==1.3.3
        ↓
requires Python >= 3.11
```

### Root Cause

The Python version used to create the virtual environment was incompatible with one of the pinned dependencies.

```text
Python 3.10
    ↓
contourpy 1.3.3
    ↓
Python >= 3.11 ❌
```

### Solution

Installed Python 3.11 and recreated the virtual environment using:

```powershell
py -3.11 -m venv project_env
```

Activated it:

```powershell
.\project_env\Scripts\Activate.ps1
```

Verified the version:

```powershell
python --version
```

Then installed dependencies:

```powershell
uv pip install -r requirements.txt
```

### What I Learned

Before creating a virtual environment, I should check:

- Required Python version
- `requirements.txt`
- Dependency compatibility
- Project documentation

A virtual environment is tied to the Python version used to create it.

### How To Avoid This

Check the Python version before creating the environment:

```powershell
py -0p
```

Then create the environment explicitly:

```powershell
py -3.11 -m venv project_env
```

---

# ERR-002 — `uv` Command Not Recognized

**Date:** 2026-08-08  
**Stage:** Environment Setup  
**Severity:** 🟡 Medium  
**Status:** ✅ Resolved

### What I Was Trying To Do

Install project dependencies using:

```powershell
uv pip install -r requirements.txt
```

### Error

```text
The term 'uv' is not recognized as the name of a cmdlet,
function, script file, or operable program.
```

### Root Cause

`uv` was not installed or was not available in the system PATH.

### Solution

Installed `uv`:

```powershell
pip install uv
```

Then verified:

```powershell
uv --version
```

After that:

```powershell
uv pip install -r requirements.txt
```

worked.

### What I Learned

`uv` is a separate Python package/environment management tool. Creating a virtual environment does not automatically install `uv`.

### How To Avoid This

If a project uses `uv`, verify it before installing dependencies:

```powershell
uv --version
```

---

# ERR-003 — MLflow Windows File URI Error

**Date:** 2026-08-09  
**Stage:** Experiment Tracking / MLflow  
**Severity:** 🔴 High  
**Status:** ✅ Resolved

### What I Was Trying To Do

Configure MLflow to store experiment tracking information locally.

Original code:

```python
project_root = os.path.abspath(os.path.join(os.getcwd(), ".."))

mlflow.set_tracking_uri(
    f"file://{project_root}/mlruns"
)
```

### Error

```text
MlflowException:

file://f:\resume project\Telco chun customer end to end project/mlruns
is not a valid remote uri.

For remote access on Windows, please consider using
a different scheme such as SMB.
```

### Root Cause

The local Windows filesystem path was manually converted into a `file://` URI.

The resulting path looked like:

```text
file://f:\resume project\Telco chun customer end to end project/mlruns
```

The Windows path format and URI format were incompatible with how MLflow interpreted the tracking URI.

### Solution

Use `pathlib` to correctly construct the local path and convert it to a URI:

```python
from pathlib import Path
import mlflow

project_root = Path.cwd().parent

mlruns_path = project_root / "mlruns"

mlflow.set_tracking_uri(
    mlruns_path.as_uri()
)

mlflow.set_experiment("Telco Churn - XGBoost")
```

Alternatively, a direct filesystem path can be used:

```python
import os
import mlflow

project_root = os.path.abspath(
    os.path.join(os.getcwd(), "..")
)

mlruns_path = os.path.join(
    project_root,
    "mlruns"
)

mlflow.set_tracking_uri(mlruns_path)
```

### What I Learned

Do not manually construct filesystem URIs using:

```python
f"file://{path}"
```

especially when the project needs to work across operating systems.

`pathlib` provides safer cross-platform path handling.

### Better Practice

Prefer:

```python
Path(...).as_uri()
```

instead of manually creating:

```python
file://...
```

---

# ERR-004 — Virtual Environment Should Not Be Committed

**Date:** 2026-08-09  
**Stage:** Git / Project Management  
**Severity:** 🟡 Medium  
**Status:** ✅ Resolved

### What I Initially Considered

I created a virtual environment:

```text
project_env/
```

and considered whether it should be pushed to GitHub.

### Mistake

A virtual environment contains:

- Installed packages
- Python binaries
- Platform-specific files
- Machine-specific paths
- Large amounts of unnecessary data

Therefore, it should not be committed to Git.

### Solution

Added the environment to `.gitignore`:

```gitignore
project_env/
venv/
env/
.venv/
```

### What Should Be Committed Instead?

Commit:

```text
requirements.txt
```

rather than:

```text
project_env/
```

A developer can recreate the environment using:

```powershell
py -3.11 -m venv project_env
.\project_env\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

### What I Learned

Git should track the **instructions needed to reproduce the environment**, not the environment itself.

---

# ERR-005 — MLflow Artifacts Should Not Be Committed

**Date:** 2026-08-09  
**Stage:** Git / MLflow  
**Severity:** 🟢 Low  
**Status:** ✅ Resolved

### Problem

MLflow creates experiment tracking data under:

```text
mlruns/
```

The project can also generate:

```text
artifacts/
```

These can become large and are usually generated during experimentation.

### Solution

Added them to `.gitignore`:

```gitignore
mlruns/
artifacts/
```

### What I Learned

Generated experiment data should generally be separated from source code.

GitHub should contain:

```text
source code
configuration
documentation
requirements
tests
```

while generated MLflow data can remain local or be stored using an appropriate experiment tracking system.

---

# 🧠 General Debugging Checklist

Whenever I encounter a new error, I should go through these steps.

## 1. Read the Entire Error

Don't immediately copy the last line.

Look for:

```text
Exception Type
↓
Error Message
↓
File
↓
Line Number
↓
Root Cause
```

---

## 2. Identify the Layer

Ask:

```text
Is this a...

[ ] Python error?
[ ] Dependency error?
[ ] Virtual environment error?
[ ] Operating system error?
[ ] File/path error?
[ ] Git error?
[ ] Database error?
[ ] MLflow error?
[ ] Model training error?
[ ] API error?
[ ] Docker error?
[ ] Deployment error?
```

---

## 3. Check the Environment

For Python-related problems:

```powershell
python --version
```

Check Python location:

```powershell
where python
```

Check installed packages:

```powershell
pip list
```

Check `uv`:

```powershell
uv --version
```

---

## 4. Check Paths

For Windows path problems:

```python
from pathlib import Path

print(Path.cwd())
```

Prefer:

```python
Path(...)
```

over manually concatenating paths.

---

## 5. Check Dependencies

If installation fails:

```text
Python Version
        ↓
Package Version
        ↓
Package Compatibility
        ↓
requirements.txt
```

Do not immediately downgrade a package without understanding why it is incompatible.

---

## 6. Record the Error

After solving a problem, add an entry to this file.

Use the format:

```text
ERR-XXX — Short Description

Date:
Stage:
Severity:
Status:

What I Was Trying To Do:

Error:

Root Cause:

Solution:

What I Learned:

How To Avoid This:
```

---

# 📊 Error Summary

| ID | Problem | Stage | Severity | Status |
|---|---|---|---|---|
| ERR-001 | Python 3.10 incompatible with `contourpy==1.3.3` | Environment | 🔴 High | ✅ Resolved |
| ERR-002 | `uv` command not recognized | Environment | 🟡 Medium | ✅ Resolved |
| ERR-003 | MLflow Windows file URI error | MLflow | 🔴 High | ✅ Resolved |
| ERR-004 | Virtual environment and Git | Git | 🟡 Medium | ✅ Resolved |
| ERR-005 | MLflow artifacts and Git | Git / MLflow | 🟢 Low | ✅ Resolved |

---

# 💡 Lessons Learned So Far

### Environment Management

- Always verify the required Python version before creating a virtual environment.
- Different projects can require different Python versions.
- Virtual environments should not be committed to Git.

### Dependency Management

- A package version can impose its own Python-version requirements.
- `requirements.txt` should be treated as part of the project's reproducibility configuration.
- Don't blindly downgrade dependencies to fix an error.

### Cross-Platform Development

- Windows and Unix-like systems handle paths differently.
- Avoid manually constructing filesystem URIs.
- Use Python's `pathlib` for portable path handling.

### Git

- Don't commit virtual environments.
- Don't commit generated MLflow runs.
- Don't commit secrets or `.env` files.
- Commit reproducible configuration instead.

### MLflow

- Local MLflow tracking requires correct filesystem path configuration.
- Experiment data and source code should be treated separately.

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
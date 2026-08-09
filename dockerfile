# 1. Official lightweight Python base image
FROM python:3.11-slim

# 2. Set working directory inside container
WORKDIR /app

# 3. Copy requirements first for Docker build caching
COPY requirements.txt .

# 4. Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 5. Copy application source code
COPY . .

# Ensure MLflow model artifacts & feature schemas are populated at /app/model for inference
COPY src/serving/model/3b1a41221fc44548aed629fa42b762e0/artifacts/model /app/model
COPY src/serving/model/3b1a41221fc44548aed629fa42b762e0/artifacts/feature_columns.txt /app/model/feature_columns.txt
COPY src/serving/model/3b1a41221fc44548aed629fa42b762e0/artifacts/preprocessing.pkl /app/model/preprocessing.pkl

# Environment variables for real-time logging, Python imports, and Matplotlib config
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    MPLCONFIGDIR=/tmp/matplotlib

# Expose FastAPI port
EXPOSE 8000

# Entrypoint: Start FastAPI + Gradio server using Uvicorn
CMD ["python", "-m", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

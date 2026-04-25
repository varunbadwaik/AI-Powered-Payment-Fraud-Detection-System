# =============================================================================
# Dockerfile for AI-Powered Payment Fraud Detection System
# Multi-stage build: train models → serve API + dashboard
# =============================================================================

FROM python:3.11-slim AS base

# Security: run as non-root user
RUN groupadd -r fraudapp && useradd -r -g fraudapp fraudapp

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/sample models/artifacts logs \
    && chown -R fraudapp:fraudapp /app

# =============================================================================
# Stage: Train models (build time)
# =============================================================================
FROM base AS trainer
RUN python -c "from models.train import run_training_pipeline; run_training_pipeline()"

# =============================================================================
# Stage: Production API server
# =============================================================================
FROM base AS api

# Copy trained model artifacts from trainer stage
COPY --from=trainer /app/models/artifacts /app/models/artifacts
COPY --from=trainer /app/data/sample /app/data/sample

USER fraudapp

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health').raise_for_status()"

CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# Stage: Production dashboard
# =============================================================================
FROM base AS dashboard

COPY --from=trainer /app/models/artifacts /app/models/artifacts

USER fraudapp

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "frontend/app.py", \
     "--server.port", "8501", \
     "--server.headless", "true", \
     "--theme.base", "dark"]

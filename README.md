# 🛡️ AI-Powered Payment Fraud Detection System

A production-ready, real-time fraud detection system that uses ensemble machine learning to analyze financial transactions, provide risk scores, and deliver explainable AI insights through an interactive dashboard.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [ML Models](#-ml-models)
- [Dashboard](#-dashboard)
- [Testing](#-testing)
- [Docker Deployment](#-docker-deployment)
- [Configuration](#-configuration)
- [Security Considerations](#-security-considerations)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Ensemble ML** | Isolation Forest + Logistic Regression for robust fraud detection |
| ⚡ **Real-time API** | Low-latency RESTful API with FastAPI |
| 📊 **Interactive Dashboard** | Streamlit-powered monitoring with 5 chart types |
| 🧠 **Explainable AI** | Per-prediction explanations of why transactions were flagged |
| 🔐 **PCI-DSS Aware** | Security best practices and data privacy by design |
| 📦 **Docker Ready** | Multi-stage Dockerfile + Docker Compose |
| ✅ **Fully Tested** | Unit, integration, and end-to-end test suites |

---

## 🏗️ Architecture

```
┌─────────────────────┐     ┌───────────────────────────┐     ┌──────────────────┐
│   Streamlit         │────▶│   FastAPI Backend          │────▶│   SQLite DB      │
│   Dashboard         │◀────│                           │     │                  │
│   (Port 8501)       │     │  ┌─────────────────────┐  │     └──────────────────┘
└─────────────────────┘     │  │  Isolation Forest    │  │
                            │  │  (Anomaly Detection) │  │
                            │  └─────────────────────┘  │
                            │  ┌─────────────────────┐  │
                            │  │  Logistic Regression │  │
                            │  │  (Classification)    │  │
                            │  └─────────────────────┘  │
                            │  ┌─────────────────────┐  │
                            │  │  Explainability      │  │
                            │  │  Module              │  │
                            │  └─────────────────────┘  │
                            │         (Port 8000)       │
                            └───────────────────────────┘
```

**Data Flow:**
```
User Input → Pydantic Validation → Feature Engineering → Model Ensemble → Risk Score + Explanation → DB Storage → Dashboard
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip

### 3-Step Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train ML models (generates synthetic data + trains both models)
python run.py --mode train

# 3. Start the full system (API + Dashboard)
python run.py --mode all
```

Then open:
- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

### Run Services Individually

```bash
# Start API server only
python run.py --mode api

# Start dashboard only (requires API to be running)
python run.py --mode dashboard
```

---

## 📁 Project Structure

```
├── backend/                  # FastAPI backend
│   ├── main.py              # App entrypoint with CORS & lifespan
│   ├── api/
│   │   ├── routes.py        # API endpoint definitions
│   │   └── schemas.py       # Pydantic request/response models
│   ├── database/
│   │   ├── connection.py    # Async SQLite connection manager
│   │   └── models.py        # Database CRUD operations
│   └── services/
│       └── prediction.py    # Prediction orchestration service
├── frontend/                 # Streamlit dashboard
│   ├── app.py               # Main dashboard app
│   └── components/
│       ├── charts.py        # Plotly chart components
│       ├── forms.py         # Transaction input form
│       └── indicators.py    # Risk indicator widgets
├── models/                   # ML model layer
│   ├── train.py             # Training pipeline
│   ├── inference.py         # Model loading & prediction
│   ├── feature_engineering.py # Feature extraction
│   ├── explainability.py    # XAI module
│   └── artifacts/           # Saved model files (.joblib)
├── data/                     # Data pipeline
│   ├── generator.py         # Synthetic data generator
│   ├── preprocessor.py      # Data cleaning & scaling
│   └── sample/              # Generated CSV files
├── utils/                    # Shared utilities
│   ├── config.py            # Configuration loader
│   ├── logger.py            # Structured logging
│   └── constants.py         # Project-wide constants
├── tests/                    # Test suites
│   ├── test_api.py          # API endpoint tests
│   ├── test_model.py        # ML model tests
│   └── test_pipeline.py     # End-to-end pipeline tests
├── run.py                    # CLI launcher
├── requirements.txt          # Python dependencies
├── Dockerfile                # Multi-stage Docker build
├── docker-compose.yml        # Service orchestration
└── .env.example              # Environment variable template
```

---

## 📖 API Documentation

### POST `/api/v1/predict`

Evaluate a transaction for fraud risk.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 4999.99,
    "merchant_category": "online_retail",
    "transaction_hour": 2,
    "day_of_week": 6,
    "location_distance_km": 3500.0,
    "is_international": true,
    "card_present": false,
    "velocity_last_1h": 12,
    "avg_amount_30d": 65.00
  }'
```

**Response:**
```json
{
  "transaction_id": "TXN-A1B2C3D4E5F6",
  "fraud_probability": 0.8723,
  "risk_level": "High",
  "model_scores": {
    "isolation_forest_score": 0.8145,
    "logistic_regression_score": 0.9108
  },
  "explanation": "The transaction amount of $4,999.99 is unusually high, increasing fraud risk. The transaction occurred at hour 2 (late night/early morning), which increased the risk score. The transaction location is 3500 km from the cardholder's typical area, which increased the risk score.",
  "top_risk_factors": [
    {"feature": "Transaction Amount ($)", "contribution": 0.4521},
    {"feature": "Distance from Home (km)", "contribution": 0.3892},
    {"feature": "Hour of Day", "contribution": 0.1234}
  ],
  "timestamp": "2026-04-24T06:00:00Z"
}
```

### GET `/api/v1/health`

```bash
curl http://localhost:8000/api/v1/health
```

### GET `/api/v1/transactions?limit=10&risk_level=High`

```bash
curl http://localhost:8000/api/v1/transactions?limit=10
```

### GET `/api/v1/stats`

```bash
curl http://localhost:8000/api/v1/stats
```

### GET `/api/v1/feature-importance`

```bash
curl http://localhost:8000/api/v1/feature-importance
```

Full interactive API docs available at **http://localhost:8000/docs** (Swagger UI).

---

## 🤖 ML Models

### Isolation Forest (Primary)

- **Type**: Unsupervised anomaly detection
- **Approach**: Randomly partitions feature space; anomalies require fewer partitions to isolate
- **Strengths**: Detects novel fraud patterns not seen in training data
- **Parameters**: 200 estimators, 3% contamination, auto max_samples

### Logistic Regression (Secondary)

- **Type**: Supervised binary classification
- **Approach**: Learns a linear decision boundary with probability calibration
- **Strengths**: Interpretable coefficients, calibrated probability output
- **Parameters**: Balanced class weights, L2 regularization

### Ensemble Strategy

- **Weighted Average**: 40% Isolation Forest + 60% Logistic Regression
- **Risk Levels**:
  - 🟢 **Low** (< 0.30): Auto-approve
  - 🟡 **Medium** (0.30 – 0.70): Manual review recommended
  - 🔴 **High** (> 0.70): Block and investigate

### Features (10 engineered features)

| Feature | Description |
|---------|-------------|
| `amount` | Transaction amount in USD |
| `merchant_category_encoded` | Encoded merchant type |
| `transaction_hour` | Hour of day (0–23) |
| `day_of_week` | Day (0=Mon, 6=Sun) |
| `location_distance_km` | Distance from typical location |
| `is_international` | Cross-border flag |
| `card_present` | Physical card present flag |
| `velocity_last_1h` | Transactions in last hour |
| `avg_amount_30d` | 30-day average amount |
| `amount_deviation` | Deviation from average |

---

## 🖥️ Dashboard

The Streamlit dashboard provides three pages:

### 🔍 Transaction Analyzer
- Submit individual transactions for real-time analysis
- Quick-fill presets: Normal, Suspicious, and Likely Fraud scenarios
- Color-coded risk badge with fraud probability gauge
- AI explanation with top risk factors

### 📊 Monitoring Dashboard
- KPI cards: total transactions, flagged count, fraud rate, avg score
- Risk distribution donut chart
- Fraud score histogram with threshold indicators
- Transaction risk timeline
- Amount vs risk scatter plot
- Global feature importance chart
- Recent transactions table

### 🧠 Model Info
- System architecture diagram
- Model parameters and ensemble strategy
- Feature importance chart
- Training metrics with confusion matrices

---

## ✅ Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_api.py -v
python -m pytest tests/test_model.py -v
python -m pytest tests/test_pipeline.py -v

# Run with coverage
python -m pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Using Docker Directly

```bash
# Build API image
docker build --target api -t fraud-api .

# Run API
docker run -p 8000:8000 fraud-api

# Build dashboard image
docker build --target dashboard -t fraud-dashboard .

# Run dashboard
docker run -p 8501:8501 -e BACKEND_URL=http://host.docker.internal:8000 fraud-dashboard
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and adjust:

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | API listen address |
| `API_PORT` | `8000` | API port |
| `DB_PATH` | `data/fraud_detection.db` | SQLite database path |
| `MODEL_DIR` | `models/artifacts` | Trained model artifacts |
| `LOG_LEVEL` | `INFO` | Logging level |
| `NUM_TRANSACTIONS` | `10000` | Synthetic data size |
| `FRAUD_RATIO` | `0.03` | Fraud proportion |
| `STREAMLIT_PORT` | `8501` | Dashboard port |
| `BACKEND_URL` | `http://localhost:8000` | API URL for frontend |

---

## 🔐 Security Considerations

This system is built with PCI-DSS awareness:

| Requirement | Implementation |
|-------------|---------------|
| **Req 3**: Protect stored data | System uses only synthetic data; no real PANs/CVVs stored |
| **Req 6**: Secure coding | Pydantic input validation, parameterized SQL queries |
| **Req 10**: Logging & monitoring | Structured JSON logs for all predictions |
| **Req 8**: Authentication | Not implemented (demo) — add OAuth2/JWT for production |

**For production deployment, additionally implement:**
- TLS/HTTPS termination
- API rate limiting
- JWT-based authentication
- Input sanitization middleware
- Database encryption at rest
- Network segmentation

---

## 📄 License

This project is for educational and portfolio purposes. Built to demonstrate ML engineering, API design, and production system architecture in the fintech domain.

---

## 🙋 Author

Built as a demonstration of AI-powered fintech systems, suitable for:
- Technical interviews (AI/ML, Backend, Full-stack)
- GitHub portfolio showcase
- Learning resource for fraud detection systems

"""
API endpoint tests for the Fraud Detection System.

Tests the FastAPI backend using httpx TestClient.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /api/v1/health."""

    def test_health_returns_200(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_has_status_field(self, client):
        response = client.get("/api/v1/health")
        data = response.json()
        assert "status" in data
        assert data["status"] in ("healthy", "degraded")

    def test_health_has_version(self, client):
        response = client.get("/api/v1/health")
        data = response.json()
        assert "api_version" in data

    def test_health_has_model_loaded(self, client):
        response = client.get("/api/v1/health")
        data = response.json()
        assert "model_loaded" in data
        assert isinstance(data["model_loaded"], bool)


class TestRootEndpoint:
    """Tests for GET /."""

    def test_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_has_service_name(self, client):
        response = client.get("/")
        data = response.json()
        assert "service" in data
        assert "Fraud" in data["service"]


class TestPredictEndpoint:
    """Tests for POST /api/v1/predict."""

    @pytest.fixture
    def valid_transaction(self):
        return {
            "amount": 150.00,
            "merchant_category": "grocery",
            "transaction_hour": 14,
            "day_of_week": 2,
            "location_distance_km": 5.0,
            "is_international": False,
            "card_present": True,
            "velocity_last_1h": 1,
            "avg_amount_30d": 120.00,
        }

    @pytest.fixture
    def suspicious_transaction(self):
        return {
            "amount": 4999.99,
            "merchant_category": "online_retail",
            "transaction_hour": 2,
            "day_of_week": 6,
            "location_distance_km": 3500.0,
            "is_international": True,
            "card_present": False,
            "velocity_last_1h": 12,
            "avg_amount_30d": 65.00,
        }

    def test_predict_valid_transaction(self, client, valid_transaction):
        """Test that a valid transaction returns a prediction."""
        response = client.post("/api/v1/predict", json=valid_transaction)
        # 200 if models loaded, 503 if not
        assert response.status_code in (200, 503)

        if response.status_code == 200:
            data = response.json()
            assert "fraud_probability" in data
            assert "risk_level" in data
            assert "explanation" in data
            assert 0.0 <= data["fraud_probability"] <= 1.0
            assert data["risk_level"] in ("Low", "Medium", "High")

    def test_predict_invalid_amount_negative(self, client):
        """Validate that negative amounts are rejected."""
        response = client.post("/api/v1/predict", json={
            "amount": -10.00,
            "merchant_category": "grocery",
            "transaction_hour": 14,
        })
        assert response.status_code == 422  # Validation error

    def test_predict_invalid_amount_too_high(self, client):
        """Validate that amounts above limit are rejected."""
        response = client.post("/api/v1/predict", json={
            "amount": 100000.00,
            "merchant_category": "grocery",
            "transaction_hour": 14,
        })
        assert response.status_code == 422

    def test_predict_invalid_merchant(self, client):
        """Validate that unknown merchant categories are rejected."""
        response = client.post("/api/v1/predict", json={
            "amount": 50.00,
            "merchant_category": "invalid_category",
            "transaction_hour": 14,
        })
        assert response.status_code == 422

    def test_predict_invalid_hour(self, client):
        """Validate that invalid hours are rejected."""
        response = client.post("/api/v1/predict", json={
            "amount": 50.00,
            "merchant_category": "grocery",
            "transaction_hour": 25,
        })
        assert response.status_code == 422

    def test_predict_missing_required_fields(self, client):
        """Validate that missing required fields return 422."""
        response = client.post("/api/v1/predict", json={})
        assert response.status_code == 422

    def test_predict_empty_body(self, client):
        """Validate that empty body returns 422."""
        response = client.post("/api/v1/predict")
        assert response.status_code == 422


class TestTransactionsEndpoint:
    """Tests for GET /api/v1/transactions."""

    def test_transactions_returns_200(self, client):
        response = client.get("/api/v1/transactions")
        assert response.status_code == 200

    def test_transactions_has_count(self, client):
        response = client.get("/api/v1/transactions")
        data = response.json()
        assert "transactions" in data
        assert "count" in data

    def test_transactions_respects_limit(self, client):
        response = client.get("/api/v1/transactions?limit=5")
        data = response.json()
        assert len(data["transactions"]) <= 5

    def test_transactions_filter_by_risk(self, client):
        response = client.get("/api/v1/transactions?risk_level=High")
        assert response.status_code == 200


class TestStatsEndpoint:
    """Tests for GET /api/v1/stats."""

    def test_stats_returns_200(self, client):
        response = client.get("/api/v1/stats")
        assert response.status_code == 200

    def test_stats_has_required_fields(self, client):
        response = client.get("/api/v1/stats")
        data = response.json()
        assert "total_transactions" in data
        assert "total_flagged" in data
        assert "fraud_rate" in data

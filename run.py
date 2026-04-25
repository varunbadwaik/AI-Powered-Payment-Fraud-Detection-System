"""
Convenience launcher for the AI-Powered Payment Fraud Detection System.

Usage:
    python run.py --mode train       # Train ML models
    python run.py --mode api         # Start FastAPI backend
    python run.py --mode dashboard   # Start Streamlit frontend
    python run.py --mode all         # Train + start both services
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def train_models():
    """Run the model training pipeline."""
    print("\n" + "=" * 60)
    print("  [ML] Training Fraud Detection Models")
    print("=" * 60 + "\n")

    from models.train import run_training_pipeline

    results = run_training_pipeline()

    print("\n" + "=" * 60)
    print("  [OK] Training Complete!")
    print(f"  Artifacts saved to: {results['artifact_dir']}")
    print(f"  Isolation Forest ROC-AUC: {results['isolation_forest_metrics']['roc_auc']:.4f}")
    print(f"  Logistic Regression ROC-AUC: {results['logistic_regression_metrics']['roc_auc']:.4f}")
    print("=" * 60 + "\n")

    return results


def start_api():
    """Start the FastAPI backend server."""
    print("\n" + "=" * 60)
    print("  [API] Starting FastAPI Backend")
    print("=" * 60 + "\n")

    from utils.config import settings

    subprocess.run(
        [
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", settings.API_HOST,
            "--port", str(settings.API_PORT),
            "--reload",
        ],
        cwd=str(PROJECT_ROOT),
    )


def start_dashboard():
    """Start the Streamlit frontend dashboard."""
    print("\n" + "=" * 60)
    print("  [UI] Starting Streamlit Dashboard")
    print("=" * 60 + "\n")

    from utils.config import settings

    subprocess.run(
        [
            sys.executable, "-m", "streamlit", "run",
            "frontend/app.py",
            "--server.port", str(settings.STREAMLIT_PORT),
            "--server.headless", "true",
            "--theme.base", "dark",
        ],
        cwd=str(PROJECT_ROOT),
    )


def start_all():
    """Train models (if needed), then start both backend and frontend."""
    # Check if models exist
    from utils.config import settings

    model_dir = Path(settings.MODEL_DIR)
    if not (model_dir / "isolation_forest.joblib").exists():
        print("[WARN] No trained models found. Training now...")
        train_models()
    else:
        print("[OK] Trained models found. Skipping training.")

    print("\n[START] Launching both services...\n")

    # Start API in background
    api_process = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", settings.API_HOST,
            "--port", str(settings.API_PORT),
        ],
        cwd=str(PROJECT_ROOT),
    )

    # Give API a moment to start
    time.sleep(3)

    # Start dashboard (foreground)
    try:
        start_dashboard()
    finally:
        api_process.terminate()
        api_process.wait()
        print("\n[STOP] Services stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered Payment Fraud Detection System Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run.py --mode train       # Train ML models
    python run.py --mode api         # Start backend API only
    python run.py --mode dashboard   # Start frontend only
    python run.py --mode all         # Train + start everything
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["train", "api", "dashboard", "all"],
        default="all",
        help="Operation mode (default: all)",
    )

    args = parser.parse_args()

    if args.mode == "train":
        train_models()
    elif args.mode == "api":
        start_api()
    elif args.mode == "dashboard":
        start_dashboard()
    elif args.mode == "all":
        start_all()


if __name__ == "__main__":
    main()

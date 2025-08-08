import sys
import os

# Add the Desktop to sys.path so lloyd_drift_demo is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

# demos/cli_demo/run.py
from lloyd_drift_demo.engine.test_drift_cases import run_all_tests

if __name__ == "__main__":
    run_all_tests()
#!/usr/bin/env python3
"""
Run the Streamlit frontend application.
"""
import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "sds_digest/frontend/app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
    ])


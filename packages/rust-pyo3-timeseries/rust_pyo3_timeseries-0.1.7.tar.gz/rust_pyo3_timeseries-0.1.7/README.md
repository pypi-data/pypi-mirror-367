# rust_pyo3_timeseries

> **High-performance Rust implementations of niche time-series tests, forcasting methods and more, exposed to Python via PyO3.**

This repo collects “missing” econometric and statistical algorithms that aren’t
available in mainstream Python/R libraries.  
The first release ships the **Escanciano–Lobato (2009) heteroskedasticity
proxy test**, written in pure Rust for speed and wrapped as a
pip-installable Python extension.

![CI](https://github.com/mickwise/rust_pyo3_timeseries/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)
![GitHub release (latest by tag)](https://img.shields.io/github/v/release/mickwise/rust_pyo3_timeseries)

---

## 🚀 Quick start (Python)

```bash
# create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # or `.\.venv\Scripts\activate` on Windows

# install directly from the GitHub release/tag
pip install "git+https://github.com/mickwise/rust_pyo3_timeseries.git@v0.1.1
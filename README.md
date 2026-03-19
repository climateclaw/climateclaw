# climateclaw

[![CI](https://github.com/climateclaw/climateclaw/actions/workflows/tests_ci.yml/badge.svg)](https://github.com/climateclaw/climateclaw/actions)
[![PyPI](https://img.shields.io/pypi/v/climateclaw)](https://pypi.org/project/climateclaw/)
[![Python](https://img.shields.io/pypi/pyversions/climateclaw)](https://pypi.org/project/climateclaw/)
[![License: MIT](https://img.shields.io/badge/License-BSD-purple.svg)](LICENSE)

Climate data analysis & statistics — clawing into your data.

## Installation

### Install via PyPI

```bash
pip install climateclaw
```

### Install via Conda

```bash
conda install xarray-prism
```

## Usage

```python
from climateclaw import compute_mean, compute_anomaly, detect_trend

compute_mean([13.1, 14.2, 13.8, 15.0])
# 14.025

compute_anomaly([13.5, 14.1], baseline=[12.0, 12.5, 13.0])
# array([1.17, 1.77])

detect_trend([13.1, 13.4, 13.8, 14.1, 14.5])
# {'slope': 0.35, 'intercept': 12.98, 'r_squared': 0.99, 'p_value': 0.0003}
```

## OpenClaw

```bash
clawhub install climateclaw
```

Or call the bundled script directly:

```bash
./scripts/climate.sh trend "13.1,13.4,13.8,14.1,14.5"
```

## Development

```bash
git clone https://github.com/climateclaw/climateclaw
cd climateclaw
pip install -e ".[dev]"
tox -e test
tox -e lint
```

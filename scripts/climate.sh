#!/usr/bin/env bash
# climate.sh — CLI wrapper around the climateclaw Python package.
# Used by OpenClaw agents to call analysis functions without writing inline Python.
#
# Usage:
#   ./climate.sh mean      '13.1,14.2,13.8'
#   ./climate.sh anomaly   '13.5,14.1' '12.0,12.5,13.0'
#   ./climate.sh trend     '13.1,13.4,13.8,14.1,14.5'

set -euo pipefail

CMD="${1:-}"
shift || true

csv_to_list() {
  # "1.0,2.0,3.0"  →  [1.0, 2.0, 3.0]
  echo "[$(echo "$1" | tr ',' ', ')]"
}

case "$CMD" in
  mean)
    python3 - "$1" <<'EOF'
import sys
from climateclaw import compute_mean
data = list(map(float, sys.argv[1].split(",")))
print(compute_mean(data))
EOF
    ;;
  anomaly)
    python3 - "$1" "$2" <<'EOF'
import sys
from climateclaw import compute_anomaly
data     = list(map(float, sys.argv[1].split(",")))
baseline = list(map(float, sys.argv[2].split(",")))
print(compute_anomaly(data, baseline).tolist())
EOF
    ;;
  trend)
    python3 - "$1" <<'EOF'
import sys, json
from climateclaw import detect_trend
data = list(map(float, sys.argv[1].split(",")))
print(json.dumps(detect_trend(data), indent=2))
EOF
    ;;
  fetch)
    # ./climate.sh fetch <lat> <lon> <start> <end> [variable]
    python3 - "$1" "$2" "$3" "$4" "${5:-temperature_2m_mean}" <<'EOF'
import sys, json
import numpy as np
from climateclaw.fetch import fetch_historical
result = fetch_historical(
    float(sys.argv[1]), float(sys.argv[2]),
    sys.argv[3], sys.argv[4],
    variable=sys.argv[5],
)
result["values"] = result["values"].tolist()
print(json.dumps(result, indent=2))
EOF
    ;;
  *)
    echo "Usage: $0 {mean|anomaly|trend|fetch} <args>" >&2
    echo "  fetch <lat> <lon> <start> <end> [variable]" >&2
    echo "  mean  <csv-values>" >&2
    echo "  anomaly <csv-values> <csv-baseline>" >&2
    echo "  trend <csv-values>" >&2
    exit 1
    ;;
esac
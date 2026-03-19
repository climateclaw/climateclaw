---
name: climateclaw
description: >
  Fetch historical climate data from Open-Meteo (no API key needed) and run
  analysis: compute means, detect anomalies against a baseline period, and
  identify linear warming/cooling trends. Requires the `climateclaw` Python
  package (pip install climateclaw).
metadata:
  emoji: "🌡️"
  requires:
    bins: ["python3"]
    packages: ["climateclaw"]
---

# climateclaw skill

## When to use
- User asks to fetch historical temperature, precipitation, or wind data for a location
- User wants a warming/cooling trend over a period
- User wants anomalies compared to a historical baseline
- User asks for mean climate statistics

## When NOT to use
- Real-time or forecast weather: use `weather` / `weathercli` skill

---

## Functions

### `fetch_historical(lat, lon, start, end, variable)` — pull data from Open-Meteo
No API key required. Returns `dates`, `values` (numpy array), `unit`.

Supported variables:
- `temperature_2m_mean` / `temperature_2m_max` / `temperature_2m_min`
- `precipitation_sum`, `rain_sum`, `snowfall_sum`
- `windspeed_10m_max`
- `et0_fao_evapotranspiration`, `shortwave_radiation_sum`

### `compute_mean(data)` — arithmetic mean
### `compute_anomaly(data, baseline)` — departure from baseline mean
### `detect_trend(data)` — linear trend via OLS -> slope, r², p-value

---

## Quick examples

```bash
# Fetch + mean temperature for Hamburg, last 5 years
python3 -c "
import numpy as np
from climateclaw import fetch_historical, compute_mean
d = fetch_historical(53.5753, 10.0153, '2019-01-01', '2023-12-31')
vals = d['values'][~np.isnan(d['values'])]
print(f'{compute_mean(vals):.2f} {d[\"unit\"]}')
"

# Fetch + trend (annual means) for Paris, 20 years
python3 -c "
import numpy as np, json
from climateclaw import fetch_historical, detect_trend
d = fetch_historical(48.8566, 2.3522, '2004-01-01', '2023-12-31')
dates, vals = d['dates'], d['values']
years = sorted(set(x[:4] for x in dates))
annual = [np.nanmean([v for dt, v in zip(dates, vals) if dt.startswith(y)]) for y in years]
print(json.dumps(detect_trend(annual), indent=2))
"

# Anomaly vs 30-year WMO baseline for Berlin
python3 -c "
import numpy as np
from climateclaw import fetch_historical, compute_anomaly
base = fetch_historical(52.52, 13.405, '1991-01-01', '2020-12-31')
recent = fetch_historical(52.52, 13.405, '2021-01-01', '2023-12-31')
b = base['values'][~np.isnan(base['values'])]
r = recent['values'][~np.isnan(recent['values'])]
anom = compute_anomaly(r, b)
print(f'Mean anomaly: {anom.mean():+.2f} {recent[\"unit\"]}')
"
```

---

## Example — is your city warming?

```bash
python3 << 'PYEOF'
import numpy as np, json
from climateclaw import fetch_historical, detect_trend, compute_mean

CITY   = "Hamburg"
LAT, LON = 53.5753, 10.0153

# Fetch 40 years of daily mean temperature
data = fetch_historical(LAT, LON, "1984-01-01", "2023-12-31")
dates, values = data["dates"], data["values"]
unit = data["unit"]

# Aggregate to annual means
years = sorted(set(d[:4] for d in dates))
annual_means = []
for y in years:
    year_vals = [v for d, v in zip(dates, values) if d.startswith(y) and not np.isnan(v)]
    annual_means.append(float(np.mean(year_vals)))

# Run trend
trend = detect_trend(annual_means)

# Report
coldest = years[int(np.argmin(annual_means))]
warmest = years[int(np.argmax(annual_means))]

print(f"\n  {CITY} — 40-year climate summary")
print(f"   Mean temperature : {compute_mean(annual_means):.2f} {unit}")
print(f"   Coldest year     : {coldest} ({min(annual_means):.2f} {unit})")
print(f"   Warmest year     : {warmest} ({max(annual_means):.2f} {unit})")
print(f"   Warming trend    : {trend['slope']:+.3f} {unit}/year")
print(f"   Over 40 years    : {trend['slope']*40:+.2f} {unit} total")
print(f"   R²               : {trend['r_squared']:.3f}")
print(f"   Significant?     : {'yes ' if trend['p_value'] < 0.05 else 'no ✗'} (p={trend['p_value']:.4f})")
PYEOF
```

Example output:
```
  Hamburg — 40-year climate summary
   Mean temperature : 10.31 °C
   Coldest year     : 1985 (7.94 °C)
   Warmest year     : 2020 (12.67 °C)
   Warming trend    : +0.051 °C/year
   Over 40 years    : +2.04 °C total
   R²               : 0.847
   Significant?     : yes  (p=0.0000)
```

---

## Shell script usage

```bash
./scripts/climate.sh fetch 53.5753 10.0153 2019-01-01 2023-12-31 temperature_2m_mean
./scripts/climate.sh trend "7.94,8.12,8.45,9.1,9.8,10.2"
./scripts/climate.sh mean  "7.94,8.12,8.45,9.1,9.8,10.2"
```

---

## Tips
- Aggregate daily → annual means before running `detect_trend` (daily noise kills signal).
- Use a 30-year WMO baseline (e.g. 1991–2020) for `compute_anomaly`.
- Strip NaN before any analysis: `vals = values[~np.isnan(values)]`.
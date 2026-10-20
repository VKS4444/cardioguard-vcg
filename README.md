# CARDIO_GUARD AI v4.0
### 3-Lead Spatial VCG · 140-Tree Hybrid Edge AI · Real-Time ΔST Ischemia Detection

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![Zero Dependencies](https://img.shields.io/badge/backend-zero%20pip%20installs-brightgreen)]()
[![Dataset](https://img.shields.io/badge/data-PhysioNet%20PTB--XL-informational)](https://physionet.org/content/ptb-xl/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What it does

CardioGuard is a **browser-based cardiac monitoring system** that uses **3-lead Vectorcardiography (VCG)** and a **140-tree hybrid Random Forest** to detect ST-segment ischemia in real time — directly in the browser, with no cloud dependency.

It is designed to outperform single-lead smartwatch ECG by fusing three spatial leads (II, V2, V5) into a 2D VCG loop, enabling detection of lateral, anterior, and inferior wall ischemia that a single lead would miss.

---

## Key Features

| Feature | Detail |
|---|---|
| **3-Lead VCG** | Leads II (inferior), V2 (anterior/posterior), V5 (lateral) fused into a 2D spatial loop |
| **140-Tree Hybrid Forest** | 60 SQI trees (signal quality) + 80 ST trees (ischemia classification) |
| **Real-Time ΔST Baseline** | Personalized baseline calibrated per patient; detects relative shifts, not absolute thresholds |
| **15-Second Dead-Man Switch** | Triggers alert if no signal is received for 15 seconds |
| **PhysioNet PTB-XL Scenarios** | Ships with clinical demo scenarios derived from PTB-XL records |
| **Multi-language UI** | English, Tamil (தமிழ்), Hindi (हिन्दी), Telugu (తెలుగు) |
| **SQLite Telemetry** | Local persistence — no external database, no cloud |
| **Zero pip installs** | Backend runs on Python standard library only |

---

## Architecture

```
┌─────────────────────────────────────────┐
│           Browser (index.html)           │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Live ECG  │  │ VCG Loop │  │ Tree   │ │
│  │ Scope    │  │ Compass  │  │ Builder│ │
│  └──────────┘  └──────────┘  └────────┘ │
│         JavaScript Edge AI Engine        │
│    140-tree RF (SQI + ST classification) │
└──────────────┬──────────────────────────┘
               │ HTTP POST /api/telemetry
               │ GET  /api/health
┌──────────────▼──────────────────────────┐
│         backend.py (Python stdlib)       │
│  http.server · sqlite3 · PORT 8000      │
│  ┌───────────────────────────────────┐  │
│  │  cardioguard_v4.db (SQLite)        │  │
│  │  telemetry_logs · model_state      │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## Quickstart

### Prerequisites
- Python 3.8 or higher (no extra packages needed)
- Any modern browser (Chrome / Firefox / Edge)

### Run

```bash
git clone https://github.com/<your-username>/cardioguard-vcg.git
cd cardioguard-vcg
python backend.py
```

The backend will:
1. Create `cardioguard_v4.db` locally (SQLite — **never commit this file**)
2. Start a server at `http://127.0.0.1:8000`
3. Open `index.html` in your default browser automatically

---

## Project Structure

```
cardioguard-vcg/
├── index.html          # Full frontend: ECG scope, VCG compass, tree builder, UI
├── backend.py          # Python stdlib HTTP + SQLite server (zero pip installs)
├── requirements.txt    # No runtime deps; optional analysis libs listed
├── .gitignore          # Excludes *.db, patient data, venv, etc.
├── LICENSE             # MIT
├── docs/
│   └── architecture.md # System design notes
└── assets/             # Static assets (icons, screenshots)
```

---

## How the VCG Works

A **Vectorcardiogram (VCG)** represents the heart's electrical activity as a moving vector in 2D/3D space.

CardioGuard derives a 2D spatial VCG loop from three orthogonal-ish leads:

```
VCG_x = Lead V5   (lateral component)
VCG_y = Lead II   (inferior component)
ST magnitude = √(ΔST_II² + ΔST_V2² + ΔST_V5²)
```

The circular "safe zone" on the compass represents **|ΔST| < 0.10 mV**. When the vector exits this zone, ischemia is flagged and the triage modal fires.

### Why 3 leads beat 1

| Condition | Lead II alone | Lead II + V2 + V5 |
|---|---|---|
| Inferior STEMI | ✅ Detected | ✅ Detected |
| Posterior MI | ❌ Missed | ✅ V2 reciprocal change |
| Lateral STEMI | ❌ Missed | ✅ V5 elevation |
| Noise / artifact | ❌ False positive | ✅ SQI trees filter it |

---

## Dataset

Demo scenarios are derived from the **PhysioNet PTB-XL** dataset:

> Wagner, P., et al. (2020). PTB-XL, a large publicly available electrocardiography dataset. *Scientific Data*, 7, 154. [https://doi.org/10.1038/s41597-020-0495-6](https://doi.org/10.1038/s41597-020-0495-6)

The raw `.mat` / `.hea` files are **not included** in this repository. To reproduce the demo data, download the dataset from [PhysioNet](https://physionet.org/content/ptb-xl/).

---

## API Reference

### `GET /api/health`
Returns backend status.
```json
{ "status": "ONLINE", "db": "cardioguard_v4.db" }
```

### `POST /api/telemetry`
Persists a telemetry event and model state snapshot.
```json
{
  "entry": { "id": "abc123", "type": "ALERT", "payload": { ... } },
  "state": { "sqiTrees": 60, "stTrees": 80, "windowsTrained": 60000,
              "baseII": 0.02, "baseV2": -0.01, "baseV5": 0.00 }
}
```

---

## Privacy & Data

> ⚠️ **This project does not store or transmit any real patient data.**
> The SQLite database (`cardioguard_v4.db`) is local-only and is excluded from version control.
> All demo ECG waveforms are synthetically generated from published PTB-XL statistical parameters.

---

## Author

**Koushik Subbiah** — [vkoushiksubbiah@gmail.com](mailto:vkoushiksubbiah@gmail.com)

Built for a hackathon. Contributions welcome.

---

## License

[MIT](LICENSE)

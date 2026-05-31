# AI-Powered Threat Detection SOC

> Upgraded an Azure Mini SOC from static alert rules to a machine learning 
> threat classification system. The model analyzes network flows in real time 
> and feeds predictions directly into a REST API that a SOC team can query.

---

## Results

| Metric | Score |
|--------|-------|
| Accuracy | 99.98% |
| F1 Score | 0.9998 |
| Precision | 1.0000 |
| Recall | 0.9997 |
| False Positives | ~0 |
| Training Samples | 177,011 |
| Test Samples | 44,253 |
| API Response Time | <100ms |

---

## Architecture

```
CICIDS 2017 Network Traffic (221K flows)
        |
        v
Feature Engineering + StandardScaler
        |
        v
Random Forest Classifier (100 trees)
        |
        v
Flask REST API (/predict, /alerts, /stats)
        |
        v
Azure Sentinel Log Analytics
```

---

## What This Does

Traditional SOC alert systems use hand-written rules to detect threats.
If attackers change their behavior slightly, the rules miss them.

This system trains a Random Forest model on 221,264 real network flows
from the CICIDS 2017 dataset. The model learns the statistical patterns
of DDoS attacks across 77 network features simultaneously.

**Key upgrade over static rules:**
- Static rules: flag if packets/second > X
- This model: learns the combination of 77 features that together
  indicate an attack, catching patterns no single threshold would catch

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and endpoint list |
| GET | `/health` | Health check |
| POST | `/predict` | Submit network flow, get threat prediction |
| GET | `/alerts` | View all detected threats |
| GET | `/stats` | Detection statistics |
| POST | `/reset` | Clear alert log |
| GET | `/features` | List of expected feature names |

### Example Request
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [0.5, 100, 50, ...]}'
```

### Example Response
```json
{
  "id": 1,
  "timestamp": "2026-05-31T09:00:00",
  "prediction": "DDoS",
  "threat_detected": true,
  "confidence_pct": 99.97,
  "severity": "CRITICAL",
  "probabilities": {
    "Benign": 0.03,
    "DDoS": 99.97
  }
}
```

---

## Dataset

**CICIDS 2017** — Canadian Institute for Cybersecurity
- 221,264 real network flow records
- 77 features per flow
- Labels: Benign (93,250) and DDoS (128,014)
- Zero missing values, zero infinite values

---

## Project Structure

```
ai-threat-detection-soc/
├── app.py                           # Flask REST API
├── test_api.py                      # API test suite
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Excludes large model files
├── data/
│   └── DDoS-Friday-no-metadata.parquet
├── models/
│   └── threat_detection_model.pkl   # Trained Random Forest (1.5MB)
├── notebooks/
│   ├── 00-project-summary.ipynb     # Full project summary with charts
│   ├── 01-data-exploration.ipynb    # EDA — 221K rows analyzed
│   ├── 02-data-preprocessing.ipynb  # Cleaning, scaling, splitting
│   ├── 03-model-training.ipynb      # Model training and evaluation
│   └── 04-api-demonstration.ipynb   # Live API testing on real data
└── outputs/
    ├── 01-class-distribution.png    # Traffic distribution chart
    ├── 02-feature-distributions.png # Feature analysis
    ├── 03-confusion-matrix.png      # Model evaluation
    ├── 03-feature-importance.png    # Top 15 detection features
    └── 03-model-results.json        # Performance metrics
```

---

## How to Run

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Start the API:**
```bash
python app.py
```

**3. Test it:**
```bash
python test_api.py
```

**4. Run notebooks in order:**
- 00-project-summary
- 01-data-exploration
- 02-data-preprocessing
- 03-model-training
- 04-api-demonstration

---

## Tech Stack

**ML:** Python · scikit-learn · pandas · NumPy
**API:** Flask · REST
**Security:** Azure Sentinel · CICIDS 2017
**Tools:** Jupyter · Git · GitHub

---

## Key Findings

- **Top detection feature:** Flow Packets/s — DDoS attacks send packets
  at dramatically higher rates than normal traffic
- **Perfect precision:** Zero false alarms — a SOC analyst would never
  chase a benign alert from this system
- **Speed:** API responds in under 100ms — fast enough for real-time
  network monitoring at scale

---

*M.S. Cybersecurity Engineering — University of San Diego (GPA: 4.0)*
*Part of an AI/ML Security Portfolio Sprint*
*[LinkedIn](https://linkedin.com/in/jacob-cudiamat) · [Portfolio](https://jkcudiamat.github.io)*
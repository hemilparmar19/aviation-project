# ✈️ Aviation Safety Intelligence Platform

> Third Year Data Science Project — Trend Analysis of Global Airplane Accidents (2015–2025)

---

## 🚀 Quick Start (Run Locally)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/aviation-accident-analysis.git
cd aviation-accident-analysis
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run pages/1_Home.py
```

### 4. Open in browser
```
http://localhost:8501
```

---

## 📁 Project Structure

```
aviation-accident-analysis/
│
├── app.py                          ← Main entry point
├── requirements.txt                ← Python dependencies
├── README.md
│
├── pages/
│   ├── 1_Home.py                   ← Landing page with KPIs & charts
│   ├── 2_Dashboard.py              ← Full interactive dashboard (3 tabs)
│   ├── 3_Accident_Explorer.py      ← Search & filter accidents (Day 2)
│   ├── 4_Risk_Predictor.py         ← ML risk prediction (Day 2)
│   ├── 5_Trend_Forecast.py         ← 2026-2027 forecasting (Day 3)
│   ├── 6_Geographic_Analysis.py    ← Interactive map (Day 3)
│   └── 7_Report_Generator.py       ← PDF report generator (Day 4)
│
├── data/
│   ├── accidents_main.csv           ← Main accident dataset (Sheet1/EDA2.0)
│   ├── country_crash_risk.csv       ← Country crash risk scores
│   ├── country_high_risk_probability.csv  ← High risk probabilities
│   └── country_risk_weighted_forecast.csv ← Weighted risk forecast
│
├── utils/
│   ├── data_loader.py              ← All DAX measures recreated in Python
│   ├── charts.py                   ← Reusable Plotly chart functions
│   └── helpers.py                  ← Formatting & utility functions
│
├── assets/
│   └── style.css                   ← Dark aviation theme
│
└── models/
    └── (ML models saved here)
```

---

## 📊 Dataset

| Table | Description | Rows |
|-------|-------------|------|
| `accidents_main.csv` | Main accident records | 2,596 |
| `country_crash_risk.csv` | Crash risk scores per country | 78 |
| `country_high_risk_probability.csv` | High-risk probability per country | 78 |
| `country_risk_weighted_forecast.csv` | Weighted overall risk per country | 78 |

### Main Table Columns
- `acc._date` — Accident date
- `year`, `month` — Extracted time components
- `aircraft_category` — 7 categories (Commercial Jet, Private, Cargo, etc.)
- `fat.` — Fatality count
- `Fatality_Severity` — Non-Fatal / Low / Medium / High
- `dmg_clean` — Damage level (Substantial / Destroyed / Minor)
- `Damage_Severity` — Numeric damage score (0–3)
- `country_clean` — Country name
- `reason_clean` — Accident cause (12 categories)

---

## 🧮 DAX Measures Recreated in Python

All Power BI DAX measures are faithfully recreated in `utils/data_loader.py`:

| DAX Measure | Python Implementation |
|-------------|----------------------|
| `Total Accidents` | `len(df)` |
| `Total Fatalities` | `df["fat."].sum()` |
| `Fatal Accident %` | `(df[fat.>0].shape[0] / len(df)) * 100` |
| `Fatality Rate` | `total_fatalities / total_accidents` |
| `Damage Severity Index` | `df["Damage_Severity"].mean()` |
| `Accidents YOY %` | `pct_change()` on yearly groupby |
| `High Severity Accidents` | `df[Fatality_Severity=="High"].count()` |
| `Highest Risk Country` | `risk_weighted_df.overall_risk_score.idxmax()` |
| `Avg High Risk Probability (Weighted)` | Weighted average by total_accidents |
| `Cause Contribution %` | `cause_count / total * 100` |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Charts | Plotly Express + Graph Objects |
| Data | Pandas + NumPy |
| ML (Day 2) | Scikit-learn (Random Forest) |
| Forecasting (Day 3) | Scikit-learn Linear Regression |
| Maps | Plotly Choropleth + Folium |
| Reports (Day 4) | ReportLab |
| Deployment | Streamlit Cloud (free) |

---

## 🌐 Deployment (Streamlit Cloud)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Select repository → `app.py` as main file
5. Click **Deploy**

Your app will be live at:
`https://YOUR_APP_NAME.streamlit.app`

---

## 👥 Team

| Name | Role |
|------|------|
| Person 1 | Frontend, UI/UX, Visualization |
| Person 2 | Data Pipeline, ML Models, Deployment |

---

## 🎓 Academic Context

- **Degree:** Third Year — Data Science
- **Project:** Trend Analysis of Global Airplane Accidents
- **Dataset:** 2,596 accidents across 100+ countries (2015–2025)
- **Domain:** Data Science — Dashboarding + ML
# aviation-accident-analysis
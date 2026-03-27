# 🎓 WellCampus — Business Validation Analytics Dashboard

A Streamlit dashboard for validating the **WellCampus** B2B Mental Health Platform startup idea.

## 📁 Files Included
| File | Description |
|------|-------------|
| `app.py` | Main Streamlit dashboard |
| `wellcampus_raw_data.csv` | Synthetic raw dataset (350 rows, 25 columns) |
| `wellcampus_cleaned_data.csv` | Cleaned & transformed dataset (336 rows, 31 columns) |
| `requirements.txt` | Python dependencies |

## 🚀 How to Run on Streamlit Cloud

1. Upload all files to a **GitHub repository**
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Click **"New App"** → select your repo
4. Set **Main file path** = `app.py`
5. Click **Deploy**

## 💻 Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📊 Dashboard Pages
1. **Overview** — KPI metrics, pipeline stage distribution, revenue by source
2. **Descriptive Statistics** — Summary stats, distributions, histograms
3. **Correlation Analysis** — Heatmap, scatter plots, correlation insights
4. **EDA: Sales Pipeline** — Conversion rates, deal values, pipeline duration
5. **Student Wellness Metrics** — Stress scores, NPS, counseling utilization
6. **Data Cleaning Log** — Step-by-step cleaning documentation + download buttons

## 🎯 Business Idea
**WellCampus** is a B2B SaaS mental health & wellness platform sold to colleges and universities across India. Institutions buy annual/semester subscriptions and offer the platform to their students for counseling booking, stress tracking, meditation, and peer support.

## 📋 Assignment Coverage
- ✅ **Task 1** — Synthetic dataset (350 rows, 25 columns, full sales pipeline)
- ✅ **Task 2** — Data cleaning & transformation (6 documented steps, 5 derived features)
- ✅ **Task 3** — 15+ EDA graphs with business insights (correlation, distribution, pipeline analysis)

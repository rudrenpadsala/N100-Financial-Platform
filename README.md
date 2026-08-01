# N100 Financial Analytics Dashboard

A Streamlit-based financial analytics platform for analyzing Nifty 100 companies using financial statements, valuation metrics, sector analytics, and interactive dashboards.

---

# Features

- Dashboard Overview
- Company Profile
- Stock Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation Map
- Annual Reports
- Valuation Module
- CSV & Excel Export
- Interactive Plotly Charts

---

# Project Structure

```
N100-Financial-Platform/

│
├── src/
│   ├── analytics/
│   │      valuation.py
│   │
│   └── dashboard/
│          app.py
│          pages/
│          utils/
│
├── db/
│      nifty100.db
│
├── output/
│      valuation_summary.xlsx
│      valuation_flags.csv
│
├── requirements.txt
│
└── README.md
```

---

# Installation

Clone repository

```bash
git clone <repository-url>
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Run Dashboard

Run the Streamlit application

```bash
streamlit run src/dashboard/app.py
```

Dashboard will open at

```
http://localhost:8501
```

---


---

# Dashboard Screens

## 1. Dashboard

Provides an overview of the N100 Financial Analytics platform with key financial KPIs, sector distribution, company statistics, and summary insights.

**Features**
- KPI Cards
- Sector Distribution
- Company Statistics
- Financial Overview
- Interactive Charts

**Screenshot**

*(Add Dashboard Screenshot Here)*

---

## 2. Company Profile

Displays complete financial information for an individual company including financial statements, key ratios, historical trends, and business information.

**Features**
- Company Search
- Company Details
- ROE & ROCE
- Revenue vs Net Profit Chart
- Balance Sheet
- Cash Flow
- Financial Summary

**Screenshot**

*(Add Company Profile Screenshot Here)*

---

## 3. Stock Screener

Allows users to filter companies using financial metrics and export the results.

**Features**
- Financial Filters
- Sector Filter
- Company Search
- Dynamic Sorting
- CSV Download
- Excel Download

**Screenshot**

*(Add Screener Screenshot Here)*

---

## 4. Peer Comparison

Compare a selected company with other companies in the same peer group.

**Features**
- Peer Selection
- KPI Comparison
- Radar Chart
- Company Comparison Table

**Screenshot**

*(Add Peer Comparison Screenshot Here)*

---

## 5. Trend Analysis

Visualizes historical financial performance across multiple years.

**Features**
- Company Search
- Multi-Metric Selection
- Trend Charts
- YoY Analysis

**Screenshot**

*(Add Trend Analysis Screenshot Here)*

---

## 6. Sector Analysis

Compares companies within sectors using financial performance and profitability metrics.

**Features**
- Bubble Chart
- Sector KPIs
- Revenue vs ROE
- Company Rankings
- CSV Export

**Screenshot**

*(Add Sector Analysis Screenshot Here)*

---

## 7. Capital Allocation

Displays capital allocation strategies using an interactive treemap.

**Features**
- Treemap Visualization
- Allocation Categories
- Company Listing
- Pattern Analysis

**Screenshot**

*(Add Capital Allocation Screenshot Here)*

---

## 8. Annual Reports

Provides quick access to annual reports for all companies.

**Features**
- Company Search
- Annual Report Links
- PDF Access
- Missing Report Detection

**Screenshot**

*(Add Annual Reports Screenshot Here)*

---

# Technologies Used

- Python
- Streamlit
- Pandas
- SQLite
- Plotly
- OpenPyXL

---

# Data Sources

- Financial Ratios
- Profit & Loss
- Balance Sheet
- Cash Flow
- Market Capitalization
- Sector Information

---

# Deliverables

- Interactive Dashboard
- Stock Screener
- Company Analytics
- Sector Analytics
- Valuation Module
- CSV Export
- Excel Export


---

# Sprint Review

## Demo Checklist

The following features were demonstrated during the Sprint 4 review.

| Module | Status |
|---------|--------|
| Dashboard Home | ✅ |
| Company Profile | ✅ |
| Stock Screener | ✅ |
| Peer Comparison | ✅ |
| Trend Analysis | ✅ |
| Sector Analysis | ✅ |
| Capital Allocation | ✅ |
| Annual Reports | ✅ |
| Valuation Module | ✅ |
| CSV Export | ✅ |
| Excel Export | ✅ |

---

# Quality Assurance

The dashboard successfully passed the following QA tests.

| Test | Status |
|------|--------|
| Application Startup | ✅ Pass |
| Dashboard Navigation | ✅ Pass |
| Company Profile | ✅ Pass |
| Stock Screener | ✅ Pass |
| Peer Comparison | ✅ Pass |
| Trend Analysis | ✅ Pass |
| Sector Analysis | ✅ Pass |
| Capital Allocation | ✅ Pass |
| Annual Reports | ✅ Pass |
| CSV Download | ✅ Pass |
| Excel Download | ✅ Pass |
| Missing Data Handling | ✅ Pass |
| Responsive Layout | ✅ Pass |
| Performance Testing | ✅ Pass |

---

# Performance

| Metric | Result |
|--------|--------|
| Dashboard Startup | < 5 Seconds |
| Company Profile | < 3 Seconds |
| Stock Screener | Fast |
| Charts | Responsive |
| Database Queries | Cached |

---

# Future Improvements

Possible enhancements for future sprints:

- Authentication and user login
- Portfolio tracking
- Watchlist functionality
- AI-based stock recommendations
- Live NSE/BSE market data integration
- Mobile responsive optimization
- Dark mode
- PDF report generation
- Portfolio comparison dashboard
- Cloud deployment

---

# Author

**Name:** Rudren Padsala

**Project:** N100 Financial Analytics Dashboard

**Technology Stack**

- Python
- Streamlit
- SQLite
- Pandas
- Plotly
- OpenPyXL

---

# License

This project was developed for educational and internship purposes.

---

# Project Status

## Sprint 4 Completed Successfully ✅

All planned features, testing, documentation, and deliverables have been completed successfully.

Project Status:

**Completed**
# Churn Analysis & Customer Intelligence

An end-to-end churn analytics project for an OTT-style subscription business — connecting a relational SQLite database to Python, cleaning and joining multi-table subscriber data, engineering churn features, computing KPIs, and visualizing customer behavior with Matplotlib and Seaborn.

Built as a hands-on portfolio project to practice the full analyst workflow: **SQL → Python → EDA → visualization → business insight.**

## Project Overview

The dataset simulates a subscription platform with three related tables:

| Table | Contents |
|---|---|
| `db_customer` | Customer demographics — country, state, gender, date of birth |
| `db_subscription` | Subscription details — plan type, contract type, monthly charges, CLTV, churn score, cancellation info |
| `db_support` | Customer support history — complaints, escalations, CSAT scores |

The goal is to identify **who** is churning, **why**, and **when** they're most at risk, then translate that into KPIs and action items a growth or retention team could actually use.

## What's in this repo

| File | Description |
|---|---|
| `churn_analysis.ipynb` | Main analysis notebook — data import, cleaning, feature engineering, KPIs, and visualizations |
| `customer_churn.db` | SQLite database with the three source tables |
| `customer_churn_data_raw.xlsx` | Raw data (same tables) as an Excel workbook, in case you'd rather rebuild the SQLite DB yourself |
| `Churn_Analysis_Customer_Intelligence.pptx` | Slide deck summarizing the project, roadmap, and insights |

## Tech Stack

- **Python** — pandas, numpy
- **SQL** — sqlite3 (relational queries, joins, aggregation)
- **Visualization** — matplotlib, seaborn
- **Environment** — Jupyter Notebook

## Workflow

1. **Connect & Import** — load the SQLite database into Python with `sqlite3` + `pandas`, or rebuild it from the raw Excel file
2. **Data Cleaning** — rename/drop columns, fix data types (dates), standardize categorical values (e.g. gender labels), impute missing values (e.g. filling missing `country` from `state`)
3. **Feature Engineering** — derive `churn_flag` from cancellation dates, `tenure_days`, and a 3-tier `churn_risk` label (low / med / high) from churn score
4. **Joining** — merge customer, subscription, and support tables on `customerid` (de-duplicating support records first)
5. **KPI Calculation** — churn rate, retention rate, ARPU, revenue at risk, escalation rate, complaints per customer, and the correlation between escalations and churn
6. **Visualization** — monthly churn trend, churn rate by plan type and by state, a correlation heatmap, pairplots, and a multi-dimensional `catplot` (plan type × monthly charges × gender × churn risk)
7. **Reporting** — key findings distilled into a presentation for a non-technical audience

## Key Findings

- **Overall churn rate: 28.57%** (retention: 71.43%)
- **Churn is heavily concentrated in the Basic plan (60%)**, vs. 22.2% for Standard and only 14.3% for Premium
- **ARPU: ₹18.85**, with **₹73.94** in monthly revenue at risk from already-churned customers
- **Escalation rate: 19.05%**, and escalations correlate strongly with churn (**r = 0.77**) — customers who escalate a complaint are far more likely to leave
- **Average customer tenure: ~1,452 days**, with **0.43 average complaints per customer**

> Note: this is a compact, hand-curated sample dataset (21 customers) built for learning and portfolio purposes — the workflow and KPI logic are designed to scale directly to a larger production dataset.

## Possible Extensions

A few analyses were deliberately left as exercises for further practice:
- Churn rate broken out by state and by contract type, alongside revenue and customer-count impact
- Customer age (from date of birth) as an additional churn driver
- A proper predictive churn model (e.g. logistic regression or gradient boosting) on top of the existing feature set

## Author

**Shubham Verma**

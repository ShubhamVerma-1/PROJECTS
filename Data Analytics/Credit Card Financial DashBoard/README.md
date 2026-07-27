# Credit Card Financial Dashboard

An interactive Power BI dashboard that turns raw credit card transaction and customer data into a weekly-refreshable financial report — built end-to-end from a SQL database through DAX measures to two linked dashboard pages.

## Project Objective

To build a credit card financial dashboard that gives stakeholders real-time visibility into revenue, transactions, and customer behavior — and supports week-over-week tracking as new data lands, rather than a one-off static report.

## Data Model

Data is loaded into a PostgreSQL database (`ccdb`) as two related tables, joined on `Client_Num`:

| Table | Contents |
|---|---|
| `cc_detail` | One row per customer per week — card category, annual fees, activation status, acquisition cost, credit limit, revolving balance, transaction amount/count, utilization ratio, channel (chip/swipe/online), expenditure type, interest earned, delinquency flag |
| `cust_detail` | One row per customer — age, gender, dependents, education, marital status, state, home ownership, job, income, and a customer satisfaction score |

## Repo Contents

| File | Description |
|---|---|
| `SQL_Query_-_Financial_Dashboard_Data.sql` | Creates the database/tables and loads the CSVs with `COPY` |
| `credit_card.csv`, `customer.csv` | Base dataset (10,108 customers/records) |
| `cc_add.csv`, `cust_add.csv` | Week 53 data, added after the initial load to simulate a weekly refresh |
| `Credit_Card_Financial_Dashboard-Customer.pdf` | Export of the Customer Report dashboard page |
| `Credit_Card_Financial_Dashboard-Transaction.pdf` | Export of the Transaction Report dashboard page |

## Tech Stack

- **PostgreSQL** — relational storage and data loading
- **Power BI** — data modeling, DAX, dashboard/report building
- **DAX** — calculated columns and measures for grouping and week-over-week comparisons

## Workflow

1. **Create & load the database** — `CREATE TABLE` for `cc_detail` and `cust_detail`, then `COPY` in `credit_card.csv` and `customer.csv`
2. **Simulate a weekly refresh** — load `cc_add.csv` and `cust_add.csv` (Week 53) into the same tables to mimic how a new week of data would arrive in production
3. **Connect Power BI to PostgreSQL** and bring in both tables
4. **Feature engineering in DAX** — bucket customers into age and income groups, and build a `Revenue` measure plus current/previous-week revenue measures for WoW comparisons (see below)
5. **Build two report pages** — a Customer Report and a Transaction Report, each with slicers for quarter, week, card tier, and income group
6. **Summarize findings** into a set of headline insights (below)

### Key DAX measures

```dax
AgeGroup = SWITCH(
    TRUE(),
    cust_detail[Customer_Age] < 30, "20-30",
    cust_detail[Customer_Age] >= 30 && cust_detail[Customer_Age] < 40, "30-40",
    cust_detail[Customer_Age] >= 40 && cust_detail[Customer_Age] < 50, "40-50",
    cust_detail[Customer_Age] >= 50 && cust_detail[Customer_Age] < 60, "50-60",
    cust_detail[Customer_Age] >= 60, "60+",
    "unknown"
)

IncomeGroup = SWITCH(
    TRUE(),
    cust_detail[Income] < 35000, "Low",
    cust_detail[Income] >= 35000 && cust_detail[Income] < 70000, "Med",
    cust_detail[Income] >= 70000, "High",
    "unknown"
)

Revenue = cc_detail[Annual_Fees] + cc_detail[Total_Trans_Amt] + cc_detail[Interest_Earned]

week_num2 = WEEKNUM(cc_detail[Week_Start_Date])

Current_week_Revenue = CALCULATE(
    SUM(cc_detail[Revenue]),
    FILTER(ALL(cc_detail), cc_detail[week_num2] = MAX(cc_detail[week_num2]))
)

Previous_week_Revenue = CALCULATE(
    SUM(cc_detail[Revenue]),
    FILTER(ALL(cc_detail), cc_detail[week_num2] = MAX(cc_detail[week_num2]) - 1)
)
```

## Dashboard Pages

**Customer Report** — total revenue, interest, income, and customer satisfaction score at a glance, plus revenue trend by gender over time, age group breakdown, top 5 states, salary group, dependent count, marital status, and education level. Filterable by quarter, week, income group, and card tier.

**Transaction Report** — total revenue, interest, transaction amount, and transaction count, plus revenue and transaction count by quarter, revenue by card category, revenue by channel (swipe/chip/online), customer acquisition cost by card tier, and revenue broken out by expenditure type, education, and customer job.

## Key Insights

*(Based on the full dataset, including the Week 53 update)*

- **Total revenue: $56.5M** — $45.5M from transactions, $8.0M from interest, and $3.0M from annual fees
- **655,651 transactions** processed across the year
- **Card activation rate (within 30 days): 57.5%**
- **Delinquent account rate: 6.1%**
- **Male customers generate more revenue** ($30.9M) than female customers ($25.6M)
- **Blue and Silver cards drive ~93% of total revenue and transaction volume**, despite being the entry-level tiers — Gold and Platinum contribute the rest
- **Texas, New York, and California together account for ~69% of revenue** — the clearest geographic concentration in the customer base
- Self-employed and business-owner customers are the highest-revenue customer job segments; retirees the lowest

## Possible Extensions

- Automate the weekly refresh (e.g. a scheduled load replacing the manual `cc_add`/`cust_add` step)
- Add a churn/attrition view using the delinquency flag and utilization ratio as early-warning signals
- Break down revenue by age group × income group to spot underserved high-value segments

## Author

**Shubham Verma**

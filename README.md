# Enterprise Banking Data Warehouse

An end-to-end banking data warehouse project built using Python, PostgreSQL, SQL, and business-focused analytics workflows.

## Project Overview

This project simulates an enterprise banking data platform designed to support reporting, analytics, fraud monitoring, reconciliation, and operational decision-making.

The platform integrates synthetic banking data across customers, accounts, transactions, loans, credit cards, branches, employees, and fraud alerts.

## Architecture

Python Data Generators
        ↓
CSV Raw Data
        ↓
Python Data Loaders
        ↓
PostgreSQL Data Warehouse
        ↓
SQL Validation & Analytics
        ↓
BI / Reporting Layer

## Technology Stack

- Python
- Pandas
- PostgreSQL
- SQL / T-SQL concepts
- DBeaver
- VS Code
- Git / GitHub
- Power BI / Tableau-ready data structures

## Data Domains

### Customer
Customer demographic and master data.

### Accounts
Banking accounts, account types, branches, status, and customer relationships.

### Transactions
Banking transaction activity including:

- Deposits
- Withdrawals
- Transfers
- Payments
- Fees
- Interest
- Refunds

The transaction pipeline includes validation for transaction IDs, transaction references, account relationships, statuses, channels, dates, amounts, and running account balances.

### Loans

The loan pipeline generates and loads:

- Loan type
- Loan amount
- Outstanding balance
- Interest rate
- Loan term
- Monthly payment
- Start date
- Maturity date
- Loan status

### Credit Cards

The credit card pipeline includes:

- Card number
- Card type
- Card network
- Credit limit
- Available credit
- Outstanding balance
- Issue date
- Expiry date
- Card status

### Fraud Alerts

Fraud alert data is linked back to banking transactions and customers for fraud investigation and monitoring scenarios.

## Data Quality & Validation

Each pipeline includes validation before loading data into PostgreSQL.

Examples include:

- Duplicate ID detection
- NULL validation
- Foreign key validation
- Customer/account relationship validation
- Branch relationship validation
- Amount validation
- Balance validation
- Date validation
- Status validation
- Record-count reconciliation
- Post-load database validation

## Project Structure

```text
EnterpriseBankingDW/
│
├── data/
│   └── raw/
│
├── python/
│   ├── generators/
│   │   ├── generate_branches.py
│   │   ├── generate_customers.py
│   │   ├── generate_employees.py
│   │   ├── generate_transactions.py
│   │   ├── generate_loans.py
│   │   ├── generate_credit_cards.py
│   │   └── generate_fraud_alerts.py
│   │
│   └── loaders/
│       ├── load_branches.py
│       ├── load_customers.py
│       ├── load_accounts.py
│       ├── load_employees.py
│       ├── load_transactions.py
│       ├── load_loans.py
│       ├── load_credit_cards.py
│       └── load_fraud_alerts.py
│
├── sql/
│   ├── ddl/
│   ├── validation/
│   ├── analytics/
│   └── reporting/
│
├── README.md
├── requirements.txt
└── .gitignore
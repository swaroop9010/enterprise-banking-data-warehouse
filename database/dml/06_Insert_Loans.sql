-- ============================================================
-- Project: Enterprise Banking Data Warehouse
-- Module: Loan Management
-- Description: Inserts sample loan records
-- ============================================================

INSERT INTO loans (
    loan_number,
    customer_id,
    branch_id,
    loan_type,
    loan_amount,
    outstanding_balance,
    interest_rate,
    loan_term_months,
    monthly_payment,
    start_date,
    maturity_date,
    loan_status
)
VALUES (
    'LN100001',
    1,
    1,
    'Auto',
    30000.00,
    24500.00,
    5.7500,
    60,
    576.50,
    '2025-01-15',
    '2030-01-15',
    'Active'
);
-- ============================================================
-- Project: Enterprise Banking Data Warehouse
-- Module: Account Management
-- Description: Inserts sample bank account records
-- ============================================================

INSERT INTO accounts (
    account_number,
    customer_id,
    branch_id,
    account_type,
    account_status,
    current_balance,
    available_balance,
    interest_rate,
    opened_date,
    currency
)
VALUES (
    'ACC100001',
    1,
    1,
    'Checking',
    'Active',
    8500.00,
    8500.00,
    0.0100,
    '2024-01-15',
    'USD'
);

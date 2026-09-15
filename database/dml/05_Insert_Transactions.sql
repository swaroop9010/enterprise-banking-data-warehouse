-- ============================================================
-- Project: Enterprise Banking Data Warehouse
-- Module: Transaction Management
-- Description: Inserts sample banking transactions
-- ============================================================


-- Transaction 1: Deposit

INSERT INTO transactions (
    transaction_reference,
    account_id,
    transaction_type,
    transaction_amount,
    transaction_status,
    transaction_channel,
    transaction_date,
    description,
    balance_after_transaction
)
VALUES (
    'TXN100001',
    1,
    'Deposit',
    2000.00,
    'Completed',
    'Branch',
    '2026-07-01 09:30:00',
    'Cash deposit',
    10500.00
);


-- Transaction 2: ATM Withdrawal

INSERT INTO transactions (
    transaction_reference,
    account_id,
    transaction_type,
    transaction_amount,
    transaction_status,
    transaction_channel,
    transaction_date,
    description,
    location,
    balance_after_transaction
)
VALUES (
    'TXN100002',
    1,
    'ATM Withdrawal',
    500.00,
    'Completed',
    'ATM',
    '2026-07-02 14:20:00',
    'ATM cash withdrawal',
    'Philadelphia, PA',
    10000.00
);


-- Transaction 3: Card Purchase

INSERT INTO transactions (
    transaction_reference,
    account_id,
    transaction_type,
    transaction_amount,
    transaction_status,
    transaction_channel,
    transaction_date,
    description,
    merchant_name,
    merchant_category,
    location,
    balance_after_transaction
)
VALUES (
    'TXN100003',
    1,
    'Card Purchase',
    125.50,
    'Completed',
    'POS',
    '2026-07-03 18:45:00',
    'Grocery purchase',
    'Fresh Market',
    'Grocery',
    'Philadelphia, PA',
    9874.50
);


-- Transaction 4: Online Transfer

INSERT INTO transactions (
    transaction_reference,
    account_id,
    transaction_type,
    transaction_amount,
    transaction_status,
    transaction_channel,
    transaction_date,
    description,
    balance_after_transaction
)
VALUES (
    'TXN100004',
    1,
    'Transfer',
    1000.00,
    'Completed',
    'Online',
    '2026-07-04 11:15:00',
    'Online fund transfer',
    8874.50
);


-- Transaction 5: Failed Card Purchase

INSERT INTO transactions (
    transaction_reference,
    account_id,
    transaction_type,
    transaction_amount,
    transaction_status,
    transaction_channel,
    transaction_date,
    description,
    merchant_name,
    merchant_category,
    location,
    balance_after_transaction
)
VALUES (
    'TXN100005',
    1,
    'Card Purchase',
    9500.00,
    'Failed',
    'POS',
    '2026-07-05 22:30:00',
    'High value card purchase attempt',
    'Luxury Electronics Store',
    'Electronics',
    'New York, NY',
    8874.50
);
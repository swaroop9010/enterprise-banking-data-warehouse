-- ============================================================
-- Project: Enterprise Banking Data Warehouse
-- Module: Account Management
-- Description: Creates the accounts table
-- ============================================================

CREATE TABLE accounts (

    account_id BIGINT PRIMARY KEY,

    account_number VARCHAR(30) NOT NULL UNIQUE,

    customer_id BIGINT NOT NULL,

    branch_id BIGINT NOT NULL,

    account_type VARCHAR(30) NOT NULL,

    account_status VARCHAR(20) DEFAULT 'Active',

    current_balance NUMERIC(15,2) NOT NULL DEFAULT 0.00,

    available_balance NUMERIC(15,2) NOT NULL DEFAULT 0.00,

    interest_rate NUMERIC(6,4) DEFAULT 0.0000,

    opened_date DATE NOT NULL,

    closed_date DATE,

    currency VARCHAR(10) DEFAULT 'USD',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_account_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_account_branch
        FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id),

    CONSTRAINT chk_account_type
        CHECK (
            account_type IN (
                'Savings',
                'Checking',
                'Business',
                'Money Market',
                'Fixed Deposit'
            )       
        ),

    CONSTRAINT chk_account_status
        CHECK (
            account_status IN (
                'Active',
                'Inactive',
                'Frozen',
                'Closed'
            )
        ),

    CONSTRAINT chk_account_balance
        CHECK (current_balance >= 0),

    CONSTRAINT chk_available_balance
        CHECK (available_balance >= 0),

    CONSTRAINT chk_interest_rate
        CHECK (interest_rate >= 0),

    CONSTRAINT chk_account_dates
        CHECK (
            closed_date IS NULL
            OR closed_date >= opening_date
        )
);
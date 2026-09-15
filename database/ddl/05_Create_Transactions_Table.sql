-- ============================================================
-- Project: Enterprise Banking Data Warehouse
-- Module: Transaction Management
-- Description: Creates the transactions table
-- ============================================================

CREATE TABLE transactions (

    transaction_id BIGINT PRIMARY KEY,

    transaction_number VARCHAR(30) UNIQUE NOT NULL,

    account_id BIGINT NOT NULL,

    customer_id BIGINT NOT NULL,

    branch_id BIGINT NOT NULL,

    transaction_date TIMESTAMP NOT NULL,

    transaction_type VARCHAR(30) NOT NULL,

    transaction_category VARCHAR(50),

    amount NUMERIC(15,2) NOT NULL,

    currency VARCHAR(10) DEFAULT 'USD',

    transaction_status VARCHAR(20) DEFAULT 'Completed',

    channel VARCHAR(30),

    description VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,


    -- ========================================================
    -- Foreign Keys
    -- ========================================================

    CONSTRAINT fk_transaction_account
        FOREIGN KEY (account_id)
        REFERENCES accounts(account_id),

    CONSTRAINT fk_transaction_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_transaction_branch
        FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id),


    -- ========================================================
    -- Transaction Type
    -- ========================================================

    CONSTRAINT chk_transaction_type
        CHECK (
            transaction_type IN (
                'Deposit',
                'Withdrawal',
                'Transfer',
                'Payment',
                'Fee',
                'Interest',
                'Refund'
            )
        ),


    -- ========================================================
    -- Transaction Status
    -- ========================================================

    CONSTRAINT chk_transaction_status
        CHECK (
            transaction_status IN (
                'Completed',
                'Pending',
                'Failed',
                'Reversed'
            )
        ),


    -- ========================================================
    -- Transaction Amount
    -- ========================================================

    CONSTRAINT chk_transaction_amount
        CHECK (amount > 0)

);
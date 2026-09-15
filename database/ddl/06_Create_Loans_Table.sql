-- ============================================================
-- Project: Enterprise Banking Data Warehouse
-- Module: Loan Management
-- Description: Creates the loans table
-- ============================================================

CREATE TABLE loans (

    loan_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    loan_number VARCHAR(30) NOT NULL UNIQUE,

    customer_id BIGINT NOT NULL,

    branch_id BIGINT NOT NULL,

    loan_type VARCHAR(30) NOT NULL,

    loan_amount NUMERIC(15,2) NOT NULL,

    outstanding_balance NUMERIC(15,2) NOT NULL,

    interest_rate NUMERIC(6,4) NOT NULL,

    loan_term_months INTEGER NOT NULL,

    monthly_payment NUMERIC(15,2),

    start_date DATE NOT NULL,

    maturity_date DATE NOT NULL,

    loan_status VARCHAR(20) DEFAULT 'Active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_loan_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_loan_branch
        FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id),

    CONSTRAINT chk_loan_type
        CHECK (
            loan_type IN (
                'Personal',
                'Auto',
                'Mortgage',
                'Business',
                'Student'
            )
        ),

    CONSTRAINT chk_loan_status
        CHECK (
            loan_status IN (
                'Pending',
                'Approved',
                'Active',
                'Paid Off',
                'Defaulted',
                'Rejected'
            )
        ),

    CONSTRAINT chk_loan_amount
        CHECK (loan_amount > 0),

    CONSTRAINT chk_outstanding_balance
        CHECK (
            outstanding_balance >= 0
            AND outstanding_balance <= loan_amount
        ),

    CONSTRAINT chk_loan_interest_rate
        CHECK (interest_rate >= 0),

    CONSTRAINT chk_loan_term
        CHECK (loan_term_months > 0),

    CONSTRAINT chk_loan_dates
        CHECK (maturity_date > start_date)
);
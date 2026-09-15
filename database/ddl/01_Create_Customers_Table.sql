-- ============================================================
-- Project: Enterprise Banking Data Warehouse
-- Module: Customer Management
-- Description: Creates the customers table
-- ============================================================

CREATE TABLE customers (

    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    customer_number VARCHAR(20) UNIQUE NOT NULL,

    first_name VARCHAR(50) NOT NULL,

    last_name VARCHAR(50) NOT NULL,

    date_of_birth DATE NOT NULL,

    gender VARCHAR(20),

    email VARCHAR(100) NOT NULL UNIQUE,

    phone VARCHAR(20) NOT NULL,

    ssn VARCHAR(20) UNIQUE,

    address VARCHAR(255),

    city VARCHAR(100),

    state VARCHAR(50),

    zip_code VARCHAR(20),

    country VARCHAR(100) DEFAULT 'USA',

    customer_since DATE NOT NULL DEFAULT CURRENT_DATE,

    occupation VARCHAR(100),

    annual_income NUMERIC(15,2),

    risk_rating VARCHAR(20),

    kyc_status VARCHAR(20) DEFAULT 'Pending',

    customer_status VARCHAR(20) DEFAULT 'Active',

    branch_id BIGINT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_customer_status
        CHECK (customer_status IN ('Active', 'Inactive', 'Closed', 'Pending')),

    CONSTRAINT chk_kyc_status
        CHECK (kyc_status IN ('Pending', 'Verified', 'Rejected')),

    CONSTRAINT chk_risk_rating
        CHECK (risk_rating IS NULL OR risk_rating IN ('Low', 'Medium', 'High')),

    CONSTRAINT chk_annual_income
        CHECK (annual_income IS NULL OR annual_income >= 0),

    CONSTRAINT chk_date_of_birth
        CHECK (date_of_birth <= CURRENT_DATE),
    
    FOREIGN KEY (branch_id)
    REFERENCES branches(branch_id)
);
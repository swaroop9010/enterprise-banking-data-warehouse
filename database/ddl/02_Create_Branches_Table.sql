-- ============================================================
-- Project: Enterprise Banking Data Warehouse
-- Module: Branch Management
-- Description: Creates the branches table
-- ============================================================

CREATE TABLE branches (

    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    branch_code VARCHAR(20) NOT NULL UNIQUE,

    branch_name VARCHAR(100) NOT NULL,

    address VARCHAR(255) NOT NULL,

    city VARCHAR(100) NOT NULL,

    state VARCHAR(50) NOT NULL,

    zip_code VARCHAR(20) NOT NULL,

    country VARCHAR(100) DEFAULT 'USA',

    phone VARCHAR(20),

    manager_name VARCHAR(100),

    opening_date DATE,

    branch_status VARCHAR(20) DEFAULT 'Active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_branch_status
        CHECK (branch_status IN ('Active', 'Inactive', 'Closed')),

    CONSTRAINT chk_branch_opening_date
        CHECK (opening_date IS NULL OR opening_date <= CURRENT_DATE)
);
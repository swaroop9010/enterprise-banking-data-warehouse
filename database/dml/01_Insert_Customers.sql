-- ============================================================
-- Project: Enterprise Banking Data Warehouse
-- Module: Customer Management
-- Description: Inserts sample customer records
-- ============================================================

INSERT INTO customers (
    first_name,
    last_name,
    date_of_birth,
    gender,
    email,
    phone,
    ssn,
    address,
    city,
    state,
    zip_code,
    country,
    occupation,
    annual_income,
    risk_rating,
    kyc_status,
    customer_status
)
VALUES (
    'John',
    'Smith',
    '1990-05-15',
    'Male',
    'john.smith@example.com',
    '2155550101',
    '123-45-6789',
    '1500 Market Street',
    'Philadelphia',
    'PA',
    '19102',
    'USA',
    'Software Engineer',
    95000.00,
    'Low',
    'Verified',
    'Active'
);
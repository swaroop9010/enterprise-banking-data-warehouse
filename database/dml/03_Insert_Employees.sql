-- ============================================================
-- Project: Enterprise Banking Data Warehouse
-- Module: Employee Management
-- Description: Inserts sample employee records
-- ============================================================

INSERT INTO employees (
    employee_number,
    first_name,
    last_name,
    email,
    phone,
    job_title,
    department,
    branch_id,
    hire_date,
    salary,
    employment_status
)
VALUES (
    'EMP001',
    'Robert',
    'Williams',
    'robert.williams@enterprisebank.com',
    '2155552001',
    'Branch Manager',
    'Branch Operations',
    1,
    '2018-03-12',
    95000.00,
    'Active'
);
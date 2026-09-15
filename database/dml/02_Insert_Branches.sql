-- ============================================================
-- Project: Enterprise Banking Data Warehouse
-- Module: Branch Management
-- Description: Inserts sample branch records
-- ============================================================

INSERT INTO branches (
    branch_code,
    branch_name,
    address,
    city,
    state,
    zip_code,
    country,
    phone,
    manager_name,
    opening_date,
    branch_status
)
VALUES (
    'BR001',
    'Philadelphia Downtown Branch',
    '1600 Market Street',
    'Philadelphia',
    'PA',
    '19103',
    'USA',
    '2155551000',
    'Robert Williams',
    '2015-06-15',
    'Active'
);
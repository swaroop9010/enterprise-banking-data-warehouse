-- ============================================================
-- Project: Enterprise Banking Data Warehouse
-- Module: Employee Management
-- Description: Creates the employees table
-- ============================================================

CREATE TABLE employees (

    employee_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    employee_number VARCHAR(20) NOT NULL UNIQUE,

    first_name VARCHAR(50) NOT NULL,

    last_name VARCHAR(50) NOT NULL,

    email VARCHAR(100) NOT NULL UNIQUE,

    phone VARCHAR(20),

    job_title VARCHAR(100) NOT NULL,

    department VARCHAR(100),

    branch_id BIGINT NOT NULL,

    hire_date DATE NOT NULL,

    salary NUMERIC(15,2),

    employment_status VARCHAR(20) DEFAULT 'Active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_employee_branch
        FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id),

    CONSTRAINT chk_employee_salary
        CHECK (salary IS NULL OR salary >= 0),

    CONSTRAINT chk_employment_status
        CHECK (
            employment_status IN
            ('Active', 'Inactive', 'Terminated', 'On Leave')
        ),

    CONSTRAINT chk_employee_hire_date
        CHECK (hire_date <= CURRENT_DATE)
);
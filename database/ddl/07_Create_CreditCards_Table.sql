-- ==========================================================
-- Enterprise Banking Data Warehouse
-- Credit Cards Table
-- ==========================================================

CREATE TABLE credit_cards (

    card_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    customer_id BIGINT NOT NULL,

    account_id BIGINT NOT NULL,

    card_number VARCHAR(25) NOT NULL UNIQUE,

    card_type VARCHAR(30) NOT NULL,

    card_network VARCHAR(20) NOT NULL,

    credit_limit NUMERIC(15,2) NOT NULL,

    available_credit NUMERIC(15,2) NOT NULL,

    outstanding_balance NUMERIC(15,2) DEFAULT 0,

    issue_date DATE NOT NULL,

    expiry_date DATE NOT NULL,

    card_status VARCHAR(20) DEFAULT 'Active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_card_customer
        FOREIGN KEY(customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_card_account
        FOREIGN KEY(account_id)
        REFERENCES accounts(account_id),

    CONSTRAINT chk_card_type
        CHECK(card_type IN
        ('Standard','Gold','Platinum','Business')),

    CONSTRAINT chk_network
        CHECK(card_network IN
        ('Visa','MasterCard','Amex')),

    CONSTRAINT chk_status
        CHECK(card_status IN
        ('Active','Blocked','Expired','Lost')),

    CONSTRAINT chk_credit_limit
        CHECK(credit_limit > 0),

    CONSTRAINT chk_available_credit
        CHECK(available_credit >=0)
);
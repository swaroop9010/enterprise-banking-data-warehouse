CREATE TABLE fraud_alerts (

    alert_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    transaction_id BIGINT NOT NULL,

    customer_id BIGINT NOT NULL,

    alert_type VARCHAR(100) NOT NULL,

    risk_score NUMERIC(5,2),

    alert_status VARCHAR(30) DEFAULT 'Open',

    alert_description VARCHAR(300),

    detected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    investigated_by VARCHAR(100),

    investigation_notes VARCHAR(500),

    resolved_time TIMESTAMP,

    CONSTRAINT fk_alert_transaction
        FOREIGN KEY(transaction_id)
        REFERENCES transactions(transaction_id),

    CONSTRAINT fk_alert_customer
        FOREIGN KEY(customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT chk_risk_score
        CHECK(risk_score BETWEEN 0 AND 100),

    CONSTRAINT chk_alert_status
        CHECK(alert_status IN
        (
            'Open',
            'Under Investigation',
            'Resolved',
            'False Positive'
        ))

);
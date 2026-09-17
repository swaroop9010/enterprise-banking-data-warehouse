# Sprint 01 - Database Test Cases

## Module: Customer Management

### TC-001 - Create Valid Customer

**Objective:** Verify that a valid customer can be created.

**Test Data:**
- First Name: John
- Last Name: Smith
- Email: john.smith@example.com
- Annual Income: 95000
- Risk Rating: Low
- KYC Status: Verified
- Customer Status: Active

**Expected Result:** Customer should be successfully inserted.

**Actual Result:** Customer successfully inserted.

**Status:** PASS

---

### TC-002 - Duplicate Email Validation

**Objective:** Verify that duplicate customer email addresses are rejected.

**Expected Result:** Database should reject duplicate email.

**Actual Result:** Database rejected duplicate email because of UNIQUE constraint.

**Status:** PASS

---

### TC-003 - Invalid Customer Status

**Objective:** Verify that invalid customer status values are rejected.

**Test Value:** ABC

**Expected Result:** Database should reject the record.

**Actual Result:** CHECK constraint prevented insertion.

**Status:** PASS

---

### TC-004 - Negative Annual Income

**Objective:** Verify that annual income cannot be negative.

**Test Value:** -50000

**Expected Result:** Database should reject the record.

**Actual Result:** CHECK constraint prevented insertion.

**Status:** PASS


---

## Module: Employee Management

### TC-005 - Create Valid Employee

**Objective:** Verify that an employee can be assigned to an existing branch.

**Expected Result:** Employee should be successfully inserted.

**Actual Result:** Employee successfully inserted and associated with branch BR001.

**Status:** PASS

---

### TC-006 - Invalid Branch Assignment

**Objective:** Verify that an employee cannot be assigned to a non-existing branch.

**Test Data:**
- Employee Number: EMP999
- Branch ID: 9999

**Expected Result:** Database should reject the employee record.

**Actual Result:** Foreign key constraint prevented insertion.

**Status:** PASS


---

## Module: Account Management

### TC-007 - Create Valid Account

**Objective:** Verify that an account can be created for a valid customer and branch.

**Expected Result:** Account should be successfully created.

**Actual Result:** Checking account ACC100001 successfully created.

**Status:** PASS

---

### TC-008 - Invalid Customer

**Objective:** Verify that an account cannot be created for a non-existing customer.

**Test Customer ID:** 9999

**Expected Result:** Database should reject the account.

**Actual Result:** Foreign key constraint prevented insertion.

**Status:** PASS

---

### TC-009 - Invalid Branch

**Objective:** Verify that an account cannot be assigned to a non-existing branch.

**Test Branch ID:** 9999

**Expected Result:** Database should reject the account.

**Actual Result:** Foreign key constraint prevented insertion.

**Status:** PASS

---

### TC-010 - Invalid Account Type

**Objective:** Verify account type validation.

**Test Value:** Crypto

**Expected Result:** Database should reject unsupported account type.

**Actual Result:** CHECK constraint prevented insertion.

**Status:** PASS

---

### TC-011 - Negative Account Balance

**Objective:** Verify that account balance cannot be negative.

**Test Value:** -500.00

**Expected Result:** Database should reject negative balance.

**Actual Result:** CHECK constraint prevented insertion.

**Status:** PASS


---

## Module: Loan Management

### TC-012 - Create Valid Loan

**Objective:** Verify that a valid loan can be created.

**Expected Result:** Loan should be successfully created.

**Actual Result:** Auto loan LN100001 successfully created.

**Status:** PASS

---

### TC-013 - Negative Loan Amount

**Objective:** Verify that a loan cannot have a negative loan amount.

**Expected Result:** Database should reject the loan.

**Actual Result:** CHECK constraint prevented insertion.

**Status:** PASS

---

### TC-014 - Outstanding Balance Validation

**Objective:** Verify that outstanding balance cannot exceed the original loan amount.

**Expected Result:** Database should reject the loan.

**Actual Result:** CHECK constraint prevented insertion.

**Status:** PASS

---

### TC-015 - Invalid Loan Customer

**Objective:** Verify that a loan cannot be created for a non-existing customer.

**Test Customer ID:** 9999

**Expected Result:** Database should reject the loan.

**Actual Result:** Foreign key constraint prevented insertion.

**Status:** PASS
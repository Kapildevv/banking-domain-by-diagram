-- The Tamarind Bank practice database (PostgreSQL). Table and column names belong to this book's
-- teaching model, not to any vendor. Load order does not matter: there are primary keys and no foreign keys.
-- Kept by hand beside generate_bank_data.py; build_sql.py adds the rows from csv/ to make tamarind_bank.sql.

CREATE TABLE branches (
    branch_id   text PRIMARY KEY,
    branch_name text NOT NULL,
    city        text NOT NULL,
    state       text NOT NULL
);

CREATE TABLE gl_accounts (
    gl_code        text PRIMARY KEY,
    gl_name        text NOT NULL,
    gl_type        text NOT NULL,          -- ASSET, LIABILITY, INCOME, EXPENSE
    parent_gl_code text
);

CREATE TABLE products (
    product_id      text PRIMARY KEY,
    product_name    text NOT NULL,
    product_type    text NOT NULL,         -- CASA, TERM_DEPOSIT, LOAN, CC
    asset_liability text NOT NULL,
    annual_rate_pct numeric(5,2) NOT NULL,
    gl_code         text NOT NULL
);

CREATE TABLE customers (
    ucic               text PRIMARY KEY,
    customer_type      text NOT NULL,      -- INDIVIDUAL, CORPORATE
    full_name          text NOT NULL,
    date_of_birth      date,
    city               text NOT NULL,
    onboarding_channel text NOT NULL,      -- BRANCH, VCIP, AADHAAR_OTP
    kyc_status         text NOT NULL,      -- VERIFIED, OTP_LIMITED
    risk_category      text NOT NULL,      -- LOW, MEDIUM, HIGH
    ckyc_kin           text NOT NULL,
    onboarded_on       date NOT NULL,
    last_kyc_on        date NOT NULL,
    email              text NOT NULL
);

CREATE TABLE accounts (
    account_number       text PRIMARY KEY,
    ucic                 text NOT NULL,
    product_id           text NOT NULL,
    branch_id            text NOT NULL,
    opened_on            date NOT NULL,
    account_status       text NOT NULL,    -- ACTIVE, INOPERATIVE
    ledger_balance       numeric(16,2) NOT NULL,
    lien_amount          numeric(16,2) NOT NULL,
    last_customer_txn_on date NOT NULL
);

CREATE TABLE transactions (
    entry_id       integer PRIMARY KEY,
    txn_ref        text NOT NULL,
    account_number text,                   -- empty on the ledger-only leg
    gl_code        text NOT NULL,
    entry_type     text NOT NULL,          -- DR, CR
    amount         numeric(16,2) NOT NULL,
    value_date     date NOT NULL,
    channel        text NOT NULL,
    initiated_by   text NOT NULL,          -- CUSTOMER, BANK
    narration      text NOT NULL
);

CREATE TABLE loans (
    loan_id               text PRIMARY KEY,
    ucic                  text NOT NULL,
    product_id            text NOT NULL,
    secured               text NOT NULL,   -- Y, N
    sanctioned_amount     numeric(16,2) NOT NULL,
    outstanding_principal numeric(16,2) NOT NULL,
    annual_rate_pct       numeric(5,2) NOT NULL,
    emi_amount            numeric(16,2) NOT NULL,
    disbursed_on          date NOT NULL,
    days_past_due         integer NOT NULL,
    asset_class           text NOT NULL    -- STANDARD, SMA-0, SMA-1, SMA-2, NPA
);

CREATE TABLE loan_repayments (
    loan_id     text NOT NULL,
    due_date    date NOT NULL,
    emi_amount  numeric(16,2) NOT NULL,
    paid_on     date,
    paid_amount numeric(16,2) NOT NULL,
    PRIMARY KEY (loan_id, due_date)
);

CREATE TABLE credit_limits (
    limit_id          text PRIMARY KEY,
    parent_limit_id   text,
    ucic              text NOT NULL,
    limit_type        text NOT NULL,       -- TOTAL, CC, WCDL
    sanctioned_amount numeric(16,2) NOT NULL,
    drawing_power     numeric(16,2),
    utilised_amount   numeric(16,2),
    expiry_date       date NOT NULL
);

CREATE TABLE stock_statements (
    ucic              text NOT NULL,
    statement_month   text NOT NULL,       -- YYYY-MM
    paid_stock        numeric(16,2) NOT NULL,
    book_debts        numeric(16,2) NOT NULL,
    stock_margin_pct  numeric(5,2) NOT NULL,
    debtor_margin_pct numeric(5,2) NOT NULL,
    PRIMARY KEY (ucic, statement_month)
);

CREATE TABLE bank_guarantees (
    bg_id           text PRIMARY KEY,
    ucic            text NOT NULL,
    bg_type         text NOT NULL,         -- PERFORMANCE, FINANCIAL
    amount          numeric(16,2) NOT NULL,
    margin_pct      numeric(5,2) NOT NULL,
    issued_on       date NOT NULL,
    expiry_on       date NOT NULL,
    claim_expiry_on date NOT NULL,
    beneficiary     text NOT NULL,
    status          text NOT NULL,         -- ACTIVE, EXPIRED, INVOKED
    invoked_on      date
);

CREATE TABLE workflow_tasks (
    task_id      text PRIMARY KEY,
    task_type    text NOT NULL,            -- LOAN_DISBURSAL, BG_ISSUE
    reference_id text NOT NULL,            -- a loan_id or a bg_id
    ucic         text NOT NULL,
    amount       numeric(16,2) NOT NULL,
    maker_id     text NOT NULL,
    made_at      timestamp NOT NULL,
    checker_id   text NOT NULL,
    checked_at   timestamp NOT NULL,
    status       text NOT NULL
);

CREATE TABLE interest_accruals (
    accrual_id      text PRIMARY KEY,
    business_date   date NOT NULL,
    source_type     text NOT NULL,         -- DEPOSIT, LOAN
    account_number  text,
    loan_id         text,
    base_amount     numeric(16,2) NOT NULL,
    annual_rate_pct numeric(5,2) NOT NULL,
    accrued_amount  numeric(16,2) NOT NULL,
    debit_gl_code   text NOT NULL,
    credit_gl_code  text NOT NULL
);

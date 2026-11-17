"""Synthetic data for Tamarind Bank Ltd, the fictional bank of *Banking Domain by Diagram*.

Deterministic (fixed seed): the same run always writes the same rows, so every number the
book prints can be recomputed. Nothing here is real: names are random
combinations, emails use example.com, CKYC numbers start 9990, there are no phone numbers,
PANs or Aadhaar numbers.

    python generate_bank_data.py            # writes csv/*.csv beside this file (schema.sql is kept by hand)

The data carries PLANTED FINDINGS (see PLANTED below) that the book's practice tasks
ask the reader to find.
"""
from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

SEED = 20261112
AS_OF = date(2026, 9, 30)            # the bank's business date in every example
HERE = Path(__file__).parent
OUT = HERE / "csv"
R = random.Random(SEED)
R2 = random.Random(SEED + 1)         # later additions draw from here, so the first 11 tables never change
QUARTER_ENDS = [date(2024, 9, 30), date(2024, 12, 31), date(2025, 3, 31), date(2025, 6, 30), date(2025, 9, 30),
                date(2025, 12, 31), date(2026, 3, 31), date(2026, 6, 30), date(2026, 9, 30)]

FIRST = ["Aarav", "Aditi", "Akash", "Ananya", "Arjun", "Bhavna", "Chetan", "Deepa", "Farhan", "Gauri",
         "Harish", "Isha", "Jatin", "Kavya", "Lokesh", "Meera", "Naveen", "Nisha", "Omkar", "Pooja",
         "Rahul", "Ritu", "Sahil", "Sneha", "Tarun", "Uma", "Varun", "Yamini", "Zoya", "Imran"]
LAST = ["Agarwal", "Bose", "Chopra", "Desai", "Fernandes", "Gupta", "Hegde", "Iyer", "Joshi", "Kulkarni",
        "Lal", "Menon", "Nair", "Pillai", "Qureshi", "Rao", "Shetty", "Thomas", "Verma", "Yadav"]
CORP_A = ["Kestrel", "Indigo", "Marigold", "Granite", "Monsoon", "Juniper", "Cobalt", "Saffron",
          "Harbour", "Lantern", "Peacock", "Sandal"]
CORP_B = ["Polymers", "Textiles", "Agro Foods", "Logistics", "Castings", "Infra Projects",
          "Pharma", "Packaging", "Ceramics", "Auto Parts"]
BRANCHES = [("BR01", "MG Road", "Bengaluru", "Karnataka"), ("BR02", "Andheri East", "Mumbai", "Maharashtra"),
            ("BR03", "Anna Nagar", "Chennai", "Tamil Nadu"), ("BR04", "Salt Lake", "Kolkata", "West Bengal"),
            ("BR05", "Banjara Hills", "Hyderabad", "Telangana"), ("BR06", "Connaught Place", "New Delhi", "Delhi"),
            ("BR07", "Kothrud", "Pune", "Maharashtra"), ("BR08", "Vyttila", "Kochi", "Kerala")]

GL = [  # gl_code, gl_name, gl_type, parent
    ("100000", "Assets", "ASSET", ""), ("101001", "Cash and balances with RBI", "ASSET", "100000"),
    ("102001", "Interbank clearing and settlement", "ASSET", "100000"),
    ("103001", "Retail loans", "ASSET", "100000"), ("103002", "Corporate loans and cash credit", "ASSET", "100000"),
    ("104001", "Interest receivable on loans", "ASSET", "100000"),
    ("200000", "Liabilities", "LIABILITY", ""), ("201001", "Savings deposits", "LIABILITY", "200000"),
    ("201002", "Current deposits", "LIABILITY", "200000"), ("202001", "Term deposits", "LIABILITY", "200000"),
    ("203001", "Interest accrued on deposits", "LIABILITY", "200000"),
    ("204001", "Margin money on guarantees", "LIABILITY", "200000"),
    ("400000", "Income", "INCOME", ""), ("401001", "Interest income on loans", "INCOME", "400000"),
    ("402001", "Fee income", "INCOME", "400000"),
    ("500000", "Expenses", "EXPENSE", ""), ("501001", "Interest expense on deposits", "EXPENSE", "500000"),
]
PRODUCTS = [  # product_id, name, type, asset_liability, annual_rate_pct, gl_code
    ("SA_REGULAR", "Regular Savings Account", "CASA", "LIABILITY", 3.50, "201001"),
    ("SA_DIGITAL", "Digital Savings Account (Aadhaar OTP)", "CASA", "LIABILITY", 3.50, "201001"),
    ("CA_BUSINESS", "Business Current Account", "CASA", "LIABILITY", 0.00, "201002"),
    ("FD_1Y", "Fixed Deposit 1 Year", "TERM_DEPOSIT", "LIABILITY", 7.00, "202001"),
    ("HL_FLOAT", "Home Loan (repo linked)", "LOAN", "ASSET", 8.75, "103001"),
    ("AL_FIXED", "Auto Loan", "LOAN", "ASSET", 9.60, "103001"),
    ("PL_UNSEC", "Personal Loan (unsecured)", "LOAN", "ASSET", 12.00, "103001"),
    ("CC_WC", "Cash Credit (working capital)", "CC", "ASSET", 10.25, "103002"),
]
PRODUCT_GL = {p[0]: p[5] for p in PRODUCTS}

# What the reader is asked to find, with the count the book's Practice prints.
PLANTED = {
    "duplicate_customers": 3,        # same name + date of birth under two UCICs
    "otp_over_cap": 5,               # Aadhaar-OTP accounts above Rs 1,00,000
    "should_be_inoperative": 12,     # ACTIVE, no customer transaction for over 2 years
    "balance_mismatch": 3,           # ledger_balance != sum of its entries
    "unbalanced_txn_refs": 1,        # debits != credits
    "npa_contagion_missed": 4,       # borrower has an NPA loan and another loan not NPA
    "cc_over_drawing_power": 2,      # cash credit utilised above drawing power
    "maker_is_checker": 1,           # a task approved by the person who entered it
    "bg_closed_in_claim_period": 3,  # guarantee marked EXPIRED while the beneficiary may still claim
}
BG_IN_CLAIM_PERIOD = 5               # past expiry_on, claim_expiry_on not yet passed (3 of them planted above)
INVOKED_ON = date(2026, 9, 25)       # a Friday; the chapter 10 case


def money(x: float) -> str:
    return f"{x:.2f}"


def rand_date(a: date, b: date) -> date:
    return a + timedelta(days=R.randrange((b - a).days + 1))


def write(name: str, header: list[str], rows: list[list]) -> None:
    OUT.mkdir(exist_ok=True)
    with open(OUT / f"{name}.csv", "w", newline="\n", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def asset_class(dpd: int) -> str:
    if dpd == 0:
        return "STANDARD"
    if dpd <= 30:
        return "SMA-0"
    if dpd <= 60:
        return "SMA-1"
    if dpd <= 90:
        return "SMA-2"
    return "NPA"


def main() -> None:
    # ---- customers -------------------------------------------------------------------
    customers = []
    for i in range(1, 361):
        name = f"{R.choice(FIRST)} {R.choice(LAST)}"
        channel = R.choices(["BRANCH", "VCIP", "AADHAAR_OTP"], [50, 30, 20])[0]
        risk = R.choices(["LOW", "MEDIUM", "HIGH"], [70, 22, 8])[0]
        onboarded = rand_date(date(2015, 1, 1), date(2026, 8, 31))
        last_kyc = max(onboarded, rand_date(date(2018, 1, 1), date(2026, 8, 31)))
        kyc = "OTP_LIMITED" if channel == "AADHAAR_OTP" and R.random() < 0.6 else "VERIFIED"
        customers.append([f"TB{100000 + i}", "INDIVIDUAL", name, rand_date(date(1960, 1, 1), date(2004, 12, 31)).isoformat(),
                          R.choice(BRANCHES)[2], channel, kyc, risk, f"9990{R.randrange(10**10):010d}",
                          onboarded.isoformat(), last_kyc.isoformat(),
                          f"{name.lower().replace(' ', '.')}{i}@example.com"])
    used = set()
    for i in range(1, 41):
        while True:
            name = f"{R.choice(CORP_A)} {R.choice(CORP_B)} Pvt Ltd"
            if name not in used:
                used.add(name)
                break
        onboarded = rand_date(date(2012, 1, 1), date(2025, 12, 31))
        customers.append([f"TB{200000 + i}", "CORPORATE", name, "", R.choice(BRANCHES)[2], "BRANCH", "VERIFIED",
                          R.choices(["LOW", "MEDIUM", "HIGH"], [40, 45, 15])[0], f"9990{R.randrange(10**10):010d}",
                          onboarded.isoformat(), max(onboarded, rand_date(date(2020, 1, 1), date(2026, 8, 31))).isoformat(),
                          f"accounts{i}@example.com"])
    for k, src in enumerate(R.sample(customers[:360], PLANTED["duplicate_customers"])):   # planted duplicates
        dup = list(src)
        dup[0] = f"TB{190000 + k + 1}"
        dup[4], dup[5], dup[6] = R.choice(BRANCHES)[2], "BRANCH", "VERIFIED"
        dup[9] = dup[10] = rand_date(date(2024, 1, 1), date(2026, 6, 30)).isoformat()
        dup[8] = f"9990{R.randrange(10**10):010d}"
        customers.append(dup)
    individuals = [c for c in customers if c[1] == "INDIVIDUAL"]
    corporates = [c for c in customers if c[1] == "CORPORATE"]

    # ---- deposit accounts and their transactions ---------------------------------------
    accounts, txns = [], []
    seq = {"acc": 5000000000, "ref": 0}

    def post(acc: str | None, gl: str, kind: str, amt: float, d: date, channel: str, who: str, note: str, ref: str) -> None:
        txns.append([len(txns) + 1, ref, acc or "", gl, kind, money(amt), d.isoformat(), channel, who, note])

    def transfer(acc: str, gl: str, credit_customer: bool, amt: float, d: date, channel: str, who: str, note: str,
                 contra: str = "102001") -> None:
        seq["ref"] += 1
        ref = f"TXN{seq['ref']:07d}"
        post(acc, gl, "CR" if credit_customer else "DR", amt, d, channel, who, note, ref)
        post(None, contra, "DR" if credit_customer else "CR", amt, d, channel, who, note, ref)

    def open_account(cust: list, pid: str, stale: str = "") -> None:
        """stale: "" normal, "planted" quiet for 2+ years but still ACTIVE, "marked" quiet and INOPERATIVE."""
        seq["acc"] += R.randrange(7, 97)
        acc = str(seq["acc"])
        opened = max(date.fromisoformat(cust[9]), date(2019, 1, 1))
        opened = rand_date(opened, max(opened, date(2022, 12, 31) if stale else date(2024, 6, 30)))
        gl = PRODUCT_GL[pid]
        cap = 90000 if pid == "SA_DIGITAL" else (4000000 if pid == "CA_BUSINESS" else 600000)
        bal = 0.0
        last_customer = opened
        end = date(2024, 6, 30) if stale else AS_OF
        opened = min(opened, end)
        first = round(R.uniform(0.2, 0.9) * cap / 2, 2)
        transfer(acc, gl, True, first, opened, "BRANCH", "CUSTOMER", "Opening deposit")
        bal += first
        if pid == "FD_1Y":
            n = 0
        else:
            n = R.randrange(4, 9) if stale else R.randrange(10, 28)
        for d in sorted(rand_date(opened, end) for _ in range(n)):
            credit = R.random() < 0.52 or bal < 2000
            amt = round(R.uniform(500, cap / 8), 2)
            if not credit:
                amt = round(min(amt, bal * 0.6), 2)
            if credit and bal + amt > cap:
                continue
            ch = R.choice(["UPI", "NEFT", "ATM", "BRANCH", "IMPS"])
            transfer(acc, gl, credit, amt, d, ch, "CUSTOMER", f"{ch} {'credit' if credit else 'debit'}")
            bal += amt if credit else -amt
            last_customer = d
        if not stale and pid != "FD_1Y" and last_customer < date(2025, 10, 1):     # every live account moved this year
            d = rand_date(max(opened, date(2025, 10, 1)), AS_OF)
            amt = round(R.uniform(500, 5000), 2)
            if bal + amt <= cap:
                transfer(acc, gl, True, amt, d, "UPI", "CUSTOMER", "UPI credit")
                bal += amt
            else:
                transfer(acc, gl, False, amt, d, "UPI", "CUSTOMER", "UPI debit")
                bal -= amt
            last_customer = d
        if pid.startswith("SA"):                      # quarterly interest: a BANK-induced credit
            for q in QUARTER_ENDS:
                if q > opened:
                    amt = round(bal * 0.035 / 4, 2)
                    transfer(acc, gl, True, amt, q, "SYSTEM", "BANK", "Quarterly interest credit", contra="501001")
                    bal += amt
        if stale:      # the RBI counts a KYC update as customer-induced, so a quiet owner made none since
            cust[10] = min(cust[10], last_customer.isoformat())
        accounts.append([acc, cust[0], pid, R.choice(BRANCHES)[0], opened.isoformat(),
                         "INOPERATIVE" if stale == "marked" else "ACTIVE", money(bal), "0.00", last_customer.isoformat()])

    old = [c[0] for c in individuals if c[9] < "2022-01-01" and not (c[5] == "AADHAAR_OTP" and c[6] == "OTP_LIMITED")]
    quiet = R.sample(old, PLANTED["should_be_inoperative"] + 9)
    planted, marked = set(quiet[:PLANTED["should_be_inoperative"]]), set(quiet[PLANTED["should_be_inoperative"]:])
    for c in individuals:
        if c[5] == "AADHAAR_OTP" and c[6] == "OTP_LIMITED":
            open_account(c, "SA_DIGITAL")
        else:
            open_account(c, "SA_REGULAR", stale="planted" if c[0] in planted else "marked" if c[0] in marked else "")
        if R.random() < 0.25:
            open_account(c, "FD_1Y")
    for c in corporates:
        open_account(c, "CA_BUSINESS")
    # planted: Aadhaar-OTP accounts above the Rs 1,00,000 cap (one extra credit each)
    for a in R.sample([a for a in accounts if a[2] == "SA_DIGITAL"], PLANTED["otp_over_cap"]):
        amt = round(100000 - float(a[6]) + R.uniform(5000, 60000), 2)     # always lands above the cap
        d = rand_date(date(2026, 7, 1), AS_OF)
        transfer(a[0], "201001", True, amt, d, "NEFT", "CUSTOMER", "NEFT credit")
        a[6] = money(float(a[6]) + amt)
        a[8] = max(a[8], d.isoformat())
    # planted: balances that do not equal the sum of their entries
    for a in R.sample([a for a in accounts if a[2] == "SA_REGULAR"], PLANTED["balance_mismatch"]):
        a[6] = money(float(a[6]) + R.choice([-2500.00, 1000.00, 4999.99]))
    # planted: one transaction whose two legs differ
    victim = next(t for t in txns if t[4] == "DR" and t[2] == "" and t[7] == "NEFT")
    victim[5] = money(float(victim[5]) - 100.00)

    # ---- retail loans -------------------------------------------------------------------
    loans, repay = [], []
    borrowers = R.sample(individuals[:360], 150)
    second = R.sample(borrowers, 40)                          # 40 borrowers hold two loans

    def add_loan(cust: list, pid: str, dpd: int, force_class: str | None = None) -> None:
        rate = {"HL_FLOAT": 8.75, "AL_FIXED": 9.60, "PL_UNSEC": 12.00}[pid]
        lo, hi = {"HL_FLOAT": (1500000, 7500000), "AL_FIXED": (300000, 1200000), "PL_UNSEC": (50000, 800000)}[pid]
        sanctioned = float(R.randrange(lo, hi, 25000))
        outstanding = round(sanctioned * R.uniform(0.35, 0.97), 2)
        months = {"HL_FLOAT": 240, "AL_FIXED": 60, "PL_UNSEC": 36}[pid]
        r = rate / 1200
        emi = round(sanctioned * r * (1 + r) ** months / ((1 + r) ** months - 1), 2)
        lid = f"LN{len(loans) + 1:05d}"
        due_day = R.choice([5, 10, 15])
        dues = [date(2026, m, due_day) for m in range(4, 10)]                 # Apr-Sep 2026
        if dpd:
            oldest = AS_OF - timedelta(days=dpd - 1)                         # the due date is day 1
            dues = sorted({d for d in dues if d < oldest} | {oldest} | {d for d in dues if d > oldest})
        for d in dues:
            unpaid = dpd and d >= AS_OF - timedelta(days=dpd - 1)
            repay.append([lid, d.isoformat(), money(emi), "" if unpaid else (d + timedelta(days=R.randrange(0, 2))).isoformat(),
                          "0.00" if unpaid else money(emi)])
        loans.append([lid, cust[0], pid, "N" if pid == "PL_UNSEC" else "Y", money(sanctioned), money(outstanding),
                      f"{rate:.2f}", money(emi), rand_date(date(2020, 1, 1), date(2025, 12, 31)).isoformat(),
                      dpd, force_class or asset_class(dpd)])

    def pick_dpd() -> int:
        bucket = R.choices(["0", "a", "b", "c", "n"], [78, 9, 5, 4, 4])[0]
        return {"0": 0, "a": R.randrange(1, 31), "b": R.randrange(31, 61), "c": R.randrange(61, 91),
                "n": R.randrange(91, 240)}[bucket]

    missed = set(c[0] for c in R.sample(second, PLANTED["npa_contagion_missed"]))
    for c in borrowers:
        two = c in second
        if c[0] in missed:
            add_loan(c, "HL_FLOAT", R.randrange(95, 200))
            add_loan(c, "AL_FIXED", 0)                                       # planted: still STANDARD
        elif two:
            d = pick_dpd()
            add_loan(c, "HL_FLOAT", d)
            add_loan(c, R.choice(["AL_FIXED", "PL_UNSEC"]), 0, force_class="NPA" if d > 90 else None)
        else:
            add_loan(c, R.choice(["HL_FLOAT", "AL_FIXED", "PL_UNSEC"]), pick_dpd())

    # ---- corporate limits, stock statements, guarantees ---------------------------------
    limits, stock, bgs = [], [], []
    cc_customers = R.sample(corporates, 24)
    over = set(c[0] for c in R.sample(cc_customers, PLANTED["cc_over_drawing_power"]))
    for n, c in enumerate(cc_customers, 1):
        total = float(R.choice([20, 35, 50, 80, 120, 160, 200, 300])) * 1e7     # in rupees (crore = 1e7)
        parent = f"LIM{n:03d}"
        limits.append([parent, "", c[0], "TOTAL", money(total), "", "", "2027-03-31"])
        cc_share = 0.40 if total >= 150e7 else 1.00
        cc_limit = round(total * cc_share, 2)
        paid_stock = round(cc_limit * R.uniform(0.55, 1.05), 2)
        debts = round(cc_limit * R.uniform(0.25, 0.60), 2)
        dp = round(paid_stock * 0.75 + debts * 0.60, 2)
        usable = min(cc_limit, dp)
        used_amt = round(usable * (R.uniform(1.04, 1.15) if c[0] in over else R.uniform(0.30, 0.95)), 2)
        stock.append([c[0], "2026-09", money(paid_stock), money(debts), "25.00", "40.00"])
        limits.append([f"{parent}-CC", parent, c[0], "CC", money(cc_limit), money(dp), money(used_amt), "2027-03-31"])
        if cc_share < 1:
            limits.append([f"{parent}-WCDL", parent, c[0], "WCDL", money(total - cc_limit), "", money(total - cc_limit), "2027-03-31"])
    for n in range(1, 31):
        c = R.choice(corporates)
        amt = float(R.randrange(5, 200)) * 100000
        issued = rand_date(date(2025, 1, 1), date(2026, 8, 31))
        expiry = issued + timedelta(days=365)
        status = "EXPIRED" if expiry < AS_OF else R.choices(["ACTIVE", "INVOKED"], [9, 1])[0]
        bgs.append([f"BG{n:04d}", c[0], R.choice(["PERFORMANCE", "FINANCIAL"]), money(amt), "20.00", issued.isoformat(),
                    expiry.isoformat(), (expiry + timedelta(days=30)).isoformat(),
                    R.choice(["State Highways Authority", "Metro Rail Project Office", "Port Trust Stores", "City Water Board"]),
                    status])

    # ---- additions: all randomness from R2 ------------------------------------------------------
    # guarantees: four more that expired in September 2026, so their 30-day claim period is still open
    for n in range(31, 35):
        c = R2.choice(corporates)
        issued = date(2025, 9, 1) + timedelta(days=R2.randrange(1, 29))
        expiry = issued + timedelta(days=365)
        bgs.append([f"BG{n:04d}", c[0], R2.choice(["PERFORMANCE", "FINANCIAL"]), money(float(R2.randrange(5, 200)) * 100000),
                    "20.00", issued.isoformat(), expiry.isoformat(), (expiry + timedelta(days=30)).isoformat(),
                    R2.choice(["State Highways Authority", "Metro Rail Project Office", "Port Trust Stores", "City Water Board"]),
                    "ACTIVE"])
    # the rule: a guarantee is EXPIRED (closed, margin released) only after claim_expiry_on
    open_claims = [b for b in bgs if b[6] < AS_OF.isoformat() <= b[7] and b[9] != "INVOKED"]
    assert len(open_claims) == BG_IN_CLAIM_PERIOD, len(open_claims)
    for b in open_claims:
        b[9] = "ACTIVE"
    for b in R2.sample(open_claims, PLANTED["bg_closed_in_claim_period"]):   # planted: closed too early
        b[9] = "EXPIRED"
    for b in bgs:
        b.append(INVOKED_ON.isoformat() if b[9] == "INVOKED" else "")

    # workflow tasks: who entered (maker) and who approved (checker) each loan disbursal and guarantee
    makers = [f"EMP{n}" for n in range(2001, 2041)]
    checkers = [f"EMP{n}" for n in range(1001, 1013)]
    tasks = []

    def add_task(kind: str, ref: str, ucic: str, amt: str, day: str) -> None:
        made = datetime.fromisoformat(day) + timedelta(hours=10, minutes=R2.randrange(0, 360))
        checked = made + timedelta(minutes=R2.randrange(12, 300))
        tasks.append([f"WT{len(tasks) + 1:05d}", kind, ref, ucic, amt, R2.choice(makers),
                      made.isoformat(sep=" "), R2.choice(checkers), checked.isoformat(sep=" "), "APPROVED"])

    for ln in loans:
        add_task("LOAN_DISBURSAL", ln[0], ln[1], ln[4], ln[8])
    for b in bgs:
        add_task("BG_ISSUE", b[0], b[1], b[3], b[5])
    victim_task = R2.choice([t for t in tasks if t[1] == "LOAN_DISBURSAL" and float(t[4]) >= 3000000])
    victim_task[7] = victim_task[5]                                         # planted: maker approved their own entry

    # one day's interest accrual, the run of AS_OF: balance x rate / 365, to the paisa, half up
    accruals = []
    rate_of = {p[0]: p[4] for p in PRODUCTS}

    def accrue(kind: str, acc: str, lid: str, base: str, rate: float, dr: str, cr: str) -> None:
        amt = (Decimal(base) * Decimal(f"{rate:.2f}") / Decimal(36500)).quantize(Decimal("0.01"), ROUND_HALF_UP)
        accruals.append([f"AC{len(accruals) + 1:05d}", AS_OF.isoformat(), kind, acc, lid, base, f"{rate:.2f}",
                         str(amt), dr, cr])

    for a in accounts:                                # savings and fixed deposits; current accounts pay nothing
        if rate_of[a[2]] > 0:
            accrue("DEPOSIT", a[0], "", a[6], rate_of[a[2]], "501001", "203001")
    for ln in loans:                                  # a non-performing loan earns no accrued income
        if ln[10] != "NPA":
            accrue("LOAN", "", ln[0], ln[5], float(ln[6]), "104001", "401001")

    # ---- write --------------------------------------------------------------------------
    write("branches", ["branch_id", "branch_name", "city", "state"], [list(b) for b in BRANCHES])
    write("gl_accounts", ["gl_code", "gl_name", "gl_type", "parent_gl_code"], [list(g) for g in GL])
    write("products", ["product_id", "product_name", "product_type", "asset_liability", "annual_rate_pct", "gl_code"],
          [list(p) for p in PRODUCTS])
    write("customers", ["ucic", "customer_type", "full_name", "date_of_birth", "city", "onboarding_channel", "kyc_status",
                        "risk_category", "ckyc_kin", "onboarded_on", "last_kyc_on", "email"], customers)
    write("accounts", ["account_number", "ucic", "product_id", "branch_id", "opened_on", "account_status",
                       "ledger_balance", "lien_amount", "last_customer_txn_on"], accounts)
    write("transactions", ["entry_id", "txn_ref", "account_number", "gl_code", "entry_type", "amount", "value_date",
                           "channel", "initiated_by", "narration"], txns)
    write("loans", ["loan_id", "ucic", "product_id", "secured", "sanctioned_amount", "outstanding_principal",
                    "annual_rate_pct", "emi_amount", "disbursed_on", "days_past_due", "asset_class"], loans)
    write("loan_repayments", ["loan_id", "due_date", "emi_amount", "paid_on", "paid_amount"], repay)
    write("credit_limits", ["limit_id", "parent_limit_id", "ucic", "limit_type", "sanctioned_amount", "drawing_power",
                            "utilised_amount", "expiry_date"], limits)
    write("stock_statements", ["ucic", "statement_month", "paid_stock", "book_debts", "stock_margin_pct",
                               "debtor_margin_pct"], stock)
    write("bank_guarantees", ["bg_id", "ucic", "bg_type", "amount", "margin_pct", "issued_on", "expiry_on",
                              "claim_expiry_on", "beneficiary", "status", "invoked_on"], bgs)
    write("workflow_tasks", ["task_id", "task_type", "reference_id", "ucic", "amount", "maker_id", "made_at",
                             "checker_id", "checked_at", "status"], tasks)
    write("interest_accruals", ["accrual_id", "business_date", "source_type", "account_number", "loan_id",
                                "base_amount", "annual_rate_pct", "accrued_amount", "debit_gl_code", "credit_gl_code"],
          accruals)
    for f in sorted(OUT.glob("*.csv")):
        print(f"{f.name:24s} {sum(1 for _ in open(f, encoding='utf-8')) - 1:6d} rows")


if __name__ == "__main__":
    main()

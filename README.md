# Banking Domain by Diagram: the practice data

The practice database for the book *Banking Domain by Diagram* by Kapil Dev V: thirteen tables
of Tamarind Bank Ltd, a fictional Indian commercial bank, on its business date, Wednesday
30 September 2026. From chapter 4 on, every query in the book runs on this data.

| File | What it is |
|---|---|
| `tamarind_bank.sql` | One file that creates the 13 tables and fills them (24,300 rows). Run it once. |
| `data/csv/` | The same 13 tables as CSV files, one per table, with a header row. |
| `data/schema.sql` | The table definitions, with a note on every column that holds a code. |
| `data/generate_bank_data.py` | The script that made the data (Python 3, standard library only, fixed seed). |
| `data/build_sql.py` | The script that writes `tamarind_bank.sql` from `schema.sql` and `csv/`. |

## Load the data into PostgreSQL

You need PostgreSQL, a free database, and an empty database in it called `tamarind`. Every query
and result in the book was run on PostgreSQL 18.3, in PGlite (PostgreSQL built to run as a library). The install steps below follow each system's
standard installer.

First copy this repository to your computer: `git clone
https://github.com/Kapildevv/banking-domain-by-diagram.git`, or on this page choose **Code**, then
**Download ZIP**, and unzip it.

### Windows and macOS: pgAdmin

1. Install PostgreSQL from [postgresql.org/download](https://www.postgresql.org/download/). The
   installer for Windows and macOS also installs pgAdmin 4, a window for working with the
   database. Note the password it asks you to set for the `postgres` user.
2. Open pgAdmin 4 and open the server under **Servers**, giving that password.
3. Right-click **Databases**, choose **Create**, then **Database...**, name it `tamarind` and save.
4. Select `tamarind`, then choose **Tools**, then **Query Tool**.
5. In the Query Tool, open the file `tamarind_bank.sql` from this repository and run it
   (the **Execute** button, or F5).

### Windows: the SQL Shell instead

The installer also adds **SQL Shell (psql)** to the Start menu. Open it, press Enter at each
prompt to accept the default and give your password, then type these three lines, with the path
to where you put the repository (use forward slashes):

```text
CREATE DATABASE tamarind;
\c tamarind
\i 'C:/Users/you/Downloads/banking-domain-by-diagram/tamarind_bank.sql'
```

### Linux (Debian or Ubuntu)

```bash
sudo apt install postgresql
sudo -u postgres createdb tamarind
sudo -u postgres psql -d tamarind < tamarind_bank.sql      # run this inside the repository folder
sudo -u postgres psql -d tamarind                          # then type your queries here
```

### Check the load

```sql
SELECT count(*) FROM transactions;
```

The answer is `21054`. Row counts for every table: accounts 485, bank_guarantees 34, branches 8,
credit_limits 56, customers 403, gl_accounts 17, interest_accruals 625, loan_repayments 1,172,
loans 190, products 8, stock_statements 24, transactions 21,054, workflow_tasks 224.

To start again, drop the database and load the file into a new empty one. The file creates the
tables, so it fails on a database that already has them.

## Make the data again

```bash
python data/generate_bank_data.py      # rewrites data/csv/ (same seed, same rows)
python data/build_sql.py               # rewrites tamarind_bank.sql
```

## About the data

Tamarind Bank Ltd, its staff, its customers and every row here are fictional and were made by
`generate_bank_data.py`. Any resemblance to a real person, bank or business is coincidental.
Emails use `example.com`; there are no phone numbers, PANs or Aadhaar numbers, and every CKYC
number starts `9990`. A few problems are planted in the data on purpose, and the book finds them.

Table and column names are this book's teaching model and follow no vendor's system.

The data is for learning how a bank's data is shaped. It is not financial, legal or compliance
advice, and it describes no real bank's systems.

## Trademarks

PostgreSQL is a trademark of the PostgreSQL Community Association of Canada. pgAdmin, Windows, macOS,
Debian, Ubuntu and GitHub are trademarks of their owners, and UPI and IMPS of National Payments
Corporation of India. They are named for identification only. This project is not affiliated with,
endorsed by or sponsored by any of them, or by any bank.

## Licence

The data and the scripts are published under the MIT License (`LICENSE`). The book itself is
copyright Kapil Dev V, all rights reserved.

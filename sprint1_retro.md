# Sprint 1 Retrospective – Data Foundation

**Project:** NIFTY100 Financial Analytics  
**Sprint:** Sprint 1 – Data Foundation  
**Status:** Completed  
**Database:** `data/nifty100.db`  
**Audit Report:** `output/load_audit.csv`

---

## 1. Sprint Goal

The goal of Sprint 1 was to establish a reliable data foundation for the NIFTY100 Financial Analytics project.

The sprint objectives were:

- Set up the project environment.
- Create the required project directory structure.
- Load and normalize all 12 source Excel files.
- Implement data quality validation rules.
- Build the SQLite database schema.
- Create 10 normalized database tables with primary and foreign-key constraints.
- Load the cleaned and normalized data into SQLite.
- Generate a database load audit report.
- Perform a manual data quality review.
- Create exploratory SQL queries for database analysis.

---

## 2. Sprint Deliverables

The following Sprint 1 deliverables were completed:

- [x] Project environment setup
- [x] Required Python dependencies installed
- [x] Project directory structure created
- [x] Excel data loader implemented
- [x] Column normalization implemented
- [x] Data cleaning implemented
- [x] Company ID validation implemented
- [x] SQLite database schema created
- [x] Primary key constraints implemented
- [x] Foreign key constraints implemented
- [x] All 12 source files processed
- [x] Database successfully loaded
- [x] `nifty100.db` generated
- [x] `load_audit.csv` generated
- [x] Manual data quality review completed
- [x] 5 companies manually reviewed across time-series tables
- [x] Exploratory SQL queries created
- [x] Sprint retrospective documented

---

## 3. Database Load Summary

The final database load successfully processed all 12 source files.

| Table | Rows Before | Rows Loaded | Status |
|---|---:|---:|---|
| companies | 92 | 92 | SUCCESS |
| profitandloss | 1276 | 1177 | SUCCESS |
| balancesheet | 1312 | 1227 | SUCCESS |
| cashflow | 1187 | 1091 | SUCCESS |
| documents | 1585 | 1457 | SUCCESS |
| prosandcons | 16 | 14 | SUCCESS |
| analysis | 20 | 16 | SUCCESS |
| sectors | 92 | 92 | SUCCESS |
| stock_prices | 5520 | 5520 | SUCCESS |
| peer_groups | 56 | 56 | SUCCESS |
| financial_ratios | 1184 | 1160 | SUCCESS |
| market_cap | 552 | 552 | SUCCESS |

All 12 tables were loaded successfully.

Some rows were excluded because their `company_id` values did not match the valid company IDs in the `companies` table. This was handled by the loader to maintain foreign-key integrity.

---

## 4. Data Quality Review

A manual data quality review was performed on five companies:

- ABB
- ADANIENSOL
- ADANIENT
- ADANIGREEN
- ADANIPORTS

The following tables were reviewed for each selected company:

- Profit and Loss
- Balance Sheet
- Cash Flow
- Documents
- Stock Prices
- Financial Ratios
- Market Cap

### Review Results

The sampled records showed:

- Correct company ID mapping.
- Correct foreign-key relationships.
- Correct loading of financial time-series data.
- Correct stock-price records.
- Correct document URLs.
- Correct market-cap records.
- Correct financial-ratio records.

No loader-related data corruption or incorrect company mapping was identified during the review.

Some source-level missing values and duplicate-period records were observed. These were retained because they appear to originate from the source data rather than the database loader.

### DQ Review Status

**PASSED**

---

## 5. What Went Well

### Database Design

The database schema was successfully implemented with:

- 10 normalized tables.
- Primary keys.
- Foreign-key constraints.
- `companies` as the parent table.
- Correct table loading order.

### Loader Development

The loader successfully handled:

- Excel file reading.
- Column normalization.
- Empty-row removal.
- Duplicate-row removal.
- Company ID cleaning.
- Foreign-key validation.
- Database insertion.
- Load auditing.

### Data Validation

The loader identified invalid company IDs before database insertion. This prevented foreign-key constraint failures and protected database integrity.

### Data Quality Review

Manual validation across five companies provided confidence that the database relationships and time-series data were loaded correctly.

---

## 6. Challenges Encountered

### Foreign-Key Constraint Failures

Some source files contained company IDs that were not present in the `companies` table.

Examples included:

- WIPRO
- Other IDs identified during the initial loading process

The loader was updated to validate `company_id` values against the master company list before insertion.

---

### Duplicate Primary Keys

During development, the database was reloaded without clearing previously inserted records. This resulted in:

`UNIQUE constraint failed: companies.id`

The issue was resolved by ensuring that the database is reset or recreated before performing a fresh full load.

---

### Incorrect Excel Header Interpretation

Some supplementary Excel files were initially read incorrectly, resulting in the first data row being interpreted as column headers.

This was resolved by explicitly using:

```python
pd.read_excel(
    file_path,
    header=0
)
-- ============================================================
-- NIFTY100 DATABASE - SPRINT 1 EXPLORATORY SQL QUERIES
-- Database: nifty100.db
-- Purpose: Basic data exploration and data quality checks
-- ============================================================


-- ============================================================
-- QUERY 1: ROW COUNT FOR ALL 12 TABLES
-- Purpose: Check the number of records loaded into each table
-- ============================================================

SELECT 'companies' AS table_name, COUNT(*) AS row_count
FROM companies

UNION ALL

SELECT 'profitandloss', COUNT(*)
FROM profitandloss

UNION ALL

SELECT 'balancesheet', COUNT(*)
FROM balancesheet

UNION ALL

SELECT 'cashflow', COUNT(*)
FROM cashflow

UNION ALL

SELECT 'documents', COUNT(*)
FROM documents

UNION ALL

SELECT 'prosandcons', COUNT(*)
FROM prosandcons

UNION ALL

SELECT 'analysis', COUNT(*)
FROM analysis

UNION ALL

SELECT 'sectors', COUNT(*)
FROM sectors

UNION ALL

SELECT 'stock_prices', COUNT(*)
FROM stock_prices

UNION ALL

SELECT 'peer_groups', COUNT(*)
FROM peer_groups

UNION ALL

SELECT 'financial_ratios', COUNT(*)
FROM financial_ratios

UNION ALL

SELECT 'market_cap', COUNT(*)
FROM market_cap;


-- ============================================================
-- QUERY 2: TOTAL NUMBER OF COMPANIES
-- Purpose: Verify the number of companies in the database
-- ============================================================

SELECT COUNT(*) AS total_companies
FROM companies;


-- ============================================================
-- QUERY 3: NULL VALUES IN COMPANIES TABLE
-- Purpose: Identify important company records with missing values
-- ============================================================

SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN id IS NULL THEN 1 ELSE 0 END) AS null_company_id,
    SUM(CASE WHEN company_name IS NULL THEN 1 ELSE 0 END) AS null_company_name,
    SUM(CASE WHEN website IS NULL THEN 1 ELSE 0 END) AS null_website,
    SUM(CASE WHEN company_logo IS NULL THEN 1 ELSE 0 END) AS null_company_logo
FROM companies;


-- ============================================================
-- QUERY 4: NULL VALUES IN FINANCIAL TABLES
-- Purpose: Check missing values in key financial columns
-- ============================================================

SELECT
    'profitandloss' AS table_name,
    SUM(CASE WHEN company_id IS NULL THEN 1 ELSE 0 END) AS null_company_id,
    SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END) AS null_year,
    SUM(CASE WHEN sales IS NULL THEN 1 ELSE 0 END) AS null_sales,
    SUM(CASE WHEN net_profit IS NULL THEN 1 ELSE 0 END) AS null_net_profit
FROM profitandloss

UNION ALL

SELECT
    'balancesheet',
    SUM(CASE WHEN company_id IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN total_assets IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN total_liabilities IS NULL THEN 1 ELSE 0 END)
FROM balancesheet

UNION ALL

SELECT
    'cashflow',
    SUM(CASE WHEN company_id IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN operating_activity IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN net_cash_flow IS NULL THEN 1 ELSE 0 END)
FROM cashflow;


-- ============================================================
-- QUERY 5: YEAR COVERAGE PER COMPANY - PROFIT AND LOSS
-- Purpose: Find earliest and latest financial years for each company
-- ============================================================

SELECT
    company_id,
    MIN(year) AS earliest_year,
    MAX(year) AS latest_year,
    COUNT(*) AS number_of_records
FROM profitandloss
GROUP BY company_id
ORDER BY company_id;


-- ============================================================
-- QUERY 6: YEAR COVERAGE PER COMPANY - BALANCE SHEET
-- Purpose: Check historical coverage of balance-sheet records
-- ============================================================

SELECT
    company_id,
    MIN(year) AS earliest_year,
    MAX(year) AS latest_year,
    COUNT(*) AS number_of_records
FROM balancesheet
GROUP BY company_id
ORDER BY company_id;


-- ============================================================
-- QUERY 7: STOCK PRICE DATE COVERAGE PER COMPANY
-- Purpose: Check the available stock-price time series
-- ============================================================

SELECT
    company_id,
    MIN(date) AS first_price_date,
    MAX(date) AS last_price_date,
    COUNT(*) AS number_of_price_records
FROM stock_prices
GROUP BY company_id
ORDER BY company_id;


-- ============================================================
-- QUERY 8: YEAR COVERAGE PER COMPANY ACROSS MARKET CAP
-- Purpose: Check market-cap historical coverage
-- ============================================================

SELECT
    company_id,
    MIN(year) AS earliest_year,
    MAX(year) AS latest_year,
    COUNT(*) AS number_of_records
FROM market_cap
GROUP BY company_id
ORDER BY company_id;


-- ============================================================
-- QUERY 9: COMPANIES WITH MISSING DATA IN TIME-SERIES TABLES
-- Purpose: Identify companies that have no records in a table
-- ============================================================

SELECT
    c.id AS company_id,
    c.company_name
FROM companies c
LEFT JOIN profitandloss p
    ON c.id = p.company_id
WHERE p.company_id IS NULL
ORDER BY c.id;


-- ============================================================
-- QUERY 10: DATA COVERAGE SUMMARY PER COMPANY
-- Purpose: Compare record coverage across major time-series tables
-- ============================================================

SELECT
    c.id AS company_id,
    c.company_name,

    COUNT(DISTINCT p.id) AS profitandloss_records,

    COUNT(DISTINCT b.id) AS balancesheet_records,

    COUNT(DISTINCT cf.id) AS cashflow_records,

    COUNT(DISTINCT sp.id) AS stock_price_records,

    COUNT(DISTINCT fr.id) AS financial_ratio_records,

    COUNT(DISTINCT mc.id) AS market_cap_records

FROM companies c

LEFT JOIN profitandloss p
    ON c.id = p.company_id

LEFT JOIN balancesheet b
    ON c.id = b.company_id

LEFT JOIN cashflow cf
    ON c.id = cf.company_id

LEFT JOIN stock_prices sp
    ON c.id = sp.company_id

LEFT JOIN financial_ratios fr
    ON c.id = fr.company_id

LEFT JOIN market_cap mc
    ON c.id = mc.company_id

GROUP BY
    c.id,
    c.company_name

ORDER BY
    c.id;
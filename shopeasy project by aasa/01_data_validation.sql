-- 01_data_validation.sql
-- systematic checks to find data quality issues BEFORE cleaning
-- run against the staging tables (raw imported data)

USE ShopEasy;
GO

-------------------------------------------------------
-- 1. FIND LOGICAL DUPLICATES
-------------------------------------------------------
-- JourneyID is unique per row, but that hides duplicates where the same
-- customer+product+date+stage+action was logged twice with different IDs.
-- ROW_NUMBER groups rows by their real-world identity and flags repeats.

WITH duplicate_check AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY CustomerID, ProductID, VisitDate, Stage, Action
            ORDER BY JourneyID
        ) AS row_num
    FROM customer_journey_staging
)
SELECT * FROM duplicate_check WHERE row_num > 1;
-- result: 30 duplicate rows found
GO

-------------------------------------------------------
-- 2. FIND HIDDEN CASING INCONSISTENCIES (Stage)
-------------------------------------------------------
-- SQL Server's default collation is case-insensitive, so a plain
-- SELECT DISTINCT would hide "View" vs "view" vs "VIEW" as one value.
-- COLLATE ... CS_AS (Case Sensitive) exposes the real distinct values.

SELECT DISTINCT Stage COLLATE Latin1_General_CS_AS AS Stage_CaseSensitive
FROM customer_journey_staging
ORDER BY Stage_CaseSensitive;
-- result: 9 distinct values found (expected clean count: 4)
GO

-------------------------------------------------------
-- 3. FIND HIDDEN CASING INCONSISTENCIES (ContentType)
-------------------------------------------------------

SELECT DISTINCT ContentType COLLATE Latin1_General_CS_AS AS ContentType_CaseSensitive
FROM engagement_data_staging
ORDER BY ContentType_CaseSensitive;
-- result: 9 distinct values found (expected clean count: 4)
GO

-------------------------------------------------------
-- 4. CHECK IF NULL DURATION IS A REAL PATTERN OR A BUG
-------------------------------------------------------
-- Drop-off rows are expected to have no Duration (nothing to measure).
-- This confirms NULLs are 100% correlated with Drop-off, not random -
-- meaning they should be preserved, not imputed with a fake value.

SELECT Stage COLLATE Latin1_General_CS_AS AS Stage,
       COUNT(*) AS total_rows,
       SUM(CASE WHEN Duration = '' OR Duration IS NULL THEN 1 ELSE 0 END) AS null_duration_count
FROM customer_journey_staging
GROUP BY Stage COLLATE Latin1_General_CS_AS
ORDER BY Stage;
-- result: null_duration_count = total_rows only for Drop-off/drop-off variants, 0 elsewhere
GO

-------------------------------------------------------
-- 5. FIND COMBINED/DIRTY COLUMN (Views-Clicks string)
-------------------------------------------------------
-- Some rows store Views and Clicks combined into one text value
-- like "1043-244" instead of two clean numeric columns.

SELECT EngagementID, ContentType, Views, Clicks
FROM engagement_data_staging
WHERE Views LIKE '%-%';
-- result: 345 rows found (~20% of engagement_data)
GO

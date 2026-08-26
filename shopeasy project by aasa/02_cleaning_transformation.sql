-- 02_cleaning_transformation.sql
-- takes the messy staging tables and inserts clean, properly-typed data
-- into the final tables we created in 00_create_tables.sql

USE ShopEasy;
GO

-- clear out the final tables first (in case this script is re-run)
DELETE FROM customer_journey;
DELETE FROM customer_reviews;
DELETE FROM engagement_data;
GO

-------------------------------------------------------
-- 1. CLEAN customer_journey
-------------------------------------------------------
-- fixes applied:
--   a) dedupe using ROW_NUMBER (keep only row_num = 1)
--   b) standardize Stage casing using a CASE statement
--   c) convert Duration from VARCHAR to INT (blank string -> NULL)

WITH deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY CustomerID, ProductID, VisitDate, Stage, Action
            ORDER BY JourneyID
        ) AS row_num
    FROM customer_journey_staging
)
INSERT INTO customer_journey (JourneyID, CustomerID, ProductID, VisitDate, Stage, Duration, Action)
SELECT
    JourneyID,
    CustomerID,
    ProductID,
    VisitDate,
    -- standardize casing: whatever variant it was, map it to one clean value
    CASE
        WHEN Stage COLLATE Latin1_General_CS_AS IN ('View', 'view', 'VIEW') THEN 'View'
        WHEN Stage COLLATE Latin1_General_CS_AS IN ('Click', 'click') THEN 'Click'
        WHEN Stage COLLATE Latin1_General_CS_AS IN ('Purchase', 'purchase') THEN 'Purchase'
        WHEN Stage COLLATE Latin1_General_CS_AS IN ('Drop-off', 'drop-off') THEN 'Drop-off'
        ELSE Stage
    END AS Stage,
    -- convert Duration to INT; blank string becomes NULL (not 0 - we don't want to invent data)
    CASE WHEN Duration = '' OR Duration IS NULL THEN NULL ELSE CAST(Duration AS INT) END AS Duration,
    Action
FROM deduped
WHERE row_num = 1;   -- only keep the first occurrence of each logical duplicate group
GO

-------------------------------------------------------
-- 2. CLEAN customer_reviews
-------------------------------------------------------
-- fixes applied:
--   a) trim leading/trailing whitespace from ReviewText

INSERT INTO customer_reviews (ReviewID, CustomerID, ProductID, ReviewText, Rating, ReviewDate)
SELECT
    ReviewID,
    CustomerID,
    ProductID,
    TRIM(ReviewText) AS ReviewText,   -- removes leading/trailing spaces
    Rating,
    ReviewDate
FROM customer_reviews_staging;
GO

-------------------------------------------------------
-- 3. CLEAN engagement_data
-------------------------------------------------------
-- fixes applied:
--   a) standardize ContentType casing
--   b) split combined "views-clicks" string into two real numbers
--   c) convert Views/Clicks from VARCHAR to INT

INSERT INTO engagement_data (EngagementID, ContentType, Views, Clicks, Likes, CampaignID, EngagementDate)
SELECT
    EngagementID,
    CASE
        WHEN ContentType COLLATE Latin1_General_CS_AS IN ('Video', 'video', 'VIDEO') THEN 'Video'
        WHEN ContentType COLLATE Latin1_General_CS_AS IN ('Blog', 'blog') THEN 'Blog'
        WHEN ContentType COLLATE Latin1_General_CS_AS IN ('Social Media', 'social media') THEN 'Social Media'
        WHEN ContentType COLLATE Latin1_General_CS_AS IN ('Newsletter', 'newsletter') THEN 'Newsletter'
        ELSE ContentType
    END AS ContentType,
    -- if Views has a hyphen, it's a combined string like "1043-244"
    -- take everything BEFORE the hyphen as the real Views number
    CASE
        WHEN Views LIKE '%-%' THEN CAST(LEFT(Views, CHARINDEX('-', Views) - 1) AS INT)
        ELSE CAST(Views AS INT)
    END AS Views,
    -- if Views had a hyphen, the real Clicks value is AFTER the hyphen (Clicks column itself was blank)
    -- otherwise just use the Clicks column normally
    CASE
        WHEN Views LIKE '%-%' THEN CAST(SUBSTRING(Views, CHARINDEX('-', Views) + 1, LEN(Views)) AS INT)
        ELSE CAST(Clicks AS INT)
    END AS Clicks,
    Likes,
    CampaignID,
    EngagementDate
FROM engagement_data_staging;
GO

PRINT 'cleaning complete - checking row counts:';
SELECT COUNT(*) AS clean_journey_rows FROM customer_journey;
SELECT COUNT(*) AS clean_reviews_rows FROM customer_reviews;
SELECT COUNT(*) AS clean_engagement_rows FROM engagement_data;

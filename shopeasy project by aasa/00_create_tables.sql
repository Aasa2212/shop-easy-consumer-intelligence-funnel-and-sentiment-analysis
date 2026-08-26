-- 00_create_tables.sql
-- creating the 3 raw tables before we import the csvs
-- using VARCHAR for Stage/ContentType/Duration/Views/Clicks on purpose
-- because raw data is messy (casing issues, combined columns) - we clean these types later in step 02

USE ShopEasy;
GO

-- drop tables if they already exist, so this script can be re-run safely
IF OBJECT_ID('dbo.customer_journey', 'U') IS NOT NULL DROP TABLE dbo.customer_journey;
IF OBJECT_ID('dbo.customer_reviews', 'U') IS NOT NULL DROP TABLE dbo.customer_reviews;
IF OBJECT_ID('dbo.engagement_data', 'U') IS NOT NULL DROP TABLE dbo.engagement_data;
GO

CREATE TABLE dbo.customer_journey (
    JourneyID     INT,
    CustomerID    INT,
    ProductID     INT,
    VisitDate     DATE,
    Stage         VARCHAR(50),   -- kept as varchar, has casing mess we'll clean later
    Duration      VARCHAR(20),   -- kept as varchar because drop-off rows have blank/NULL values
    Action        VARCHAR(50)
);
GO

CREATE TABLE dbo.customer_reviews (
    ReviewID      INT,
    CustomerID    INT,
    ProductID     INT,
    ReviewText    VARCHAR(500),  -- has leading/trailing whitespace on purpose
    Rating        INT,
    ReviewDate    DATE
);
GO

CREATE TABLE dbo.engagement_data (
    EngagementID  INT,
    ContentType   VARCHAR(50),   -- casing mess we'll clean later
    Views         VARCHAR(20),   -- varchar because some rows have "views-clicks" combined string
    Clicks        VARCHAR(20),
    Likes         INT,
    CampaignID    INT,
    EngagementDate DATE
);
GO

PRINT 'tables created successfully';

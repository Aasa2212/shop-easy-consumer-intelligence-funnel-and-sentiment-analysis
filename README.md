# Shop Easy Consumer Intelligence Funnel & Sentiment Analysis

An end-to-end data analytics project simulating a consumer behavior and review sentiment pipeline for a fictional e-commerce brand, **Shop Easy**. Built entirely from synthetic data through SQL cleaning, Python sentiment analysis, and a Power BI dashboard.

## Project Overview

This project answers three business questions:
1. **Where are customers dropping off in the purchase funnel?**
2. **What do customers actually feel about our products, beyond star ratings?**
3. **What specific issues (quality, price, shipping, service) drive negative sentiment?**

## Pipeline

**1. Data Generation** (`generate_data.py`)
Synthetic datasets modeling 3 raw sources: customer journey events, product reviews, and marketing engagement — deliberately seeded with realistic data quality issues (duplicate records, inconsistent text casing, combined/dirty columns, and intentional NULL patterns) to practice real-world data cleaning.

**2. Data Validation** (`01_data_validation.sql`)
Systematic SQL checks to detect:
- Logical duplicates using `ROW_NUMBER() OVER (PARTITION BY ...)`
- Hidden text-casing inconsistencies using `COLLATE ... CS_AS`
- Whether NULL values represent a real pattern (correlated with Drop-off stage) vs. a data quality bug
- Combined/dirty columns using `LIKE` pattern matching

**3. Data Cleaning & Transformation** (`02_cleaning_transformation.sql`)
- Deduplication via `ROW_NUMBER()`
- Casing standardization via `CASE WHEN`
- Splitting a combined "Views-Clicks" string column using `CHARINDEX()` / `SUBSTRING()` / `LEFT()`
- Type conversion (VARCHAR → INT) with NULL preservation (not imputation) where NULLs represent real behavior

**4. Sentiment Analysis** (`03_sentiment_analysis.py`)
- VADER sentiment scoring on review text
- **Hybrid scoring model**: blends VADER's compound score (40%) with the customer's star rating (60%), correcting for VADER's blind spots on short, informal review text (e.g., "will buy again" scores 0.0 in VADER alone, despite a 5-star rating)

**5. Theme Extraction** (`04_theme_extraction.py`)
Keyword-bucket matching to tag *why* a review is negative (Quality / Price / Shipping-Delivery / Customer Service) — explainable and auditable, unlike a black-box classifier.

**6. Power BI Dashboard**
- Star-schema data model: a standalone Calendar table (built with DAX `CALENDAR()`) related to all 3 fact tables
- 5 DAX measures: Total Visitors, Conversion Rate %, Total Views, Average Sentiment Score, Positive Review %
- Visuals: customer journey funnel, sentiment breakdown, top negative review themes, KPI cards

## Key Findings

- **Conversion rate: 36%** of visitors who entered the funnel completed a purchase
- **Quality complaints dominate negative feedback** — 58% of negative reviews cite product quality, more than 3x the next-largest theme (Price)
- Hybrid sentiment scoring rescued cases where VADER alone returned a neutral/blank score despite a clearly positive or negative star rating

## Tech Stack

- **SQL Server** — data validation, cleaning, transformation
- **Python** (VADER, pandas-free stdlib) — sentiment analysis, theme extraction
- **Power BI** — data modeling (DAX), dashboard visualization

## Files

| File | Purpose |
|---|---|
| `generate_data.py` | Synthetic raw data generator |
| `00_create_tables.sql` | Table schema creation |
| `01_data_validation.sql` | Data quality validation queries |
| `02_cleaning_transformation.sql` | Cleaning and transformation logic |
| `03_sentiment_analysis.py` | Hybrid VADER + rating sentiment scoring |
| `04_theme_extraction.py` | Keyword-based complaint theme tagging |
| `Shop Easy_Dashboard.pbix` | Power BI dashboard file |
| `reviews_final.csv` | Final sentiment-scored review dataset |

## Author

Aasa Singh Sabharwal — [LinkedIn](https://linkedin.com/in/aasasingh) · [GitHub](https://github.com/Aasa2212)

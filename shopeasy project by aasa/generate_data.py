"""
shopeasy synthetic data generator
-----------------------------------
basically recreating the 3 raw tables from scratch, but with my own random seed
and smaller scale (~1500 journey rows, ~500 reviews, ~1700 engagement rows)

deliberately injecting some messy stuff (dupes, null durations, casing issues)
so later we can practice writing the SQL cleaning scripts on OUR OWN data
"""

import random
from datetime import datetime, timedelta
import csv

random.seed(42)  # so results are reproducible when i re-run this

# ---- reference lists ----
products = [
    "Running Shoes", "Yoga Mat", "Golf Clubs", "Basketball", "Tennis Racket",
    "Dumbbells", "Fitness Tracker", "Swim Goggles", "Boxing Gloves",
    "Cycling Helmet", "Soccer Ball", "Football Helmet", "Hockey Stick",
    "Climbing Rope", "Baseball Glove", "Surfboard", "Volleyball"
]
product_ids = {name: i + 1 for i, name in enumerate(products)}

stages = ["View", "Click", "Purchase", "Drop-off"]
# messing up casing on purpose for a few, like the real repo found
stage_variants = {
    "View": ["View", "view", "VIEW"],
    "Click": ["Click", "click"],
    "Purchase": ["Purchase", "purchase"],
    "Drop-off": ["Drop-off", "drop-off"]
}

content_types = ["Video", "Blog", "Social Media", "Newsletter"]
content_variants = {
    "Video": ["Video", "video", "VIDEO"],
    "Blog": ["Blog", "blog"],
    "Social Media": ["Social Media", "social media"],
    "Newsletter": ["Newsletter", "newsletter"]
}

n_customers = 300
customer_ids = list(range(1001, 1001 + n_customers))

start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)

def random_date():
    delta = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, delta))

# ---------------------------------------------------------------
# 1. customer_journey table (~1500 rows, funnel behavior)
# ---------------------------------------------------------------
journey_rows = []
journey_id = 1

for _ in range(1500):
    cust = random.choice(customer_ids)
    prod = random.choice(products)
    visit_date = random_date()

    # weighted funnel: most people View, fewer Click, even fewer Purchase, rest Drop-off
    stage = random.choices(stages, weights=[45, 25, 8, 22])[0]
    stage_display = random.choice(stage_variants[stage])  # inject casing mess

    action = "Completed" if stage == "Purchase" else ("Abandoned" if stage == "Drop-off" else "In-progress")

    # drop-off rows should have NULL duration (mirrors the real pattern we want to preserve, not impute)
    if stage == "Drop-off":
        duration = ""  # empty = NULL when loaded into sql
    else:
        duration = random.randint(5, 600)  # seconds spent

    journey_rows.append([
        journey_id, cust, product_ids[prod], visit_date.strftime("%Y-%m-%d"),
        stage_display, duration, action
    ])
    journey_id += 1

# inject ~30 logical duplicates (same customer+product+date+stage+action, different JourneyID)
# this mirrors the "PK-invisible" duplicate issue from the original project
for _ in range(30):
    dupe = random.choice(journey_rows).copy()
    dupe[0] = journey_id  # new journey id, so PK looks unique but it's a logical dupe
    journey_rows.append(dupe)
    journey_id += 1

with open("/home/claude/shopeasy/customer_journey_raw.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["JourneyID", "CustomerID", "ProductID", "VisitDate", "Stage", "Duration", "Action"])
    w.writerows(journey_rows)

# ---------------------------------------------------------------
# 2. customer_reviews table (~500 rows, text + rating)
# ---------------------------------------------------------------
positive_snippets = [
    "works great and arrived fast", "exactly what i needed for training",
    "quality is top notch", "very happy with this purchase",
    "exceeded my expectations", "comfortable and well made",
    "great value for the price", "will buy again"
]
negative_snippets = [
    "did not meet my expectations", "average quality for the price",
    "arrived late and packaging was damaged", "expected better performance",
    "too expensive for what you get", "stopped working after a week",
    "sizing was way off from the description", "customer service never responded"
]
mixed_snippets = [
    "good product but delivery took forever", "quality is fine but price is too high",
    "does the job but description was misleading", "decent but not as expected"
]

review_rows = []
review_id = 1
for _ in range(500):
    cust = random.choice(customer_ids)
    prod = random.choice(products)
    review_date = random_date()

    rating = random.choices([1, 2, 3, 4, 5], weights=[8, 8, 20, 30, 34])[0]

    if rating >= 4:
        text = random.choice(positive_snippets)
    elif rating == 3:
        text = random.choice(mixed_snippets)
    else:
        text = random.choice(negative_snippets)

    # sprinkle whitespace mess on ~15% of rows (mirrors original data quality issue)
    if random.random() < 0.15:
        text = "  " + text + "   "

    review_rows.append([review_id, cust, product_ids[prod], text, rating, review_date.strftime("%Y-%m-%d")])
    review_id += 1

with open("/home/claude/shopeasy/customer_reviews_raw.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ReviewID", "CustomerID", "ProductID", "ReviewText", "Rating", "ReviewDate"])
    w.writerows(review_rows)

# ---------------------------------------------------------------
# 3. engagement_data table (~1700 rows, marketing content performance)
# ---------------------------------------------------------------
engagement_rows = []
engagement_id = 1
for _ in range(1700):
    content = random.choice(content_types)
    content_display = random.choice(content_variants[content])
    eng_date = random_date()

    views = random.randint(50, 5000)
    clicks = int(views * random.uniform(0.15, 0.25))  # ~15-25% ctr, mirrors real project
    likes = int(clicks * random.uniform(0.2, 0.4))

    # combine views+clicks into one messy string column for ~20% of rows
    # (mirrors the "1500-300" combined column issue from the original repo)
    if random.random() < 0.2:
        views_clicks_combined = f"{views}-{clicks}"
        engagement_rows.append([engagement_id, content_display, views_clicks_combined, "", likes,
                                 random.randint(1, 20), eng_date.strftime("%Y-%m-%d")])
    else:
        engagement_rows.append([engagement_id, content_display, views, clicks, likes,
                                 random.randint(1, 20), eng_date.strftime("%Y-%m-%d")])
    engagement_id += 1

with open("/home/claude/shopeasy/engagement_data_raw.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["EngagementID", "ContentType", "Views", "Clicks", "Likes", "CampaignID", "Date"])
    w.writerows(engagement_rows)

print("done. files written:")
print("- customer_journey_raw.csv:", len(journey_rows), "rows")
print("- customer_reviews_raw.csv:", len(review_rows), "rows")
print("- engagement_data_raw.csv:", len(engagement_rows), "rows")

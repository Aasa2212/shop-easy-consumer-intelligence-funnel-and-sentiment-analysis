"""
theme extraction: find WHY reviews are positive/negative, not just IF
-------------------------------------------------------------------------
approach: keyword bucket matching (simple, explainable, no black-box ML)
we scan each review's text for words belonging to a theme, and tag it.
one review can belong to multiple themes if it mentions multiple things.
"""

import csv

# theme buckets, built by actually looking at our negative review text first
# (not guessed blindly - this matters, always inspect real data before defining rules)
THEME_KEYWORDS = {
    "Shipping/Delivery": ["arrived", "late", "packaging", "damaged", "delivery", "shipping", "forever"],
    "Quality": ["quality", "stopped working", "sizing", "description", "misleading", "performance", "expected"],
    "Price": ["expensive", "price", "value", "cost", "worth"],
    "Customer Service": ["customer service", "responded", "support", "response"]
}

def extract_themes(text):
    text_lower = text.lower()
    matched_themes = []
    for theme, keywords in THEME_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            matched_themes.append(theme)
    return matched_themes if matched_themes else ["General"]

# run on our sentiment-scored data
rows = []
with open("/home/claude/shopeasy/reviews_with_sentiment.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        themes = extract_themes(row["ReviewText"])
        row["Themes"] = ", ".join(themes)
        rows.append(row)

# write final output with themes added
with open("/home/claude/shopeasy/reviews_final.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

# show a sample of negative reviews with their themes
print("sample negative reviews with themes:")
print("-" * 80)
for r in rows:
    if r["Sentiment_Label"] == "Negative":
        print(f"[{r['Themes']}] {r['ReviewText']}")

# count how often each theme appears among negative reviews specifically
from collections import Counter
theme_counter = Counter()
for r in rows:
    if r["Sentiment_Label"] == "Negative":
        for theme in r["Themes"].split(", "):
            theme_counter[theme] += 1

print("\ntheme frequency among NEGATIVE reviews:")
for theme, count in theme_counter.most_common():
    print(f"  {theme}: {count}")

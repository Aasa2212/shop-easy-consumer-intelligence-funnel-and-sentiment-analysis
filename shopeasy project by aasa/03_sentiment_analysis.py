"""
hybrid sentiment analysis: VADER (text) + star rating
-------------------------------------------------------
why hybrid? we just proved VADER alone misses things like
"did not meet my expectations" (scored as neutral, should be negative)

so instead of trusting VADER 100%, we blend it with the star rating,
which is a direct, reliable signal straight from the customer.

weighting: rating counts more (60%) than VADER text score (40%),
because star ratings are unambiguous while text sentiment can be tricky
to parse correctly, especially with sarcasm, slang, or mixed reviews.
"""

import csv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

# column order in our clean csv (no header row, so we define manually)
# ReviewID, CustomerID, ProductID, ReviewText, Rating, ReviewDate

def normalize_vader(compound):
    """
    VADER compound score is -1 to +1.
    we shift/scale it to 0 to 1 so it's on the same scale as our rating score.
    formula: (score + 1) / 2   e.g. -1 -> 0, 0 -> 0.5, 1 -> 1
    """
    return (compound + 1) / 2

def normalize_rating(rating):
    """
    Rating is 1 to 5 stars.
    we scale it to 0 to 1 so it matches VADER's normalized range.
    formula: (rating - 1) / 4   e.g. 1 star -> 0, 3 stars -> 0.5, 5 stars -> 1
    """
    return (rating - 1) / 4

def hybrid_score(text, rating):
    vader_compound = analyzer.polarity_scores(text)['compound']
    vader_norm = normalize_vader(vader_compound)
    rating_norm = normalize_rating(rating)

    # weighted blend: rating counts more since it's a direct, unambiguous signal
    combined = (0.6 * rating_norm) + (0.4 * vader_norm)
    return combined, vader_compound

def label_from_score(combined):
    """turn the final 0-1 combined score into a simple 3-class label"""
    if combined >= 0.6:
        return "Positive"
    elif combined <= 0.4:
        return "Negative"
    else:
        return "Neutral"

# ---- run on our real clean data ----
results = []
with open("/home/claude/shopeasy/customer_reviews_clean.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    for row in reader:
        review_id, customer_id, product_id, review_text, rating, review_date = row
        rating = int(rating)

        combined, vader_raw = hybrid_score(review_text, rating)
        label = label_from_score(combined)

        results.append({
            "ReviewID": review_id,
            "CustomerID": customer_id,
            "ProductID": product_id,
            "ReviewText": review_text,
            "Rating": rating,
            "ReviewDate": review_date,
            "VADER_Compound": round(vader_raw, 3),
            "Hybrid_Score": round(combined, 3),
            "Sentiment_Label": label
        })

# print first 10 so we can sanity check before writing the full file
print(f"{'Rating':<7}{'VADER':<8}{'Hybrid':<8}{'Label':<10}Review Text")
print("-" * 90)
for r in results[:10]:
    print(f"{r['Rating']:<7}{r['VADER_Compound']:<8}{r['Hybrid_Score']:<8}{r['Sentiment_Label']:<10}{r['ReviewText'][:50]}")

# write full output
with open("/home/claude/shopeasy/reviews_with_sentiment.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print(f"\ndone. wrote {len(results)} rows to reviews_with_sentiment.csv")

# quick label distribution
from collections import Counter
label_counts = Counter(r["Sentiment_Label"] for r in results)
print("\nsentiment distribution:")
for label, count in label_counts.items():
    print(f"  {label}: {count} ({count/len(results)*100:.1f}%)")

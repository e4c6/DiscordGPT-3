from string import Template


def prep_sentiment(results):
    if len(results) != 3:
        raise ValueError("Expected three results from sentiment array.")
    values = [r["score"] for r in results]
    chosen_item_index = values.index(max(values))
    values[chosen_item_index] = str(values[chosen_item_index]) + " ✅"
    positive, negative, neutral = values
    sentiments = Template("""
        Sentiment:
        Positive: $positive
        Negative: $negative
        Neutral: $neutral
        """).substitute(positive=positive, negative=negative, neutral=neutral)

    return sentiments

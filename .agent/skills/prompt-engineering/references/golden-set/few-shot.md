---
pattern: few-shot
model: claude-sonnet-4-6
applies-to: [claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001]
last-verified-against: claude-sonnet-4-6
verified-date: 2026-02-24
---

## Input Prompt

User (example 1): Classify sentiment: "Product arrived broken and customer service was useless."
Assistant (example 1): {"sentiment": "negative", "confidence": 0.97}

User (example 2): Classify sentiment: "Fast shipping and exactly what I ordered."
Assistant (example 2): {"sentiment": "positive", "confidence": 0.95}

User (real): Classify the sentiment of the following text.

Text: The packaging was a bit dented but the item inside was perfect.

## Expected Output Criteria

- Returns valid JSON with "sentiment" and "confidence" fields
- Sentiment value is one of: "positive", "negative", "neutral"
- Confidence is a number between 0 and 1
- Correctly identifies the mixed/neutral sentiment (dented packaging vs perfect item)
- Does not wrap the JSON in markdown code fences

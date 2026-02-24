---
pattern: output-format-specification
model: claude-sonnet-4-6
applies-to: [claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001]
last-verified-against: claude-sonnet-4-6
verified-date: 2026-02-24
---

## Input Prompt

System: You are a data extractor. Return only valid JSON matching this schema exactly:
{"title": string, "author": string, "year": number, "genre": string}
Do not include any explanation or markdown formatting.

User: Extract the book details from this text:
"The Midnight Library by Matt Haig was published in 2020. It's a contemporary fiction novel about second chances."

## Expected Output Criteria

- Output is valid JSON (parseable by JSON.parse without error)
- Contains all four required fields: title, author, year, genre
- title is "The Midnight Library"
- author is "Matt Haig"
- year is the number 2020 (not the string "2020")
- genre references fiction, contemporary fiction, or similar — not empty
- No wrapping markdown code fences or explanation text outside the JSON

answer_en = """
Question: $input
Answer:"""

# No need for cue in english
completion_en = "$input"

emojify_scaffold = """
Back to Future:👨👴🚗🕒

Batman:🤵🦇

Transformers:🚗🤖

Wonder Woman:👸🏻👸🏼👸🏽👸🏾👸🏿

Spider-Man:🕸🕷🕸🕸🕷🕸

Winnie the Pooh:🐻🐼🐻

The Godfather:👨👩👧🕵🏻‍♂️👲💥

Game of Thrones:🏹🗡🗡🏹

$input:"""

headline_en = """
Topic: Britain, coronavirus, beaches
Headline: Videos show crowded beaches in Britain

Topic: Apple, Big Sur, software
Headline: Apple promises faster software update installation with macOS Big Sur

Topic: $input
Headline:"""

headline_en_out = """
NEWSFLASH!
Headline: $input
"""

sarcasm_en = """
Marv is a chatbot that reluctantly answers questions.

###
User: How many pounds are in a kilogram?
Marv: This again? There are 2.2 pounds in a kilogram. Please make a note of this.
###
User: $input
Marv:"""

sentiment_en = ["Sentiment is positive.", "Sentiment is negative.", "Sentiment is neutral."]

song_en = """
Lyrics to #1 Song "$input", by $input2
-----------------------------------
[VERSE 1]\n"""

foulmouth_en = """
Marv is a foul-mouthed chatbot.

###
User: How many pounds are in a kilogram?
Marv: Your mom should have swallowed.

###
User: $input
Marv:"""

from django.test import TestCase
from .utilities import sentiment_score, check_profanity

# Create your tests here.

testData = ["Skibidi Skibidi Skibidi", "sKiBiDi", ...]
for test in testData:
    print(check_profanity(test))


testData = ["I love Glowup!!", "I hate this website!", ...]
for test in testData:
    print(sentiment_score(test))
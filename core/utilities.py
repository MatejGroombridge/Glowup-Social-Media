from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import csv

# defining global variables to store the sentiment analysis model and tokenizer
global model
global tokenizer

# Load the sentiment analysis model and tokenizer. 
tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

# function to check the sentiment of a text input
def sentiment_score(review):
    tokens = tokenizer.encode(review, return_tensors='pt')
    result = model(tokens)

    # return integer between 1 and 5
    return int(torch.argmax(result.logits))+1

# function to check if a text input contains profanity
def check_profanity(textInput):
    filename = 'static/blocklist.csv'
    punct = ['!', '#', '"', '%', '$', '&', ')', '(', '+', '*', '-', '@', '^', '_', '`', '{', '}', '[', ']', '|', '~', ':', ';', '<', '>', '=', '?', ',', '.', '/']
    
    textProcessed = ''
    
    # remove newlines
    while textInput.find("\n") != -1:
        textInput = textInput.replace("\n", " ")

    # remove punctuation and spaces, and convert to lowercase
    for line in textInput.splitlines():
        line = line.lower().replace(" ", "")

        for punctuation in punct:
            line = line.replace(punctuation, "")

        # replace numbers with letters
        for char in line:
            if char == "0":
                textProcessed = textProcessed + "o"
            elif char == "1":
                textProcessed = textProcessed + "i"
            elif char == "3":
                textProcessed = textProcessed + "e"
            elif char == "5":
                textProcessed = textProcessed + "s"
            elif char == "8":
                textProcessed = textProcessed + "b"
            elif char == "9":
                textProcessed = textProcessed + "g"
            elif char == "4":
                textProcessed = textProcessed + "a"
            elif char == "7":
                textProcessed = textProcessed + "t"
            elif char == "6":
                textProcessed = textProcessed + "b"
            elif char == "2":
                textProcessed = textProcessed + "z"
            else:
                textProcessed = textProcessed + char

    # cycle through the blocklist and check if the text input contains any of the words
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] in textProcessed:
                return True
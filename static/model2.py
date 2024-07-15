import torch
from transformers import BertTokenizer, BertForSequenceClassification

# Load pre-trained model and tokenizer
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

# Set seed for reproducibility
torch.manual_seed(42)

# Define function to classify sentiment
def predict_sentiment(text):
    # Tokenize input text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    # Perform forward pass
    with torch.no_grad():
        outputs = model(**inputs)

    # Get predicted label (0: negative, 1: positive)
    predicted_label = torch.argmax(outputs.logits).item()

    # Map label to sentiment
    sentiment = "positive" if predicted_label == 1 else "negative"
    return sentiment

# Example usage
text = "I loved this movie, it was fantastic!"
print("Sentiment:", predict_sentiment(text))

asdf = "I hate you"
print("Sentimentasdf:", predict_sentiment(asdf))

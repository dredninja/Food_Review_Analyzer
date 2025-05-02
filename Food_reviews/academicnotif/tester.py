import torch
from DLModels import LSTMClassifier, create_vocab_and_encode, clean_text
import pandas as pd

# Load the trained model and vocab
model_path = 'sentiment_analysis_lstm.pth'
vocab_path = "vocab.pth"

vocab = torch.load(vocab_path)
model = LSTMClassifier(vocab_size=len(vocab) + 1)
model.load_state_dict(torch.load(model_path))
model.eval()

# Preprocess and encode the review
def predict_sentiment(review):
    cleaned_review = clean_text(review)
    encoded_review = torch.tensor([vocab.get(word, 0) for word in cleaned_review.split()], dtype=torch.long)
    encoded_review = encoded_review.unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        output = model(encoded_review)
        sentiment = torch.argmax(output, dim=1).item()

    return ["Negative", "Neutral", "Positive"][sentiment]

# Test reviews
test_reviews = [
    "The delivery was excellent!",
    "It was okay.",
    "Terrible experience.",
]

for review in test_reviews:
    sentiment = predict_sentiment(review)
    print(f"Review: {review} => Sentiment: {sentiment}")

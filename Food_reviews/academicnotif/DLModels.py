import numpy as np
import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from nltk.corpus import stopwords
import joblib

# Simple Negation Handling
def handle_negation(text):
    negations = ['not', 'no', 'never']
    words = text.split()
    new_words = []
    
    # Flag to identify if we are in a negated context
    negated = False
    for word in words:
        if word in negations:
            negated = True
            new_words.append(word)  # Add negation word
        elif negated:
            # Negate the following word
            new_words.append(f"NOT_{word}")
            negated = False  # Reset negation flag
        else:
            new_words.append(word)
    
    return ' '.join(new_words)

# Preprocess text with negation handling
def clean_text(text):
    # Remove URLs, mentions, hashtags, and punctuation
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    
    # Apply negation handling to the text
    text = handle_negation(text)
    
    # Remove stopwords (but preserve negation words)
    stop_words = set(stopwords.words('english'))
    return ' '.join([word for word in text.split() if word not in stop_words or word in ['not', 'no', 'never']])

def prepare_data(data):
    data['cleaned_text'] = data['content'].apply(clean_text)
    data['sentiment'] = data['score'].apply(lambda x: 0 if x <= 2 else (1 if x == 3 else 2))
    return data

# Main
if __name__ == '__main__':
    # Load and preprocess data
    data = pd.read_csv("C:/Users/adity/Downloads/archive/food_delivery_apps.csv").dropna()
    data = prepare_data(data)

    # Split data into features (X) and labels (y)
    X = data['cleaned_text']
    y = data['sentiment']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # TF-IDF Vectorizer
    tfidf = TfidfVectorizer(max_features=5000)
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)

    # Train Logistic Regression model
    model = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
    model.fit(X_train_tfidf, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test_tfidf)

    # Evaluate the model
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print(cm)

    # Save the model and TF-IDF vectorizer
    joblib.dump(model, 'sentiment_analysis_logistic_regression_with_simple_negation.pkl')
    joblib.dump(tfidf, 'tfidf_vectorizer_with_simple_negation.pkl')
    print("Model and vectorizer saved to disk.")

    # Test predictions on new sentences
    test_sentences = [
        "The food was absolutely amazing!",
        "I did not like the service at all.",
        "Delivery was on time, but the food was cold.",
        "Zomato is the best! Highly recommend it.",
        "I had a terrible experience. Never using this again."
    ]

    print("\nTest Predictions:")
    for sentence in test_sentences:
        # Preprocess the text and transform it using TF-IDF
        cleaned_text = clean_text(sentence)
        transformed_text = tfidf.transform([cleaned_text])
        
        # Predict sentiment
        sentiment_map = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
        prediction = model.predict(transformed_text)
        print(f"Text: {sentence} -> Sentiment: {sentiment_map[prediction[0]]}")








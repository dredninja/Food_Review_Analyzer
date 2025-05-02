import joblib

# Load the saved model and vectorizer
model = joblib.load('sentiment_analysis_logistic_regression.pkl')
tfidf = joblib.load('tfidf_vectorizer.pkl')

def predict_sentiment(review):
    # Preprocess and transform the review using the TF-IDF vectorizer
    cleaned_text = review.lower()  # Add any additional text cleaning logic if needed
    transformed_text = tfidf.transform([cleaned_text])

    # Predict sentiment
    sentiment_map = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
    prediction = model.predict(transformed_text)
    return sentiment_map[prediction[0]]





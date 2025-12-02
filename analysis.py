import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import scrape

 

def analyze_sentiment_from_variable(all_cleaned_comments):
    """
    Takes a Python list of cleaned comments and returns
    a dataframe with sentiment scores and classifications.
    """
    
    # Convert list to DataFrame
    df = pd.DataFrame({'comment': all_cleaned_comments})

    # Initialize sentiment analyzer
    sentiments = SentimentIntensityAnalyzer()

    # Apply VADER sentiment scoring
    df['sentiment_scores'] = df['comment'].apply(lambda x: sentiments.polarity_scores(x))

    # Extract compound scores
    df['Compound'] = df['sentiment_scores'].apply(lambda x: x['compound'])

    # Classify sentiment
    df['Sentiment'] = df['Compound'].apply(
        lambda x: 'Positive' if x >= 0.05 else ('Negative' if x <= -0.05 else 'Neutral')
    )

    # Count each category
    sentiment_counts = df['Sentiment'].value_counts()

    # Format counts for plotting
    sentiment_summary = pd.DataFrame({
        'Sentiment': ['Positive', 'Negative', 'Neutral'],
        'Count': [
            sentiment_counts.get('Positive', 0),
            sentiment_counts.get('Negative', 0),
            sentiment_counts.get('Neutral', 0)
        ]
    })

    return df, sentiment_summary,sentiment_counts




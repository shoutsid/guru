from transformers import pipeline
from nltk.sentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.sentiment_model = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

    def analyze_sentiment(self, text):
        result = self.sentiment_model(text)
        return result

    def analyze_sentiment_intensity(self, text):
        return self.analyzer.polarity_scores(text)

    @staticmethod
    def extract_sentiment(doc, opinions, message_id):
        score = doc[0]['score'] if doc[0]['label'] == 'POSITIVE' else -doc[0]['score']
        opinions[message_id] = (score, message_id)


from transformers import pipeline

class EmotionAnalyzer:
    def __init__(self):
        self.emotion_classifier = pipeline('text-classification', model='bhadresh-savani/distilbert-base-uncased-emotion')

    def analyze_emotions(self, text):
        result = self.emotion_classifier(text)
        return result

    @staticmethod
    def extract_emotions(doc, emotions, message_id):
        doc = doc[0]['label']
        emotions[message_id] = (doc, message_id)


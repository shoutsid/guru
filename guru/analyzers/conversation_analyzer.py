from typing import Dict, Any, List
import spacy
from .utils import install_spacy_model
from guru.db import Entity, Opinion, Topic, Emotion
from sqlmodel import select
from .sentiment_analyzer import SentimentAnalyzer
from .topic_modeler import TopicModeler
from .emotion_analyzer import EmotionAnalyzer
from .entity_analyzer import EntityAnalyzer

try:
    _ = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading and installing spaCy model 'en_core_web_sm'...")
    install_spacy_model("en_core_web_sm")

class ConversationAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_modeler = TopicModeler()
        self.emotion_analyzer = EmotionAnalyzer()
        self.entity_analyzer = EntityAnalyzer()

    def retrieve_analysis_results(self, session) -> Dict[str, List[Dict[str, Any]]]:
        results = {"entities": [], "opinions": [], "topics": [], "emotions": []}

        # Retrieve entities
        entities = session.exec(select(Entity)).all()
        results["entities"] = [{"text": e.text, "label": e.label, "message_id": e.message_id} for e in entities]
        # Retrieve opinions
        opinions = session.exec(select(Opinion)).all()
        results["opinions"] = [{"sentiment_score": o.sentiment_score, "message_id": o.message_id} for o in opinions]
        # Retrieve topics
        topics = session.exec(select(Topic)).all()
        results["topics"] = [{"keywords": t.keywords, "message_id": t.message_id} for t in topics]
        # Retrieve emotions
        emotions = session.exec(select(Emotion)).all()
        results["emotions"] = [{"emotion": t.emotion, "message_id": t.message_id} for t in emotions]

        return results

    def save_analysis_results(self, conversation_analysis: Dict[str, Any], session):
        # Save entities
        print("Entities:")
        existing_entities = set(e.text for e in session.exec(select(Entity)).all())
        for text, (label, message_id) in conversation_analysis["entities"].items():
            if label is not None and text not in existing_entities:
                session.add(Entity(text=text, label=label, message_id=message_id))
                existing_entities.add(text)

        # Save opinions
        print("Opinions:")
        existing_opinions = set(o.message_id for o in session.exec(select(Opinion)).all())
        for _, (sentiment_score, message_id) in conversation_analysis["opinions"].items():
            if sentiment_score is not None and message_id not in existing_opinions:
                session.add(Opinion(sentiment_score=sentiment_score, message_id=message_id))
                existing_opinions.add(message_id)

        # Save topics
        print("Topics:")
        existing_topics = set(t.message_id for t in session.exec(select(Topic)).all())
        for _, (keywords, message_id) in conversation_analysis["topics"].items():
            if keywords is not None and message_id not in existing_topics:
                session.add(Topic(keywords=", ".join(keywords), message_id=message_id))
                existing_topics.add(message_id)

        # Save Emotions
        print("Emotions:")
        existing_emotions = set(e.message_id for e in session.exec(select(Emotion)).all())
        for _, (emotion, message_id) in conversation_analysis["emotions"].items():
            if emotion is not None and message_id not in existing_emotions:
                session.add(Emotion(message_id=message_id, emotion=emotion))
                existing_emotions.add(message_id)

        session.commit()

    def analyze_conversation(self, messages):
        conversation_analysis = {"entities": {}, "opinions": {}, "topics": {}, "emotions": {}}

        for _, msg in enumerate(messages):
            # Entity analysis
            doc = self.analyze_entities(msg["content"])
            self.extract_entities(doc, conversation_analysis["entities"], msg["id"])
            # Sentiment analysis
            doc = self.analyze_sentiment(msg["content"])
            self.extract_sentiment(doc, conversation_analysis["opinions"], msg["id"])
            # Topic analysis
            doc = self.analyze_topics(msg["content"])
            self.extract_topics(doc, conversation_analysis["topics"], msg["id"])
            # Emotion analysis
            doc = self.analyze_emotions(msg["content"])
            self.extract_emotions(doc, conversation_analysis["emotions"], msg["id"])

        return conversation_analysis

    def analyze_entities(self, text):
        return self.entity_analyzer.analyze_entities(text)

    def analyze_sentiment(self, text):
        return self.sentiment_analyzer.analyze_sentiment(text)

    def analyze_topics(self, text):
        return self.topic_modeler.analyze_topics(text)

    def analyze_emotions(self, text):
        return self.emotion_analyzer.analyze_emotions(text)

    def extract_entities(self, doc, entities, message_id):
        return self.entity_analyzer.extract_entities(doc, entities, message_id)

    def extract_sentiment(self, doc, opinions, message_id):
        return self.sentiment_analyzer.extract_sentiment(doc, opinions, message_id)

    def extract_topics(self, doc, topics, message_id):
        return self.topic_modeler.extract_topics(doc, topics, message_id)

    def extract_emotions(self, doc, emotions, message_id):
        return self.emotion_analyzer.extract_emotions(doc, emotions, message_id)


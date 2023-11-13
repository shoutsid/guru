import spacy
import subprocess
import sys

# Function to install spaCy model
def install_spacy_model(model_name):
    subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])

# Check if the spaCy model is installed
try:
    _ = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading and installing spaCy model 'en_core_web_sm'...")
    install_spacy_model("en_core_web_sm")

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

from typing import List, Dict, Any
from sqlmodel import select
from collections import defaultdict
from datetime import datetime
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from bertopic import BERTopic

from townhall.db import Entity, Opinion, Topic, Message, Emotion

class ConversationAnalyzer:
    def __init__(self):
        # Ensure NLTK resources are downloaded
        self.ensure_nltk_resources()

        self.nlp = spacy.load("en_core_web_sm")
        self.analyzer = SentimentIntensityAnalyzer()
        self.lda_model = LatentDirichletAllocation(n_components=5)  # Adjustable parameter
        self.vectorizer = CountVectorizer(stop_words='english')
        self.topic_model = BERTopic(verbose=True)
        self.sentiment_model = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')
        self.emotion_classifier = pipeline('text-classification', model='bhadresh-savani/distilbert-base-uncased-emotion')

    @staticmethod
    def ensure_nltk_resources():
        try:
            nltk.data.find('sentiment/vader_lexicon')
        except LookupError:
            print("Downloading NLTK resources for SentimentIntensityAnalyzer...")
            nltk.download('vader_lexicon')

    def analyze_emotions(self, text: str) -> str:
        result = self.emotion_classifier(text)
        return result[0]['label']

    def preprocess_text(self, text: str) -> str:
        doc = self.nlp(text)
        preprocessed_text = " ".join([token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and token.is_alpha])
        return preprocessed_text

    def save_analysis_results(self, conversation_analysis: Dict[str, Any], session):
        # Save entities
        for text, (label, id) in conversation_analysis["entities"].items():
            session.add(Entity(text=text, label=label, message_id=id))
        # Save opinions
        for sentence, (sentiment_score, id) in conversation_analysis["opinions"].items():
            session.add(Opinion(sentence=sentence, sentiment_score=sentiment_score, message_id=id))
        # Save topics
        for topic_index, keywords in conversation_analysis["topics"].items():
            if keywords is not None:
                print(keywords)
                session.add(Topic(topic_index=topic_index, keywords=", ".join(keywords)))
            else:
                continue
        # Save Emotions
        for message_id, emotion in conversation_analysis["emotions"].items():
            session.add(Emotion(message_id=message_id, emotion=emotion))

        session.commit()

    def retrieve_analysis_results(self, session) -> Dict[str, List[Dict[str, Any]]]:
        results = {"entities": [], "opinions": [], "topics": [], "emotions": []}

        # Retrieve entities
        entities = session.exec(select(Entity)).all()
        results["entities"] = [{"text": e.text, "label": e.label} for e in entities]
        # Retrieve opinions
        opinions = session.exec(select(Opinion)).all()
        results["opinions"] = [{"sentence": o.sentence, "sentiment_score": o.sentiment_score} for o in opinions]
        # Retrieve topics
        topics = session.exec(select(Topic)).all()
        results["topics"] = [{"topic_index": t.topic_index, "keywords": t.keywords} for t in topics]
        # Retrieve emotions
        emotions = session.exec(select(Emotion)).all()
        results["emotions"] = [{"emotion": t.emotion, "message_id": t.message_id} for t in emotions]

        return results

    def analyze_conversation(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        conversation_analysis = {"entities": {}, "opinions": {}, "topics": {}, "emotions": {}}

        for i, msg in enumerate(messages):
            # Entity extraction
            doc = self.nlp(msg["content"])
            self.extract_entities(doc, conversation_analysis["entities"], msg["id"])
            # Sentiment analysis
            sentiment_score = self.analyze_sentiment(msg["content"])
            conversation_analysis["opinions"][msg["id"]] = (sentiment_score, msg["id"])

            # Topic modeling
            try:
                topics = self.extract_topics(msg["content"], conversation_analysis["topics"])
                print(topics)
            except Exception as e:
                print("Error in topic modeling:", e)
                topics = [None]
            conversation_analysis["topics"][msg["id"]] = topics if topics else None

            emotion = self.analyze_emotions(msg["content"])
            conversation_analysis["emotions"][msg["id"]] = emotion

        return conversation_analysis

    def analyze_sentiment(self, text: str) -> float:
        result = self.sentiment_model(text)
        return result[0]['score'] if result[0]['label'] == 'POSITIVE' else -result[0]['score']

    def extract_entities(self, doc, entities: Dict[str, str], message_id: int):
        for ent in doc.ents:
            entities[ent.text] = (ent.label_, message_id)


    def extract_topics(self, text: str, topics: Dict[int, List[str]]):
        X = self.vectorizer.fit_transform([text])
        self.lda_model.fit(X)
        feature_names = self.vectorizer.get_feature_names_out()
        for topic_idx, topic in enumerate(self.lda_model.components_):
            topics[topic_idx] = [feature_names[i] for i in topic.argsort()[:-6:-1]]

# Function to analyze sentiment trends over time
def sentiment_trend_over_time(session, thread_id: int) -> Dict[datetime, float]:
    sentiment_trend = defaultdict(list)

    messages = session.exec(select(Message).where(Message.thread_id == thread_id)).all()
    for message in messages:
        if message.opinions:
            avg_sentiment = sum(op.sentiment_score for op in message.opinions) / len(message.opinions)
            sentiment_trend[message.timestamp].append(avg_sentiment)

    # Calculating average sentiment for each timestamp
    avg_sentiment_trend = {timestamp: sum(sentiments) / len(sentiments) for timestamp, sentiments in sentiment_trend.items()}
    return avg_sentiment_trend

# Function to identify main topics in a thread
def main_topics_in_thread(session, thread_id: int) -> List[str]:
    topic_counts = defaultdict(int)

    messages = session.exec(select(Message).where(Message.thread_id == thread_id)).all()
    for message in messages:
        for topic in message.topics:
            topic_counts[topic.keywords] += 1

    # Sort topics based on frequency
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    return [topic for topic, count in sorted_topics]

def convert_db_messages_to_dict(messages):
    return [{'id': message.id, 'content': message.content} for message in messages]

# if __name__ == "__main__":
#     from townhall.db.utils import Session, SQL_ENGINE
#     session = Session(SQL_ENGINE)
#     conversation_analyzer = ConversationAnalyzer()
#     messages = session.exec(select(Message).where(Message.thread_id == 1)).all()
#     messages = convert_db_messages_to_dict(messages)
#     analysis_result = conversation_analyzer.analyze_conversation(messages)
#     conversation_analyzer.save_analysis_results(analysis_result, session)
#     retrieved_results = conversation_analyzer.retrieve_analysis_results(session)
import logging
from collections import defaultdict
from guru.db import Message, Thread
from guru.db.utils import Session, SQL_ENGINE, convert_db_messages_to_dict
from guru.analyzers.conversation_analyzer import ConversationAnalyzer
from sqlmodel import select

logging.basicConfig(level=logging.INFO)

def learn():
    session = Session(SQL_ENGINE)
    conversation_analyzer = ConversationAnalyzer()
    threads = session.exec(select(Thread)).all()
    for thread in threads:
        logging.info("Thread:")
        logging.info(thread)
        messages = convert_db_messages_to_dict(thread.messages)
        logging.info("Messages:")
        logging.info(messages)

        analysis_result = conversation_analyzer.analyze_conversation(messages)
        logging.info("Analysis result:")
        logging.info(analysis_result)
        conversation_analyzer.save_analysis_results(analysis_result, session)
        retrieved_results = conversation_analyzer.retrieve_analysis_results(session)
        logging.info("Retrieved results:")
        logging.info(retrieved_results)

def sentiment_trend_over_time(session, thread_id):
    sentiment_trend = defaultdict(list)

    messages = session.exec(select(Message).where(Message.thread_id == thread_id)).all()
    for message in messages:
        if message.opinions:
            avg_sentiment = sum(op.sentiment_score for op in message.opinions) / len(message.opinions)
            sentiment_trend[message.timestamp].append(avg_sentiment)

    avg_sentiment_trend = {timestamp: sum(sentiments) / len(sentiments) for timestamp, sentiments in sentiment_trend.items()}
    return avg_sentiment_trend

def main_topics_in_thread(session, thread_id):
    topic_counts = defaultdict(int)

    messages = session.exec(select(Message).where(Message.thread_id == thread_id)).all()
    for message in messages:
        for topic in message.topics:
            topic_counts[topic.keywords] += 1

    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    return [topic for topic, count in sorted_topics]

def analyze_and_save_conversation(thread_id):
    session = Session(SQL_ENGINE)
    conversation_analyzer = ConversationAnalyzer()

    messages = session.exec(select(Message).where(Message.thread_id == thread_id)).all()
    messages = convert_db_messages_to_dict(messages)

    analysis_result = conversation_analyzer.analyze_conversation(messages)
    conversation_analyzer.save_analysis_results(analysis_result, session)

    retrieved_results = conversation_analyzer.retrieve_analysis_results(session)

    return retrieved_results


if __name__ == "__main__":
    session = Session(SQL_ENGINE)
    learn()
    threads = session.exec(select(Thread)).all()
    for thread in threads:
        logging.info("Sentiment trend over time:")
        logging.info(sentiment_trend_over_time(session, thread.id))
        logging.info("Main topics in thread:")
        logging.info(main_topics_in_thread(session, thread.id))
        logging.info("Analysis results:")
        logging.info(analyze_and_save_conversation(thread.id))

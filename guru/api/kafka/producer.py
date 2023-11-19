import os
from confluent_kafka import Producer
import functools
import json
import threading
import logging

logging.basicConfig(level=logging.INFO)

KAFKA_URL = os.environ.get('KAFKA_URL', 'kafka:9092')
DEFAULT_CONFIG = {
    'bootstrap.servers': KAFKA_URL,
    'group.id': 'guru',
    'auto.offset.reset': 'earliest',
}


class KafkaProducerSingleton:
    _instance = None
    _lock = threading.Lock()

    @staticmethod
    def get_instance(config=None):
        with KafkaProducerSingleton._lock:
            if KafkaProducerSingleton._instance is None:
                KafkaProducerSingleton._instance = Producer(
                    config or DEFAULT_CONFIG)
        return KafkaProducerSingleton._instance

    @staticmethod
    def flush():
        if KafkaProducerSingleton._instance is not None:
            KafkaProducerSingleton._instance.flush()


def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def trigger_to_topic(topic, serialize_func=json.dumps):
    def decorator_trigger(func):
        @functools.wraps(func)
        def wrapper_trigger(*args, **kwargs):
            result = func(*args, **kwargs)

            producer = KafkaProducerSingleton.get_instance()

            try:
                message = serialize_func(result)
                producer.produce(topic, message, callback=delivery_report)
            except Exception as e:
                logging.error(f"Error producing message: {e}")

            return result
        return wrapper_trigger
    return decorator_trigger


def on_application_shutdown():
    KafkaProducerSingleton.flush()
    logging.info("Kafka Producer flushed and shut down")


if __name__ == "__main__":
    @trigger_to_topic('example')
    def my_function(data):
        return {"data": data}


    # Test the decorated function
    my_function("Hello Kafka")

    # Ensure to call this on application shutdown
    on_application_shutdown()

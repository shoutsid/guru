import os
import logging
import threading
from confluent_kafka import Consumer, KafkaError
import signal

logging.basicConfig(level=logging.INFO)
KAFKA_URL = os.environ.get('KAFKA_URL', 'kafka:9092')

# Shared variable for graceful shutdown
shutdown_flag = threading.Event()


def create_consumer(config=None):
    default_config = {
        'bootstrap.servers': KAFKA_URL,
        'group.id': 'guru',
        'auto.offset.reset': 'earliest'
    }
    final_config = {**default_config, **(config or {})}
    return Consumer(final_config)


def kafka_consumer_loop(topics, consumer_config=None, deserialize_func=lambda x: x.decode('utf-8')):
    def decorator(func):
        def wrapper(*args, **kwargs):
            consumer_threads = []

            def consumer_thread():
                consumer = create_consumer(consumer_config)
                consumer.subscribe(topics)

                try:
                    while not shutdown_flag.is_set():
                        msg = consumer.poll(1)
                        if msg is None:
                            continue
                        if msg.error():
                            if msg.error().code() != KafkaError._PARTITION_EOF:
                                logging.error(
                                    f'Error in consumer: {msg.error()}')
                        else:
                            try:
                                message = deserialize_func(msg.value())
                                func(message, *args, **kwargs)
                            except Exception as e:
                                logging.error(f"Error processing message: {e}")
                finally:
                    consumer.close()
                    logging.info("Consumer closed")

            thread = threading.Thread(target=consumer_thread)
            thread.daemon = True
            thread.start()
            consumer_threads.append(thread)

            # Wait for threads to complete
            for t in consumer_threads:
                t.join()

        return wrapper
    return decorator

# Signal handler to set shutdown flag


def signal_handler(signum, frame):
    shutdown_flag.set()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Decorated functions


@kafka_consumer_loop(topics=["example"])
def process_message(message):
    logging.info(f"Processing message: {message}")


@kafka_consumer_loop(topics=["example"])
def process_message_two(message):
    logging.info(f"Processing message two: {message}")


if __name__ == "__main__":
    process_message()
    process_message_two()

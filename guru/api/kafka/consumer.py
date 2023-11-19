import os
import logging
import threading
from confluent_kafka import Consumer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
import signal
import time  # Added for delay

logging.basicConfig(level=logging.INFO)
KAFKA_URL = os.environ.get('KAFKA_URL', 'kafka:9092')

# Shared variable for graceful shutdown
shutdown_flag = threading.Event()
DEFAULT_CONFIG = {
    'bootstrap.servers': KAFKA_URL,
    'group.id': 'guru',
    'auto.offset.reset': 'earliest',
}


def create_admin_client():
    return AdminClient(DEFAULT_CONFIG)


def create_topic(topic_name, num_partitions=1, replication_factor=1):
    admin_client = create_admin_client()
    topic_list = [NewTopic(
        topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
    try:
        # dict(<topic_name, future>)
        list = admin_client.create_topics(topic_list)
        results = []
        for topic, future in list.items():
            future_result = future.result()   # wait for future to complete
            logging.info(f"Created topic {topic}: {future_result}")
            results.append(future_result)
        logging.info(f"Successfully created topic: {topic_name}")
    except Exception as e:
        logging.error(f"Failed to create topic {topic_name}: {e}")

def create_consumer(config=None):
   final_config = {**DEFAULT_CONFIG, **(config or {})}
   return Consumer(final_config)

def kafka_consumer_loop(topics, consumer_config=None, deserialize_func=lambda x: x.decode('utf-8')):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Ensure topics exist
            for topic in topics:
                create_topic(topic)

            # Delay to allow topics to be fully initialized in Kafka
            time.sleep(10)  # Delay for 10 seconds

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
                            # switch case switch on error().code()
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

def signal_handler(signum, frame):
    shutdown_flag.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


@kafka_consumer_loop(topics=[
    "discord_channel_update", "discord_guild_update",
    "discord_message_update", "discord_user_update", "discord_thread_update"])
def process_discord_update(message):
    logging.info(f"Processing message: {message}")
    print(f"Processing message: {message}")

# @kafka_consumer_loop(topics=["example"])
# def process_message_two(message):
#     logging.info(f"Processing message two: {message}")

if __name__ == "__main__":
    process_discord_update()
    # process_message_two()

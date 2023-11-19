require 'karafka'

class KafkaProducer
  # Sends data to a Kafka topic
  # @param topic [String] the Kafka topic to send the data to
  # @param data [Hash] the data to be sent, which will be serialized to JSON
  def self.publish(topic, data)
    serialized_data = serialize(data)
    produce(topic, serialized_data)
  end

  # Serializes the data to JSON
  # Handles any serialization errors
  def self.serialize(data)
    data.to_json
  rescue StandardError => e
    Rails.logger.error("KafkaProducer Serialization Error: #{e.message}")
    nil # Or handle the error as required
  end

  # Asynchronously produces the message to the Kafka topic
  # Handles any Kafka production errors
  def self.produce(topic, data)
    return if data.nil?

    Karafka.producer.produce_async(topic: topic, payload: data)
  rescue Kafka::DeliveryFailed => e
    Rails.logger.error("KafkaProducer Delivery Failed: #{e.message}")
    # Implement your error handling strategy (e.g., retry, log, alert)
  rescue StandardError => e
    Rails.logger.error("KafkaProducer Error: #{e.message}")
    # Handle other unexpected errors
  end
end

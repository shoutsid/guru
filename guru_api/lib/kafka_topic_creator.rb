require 'kafka'

class KafkaTopicCreator
  def initialize(brokers:, topics:)
    @kafka = Kafka.new(brokers)
    @topics = topics
  end

  def create_missing_topics
    existing_topics = @kafka.topics
    @topics.each do |topic_name|
      next if existing_topics.include?(topic_name)

      # Customize these options as needed
      @kafka.create_topic(topic_name, num_partitions: 3, replication_factor: 1)
      puts "Created Kafka topic: #{topic_name}"
    end
  end
end

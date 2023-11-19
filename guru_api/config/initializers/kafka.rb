require 'kafka_topic_creator'

# Create Kafka topics if they don't exist
# Do not do this on asset:precompile step
unless ENV["SECRET_KEY_BASE_DUMMY"].present?
  KafkaTopicCreator.new(
    brokers: [ENV.fetch('KAFKA_URL', 'kafka:9092')],
    topics: ['discord_guild', 'discord_user', 'discord_message', 'discord_channel', 'discord_thread', 'open_ai_assistant', 'open_ai_thread', 'open_ai_message', 'concept_origin']
  ).create_missing_topics
end
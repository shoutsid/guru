require 'karafka'
require 'karafka/web'

class KarafkaApp < Karafka::App
  setup do |config|
    kafka_url = ENV.fetch('KAFKA_URL') { 'kafka:9092' }
    config.kafka = { 'bootstrap.servers': kafka_url }
    config.consumer_persistence = !Rails.env.development?
  end

  Karafka.monitor.subscribe(Karafka::Instrumentation::LoggerListener.new)
  # Karafka.monitor.subscribe(Karafka::Instrumentation::ProctitleListener.new)

  Karafka.producer.monitor.subscribe(
    WaterDrop::Instrumentation::LoggerListener.new(
      Karafka.logger,
      log_messages: false
    )
  )

  routes.draw do
    active_job_topic :default
    # DISCORD
    topic :discord_guild do
      consumer DiscordGuildConsumer
    end
    topic :discord_user do
      consumer DiscordUserConsumer
    end
    topic :discord_message do
      consumer DiscordMessageConsumer
    end
    topic :discord_channel do
      consumer DiscordChannelConsumer
    end
    topic :discord_thread do
      consumer DiscordThreadConsumer
    end

    # OPEN AI
    topic :open_ai_assistant do
      consumer OpenAiAssistantConsumer
    end
    topic :open_ai_thread do
      consumer OpenAiThreadConsumer
    end
    topic :open_ai_message do
      consumer OpenAiMessageConsumer
    end

    # CONCEPT ORIGIN
    topic :concept_origin do
      consumer ConceptOriginConsumer
    end
  end
end

# frozen_string_literal: true
Karafka::Web.setup do |config|
  # You may want to set it per ENV. This value was randomly generated.
  config.ui.sessions.secret = 'a86d9ac3e95f21b8de7d249784145f9cdde6dc4b1876cc5ee324ba54a90c9cb8'
end

Karafka::Web.enable!

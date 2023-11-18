# app/controllers/kafka_messages_controller.rb
class KafkaMessagesController < ApplicationController

  # Example of API endpoint that sends a message to Kafka
  def create
    message = params[:message]
    kafka_producer.produce(message, topic: 'rails_topic')
    kafka_producer.deliver_messages
    render json: { status: 'Message sent to Kafka' }
  end
end
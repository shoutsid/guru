# frozen_string_literal: true

class OpenAiAssistantConsumer < ApplicationConsumer
  def consume
    messages.payloads.each do |payload|
      Rails.logger.debug("OpenAiAssistantConsumer: #{payload}")
      OpenAiAssistant.upsert payload
    end
  end
end

# frozen_string_literal: true

class OpenAiMessageConsumer < ApplicationConsumer
  def consume
    messages.payloads.each do |payload|
      Rails.logger.debug("OpenAiMessageConsumer: #{payload}")
      OpenAiMessage.upsert payload
    end
  end
end

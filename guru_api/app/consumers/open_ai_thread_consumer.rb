# frozen_string_literal: true

class OpenAiThreadConsumer < ApplicationConsumer
  def consume
    messages.payloads.each do |payload|
      Rails.logger.debug("OpenAiThreadConsumer: #{payload}")
      OpenAiThread.upsert payload
    end
  end
end

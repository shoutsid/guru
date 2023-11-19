# frozen_string_literal: true

class DiscordMessageConsumer < ApplicationConsumer
  def consume
    messages.payloads.each do |payload|
      Rails.logger.debug("DiscordMessageConsumer: #{payload}")
      DiscordMessage.upsert payload
    end
  end
end

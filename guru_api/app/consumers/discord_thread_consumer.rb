# frozen_string_literal: true

class DiscordThreadConsumer < ApplicationConsumer
  def consume
    messages.payloads.each do |payload|
      Rails.logger.debug("DiscordThreadConsumer: #{payload}")
      DiscordThread.upsert payload
    end
  end
end

# frozen_string_literal: true

class DiscordMessageConsumer < ApplicationConsumer
  def consume
    messages.payloads.each do |payload|
      Rails.logger.debug("DiscordMessageConsumer: #{payload}")
      message = DiscordMessage.find_or_create_by!(id: payload['discord_id'])
      message.update!(payload)
    end
  end
end

# frozen_string_literal: true

class DiscordUserConsumer < ApplicationConsumer
  def consume
    messages.payloads.each do |payload|
      Rails.logger.debug("DiscordUserConsumer: #{payload}")
      DiscordUser.upsert payload
    end
  end
end

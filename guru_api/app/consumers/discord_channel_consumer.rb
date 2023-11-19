# frozen_string_literal: true

class DiscordChannelConsumer < ApplicationConsumer
  def consume
    # TODO: sort out how to handle multiple of the same messages
    messages.payloads.each do |payload|
      Rails.logger.debug("DiscordChannelConsumer: #{payload}")
      DiscordChannel.upsert payload
    end
  end
end

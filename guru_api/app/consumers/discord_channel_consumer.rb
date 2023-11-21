# frozen_string_literal: true

class DiscordChannelConsumer < ApplicationConsumer
  # fingers crossed this this is fifo
  def consume
    messages.payloads.each do |payload|
      Rails.logger.debug("DiscordChannelConsumer: #{payload}")
      channel =  DiscordChannel.find(payload['discord_id'])
      channel.update!(payload)
    end
  end
end

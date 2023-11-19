# frozen_string_literal: true

class DiscordChannelConsumer < ApplicationConsumer
  def consume
    DiscordChannel.upsert_all messages.payloads
  end
end

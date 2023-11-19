# frozen_string_literal: true

class DiscordMessageConsumer < ApplicationConsumer
  def consume
    DiscordMessage.upsert_all messages.payloads
  end
end

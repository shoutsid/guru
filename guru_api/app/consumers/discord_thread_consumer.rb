# frozen_string_literal: true

class DiscordThreadConsumer < ApplicationConsumer
  def consume
    DiscordThread.upsert_all messages.payloads
  end
end

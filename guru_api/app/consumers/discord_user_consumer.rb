# frozen_string_literal: true

class DiscordUserConsumer < ApplicationConsumer
  def consume
    DiscordUser.upsert_all messages.payloads
  end
end

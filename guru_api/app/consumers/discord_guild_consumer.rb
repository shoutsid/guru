# frozen_string_literal: true

class DiscordGuildConsumer < ApplicationConsumer
  def consume
    DiscordGuild.upsert_all messages.payloads
  end
end

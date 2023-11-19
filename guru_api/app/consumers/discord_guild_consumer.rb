# frozen_string_literal: true

class DiscordGuildConsumer < ApplicationConsumer
  def consume
    messages.payloads.each do |payload|
      Rails.logger.debug("DiscordGuildConsumer: #{payload}")
      DiscordGuild.upsert payload
    end
  end
end

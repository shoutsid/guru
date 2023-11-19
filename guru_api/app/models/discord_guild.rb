class DiscordGuild < ApplicationRecord
  include KafkaEventPublisher
  has_many :channels, class_name: 'DiscordChannel', foreign_key: 'guild_id', primary_key: 'discord_id'
  has_many :messages, class_name: 'DiscordMessage', foreign_key: 'guild_id', primary_key: 'discord_id'
end

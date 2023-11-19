class DiscordMessage < ApplicationRecord
  include KafkaEventPublisher

  self.primary_key = 'discord_id'
  belongs_to :author, class_name: 'DiscordUser', foreign_key: 'author_id', primary_key: 'discord_id'
  belongs_to :channel, class_name: 'DiscordChannel', foreign_key: 'channel_id', primary_key: 'discord_id'
  belongs_to :guild, class_name: 'DiscordGuild', foreign_key: 'guild_id', primary_key: 'discord_id'
end

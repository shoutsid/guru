class DiscordChannel < ApplicationRecord
  self.inheritance_column = :_type_disabled

  belongs_to :guild, class_name: 'DiscordGuild', foreign_key: 'guild_id', primary_key: 'discord_id'
  has_many :messages, class_name: 'DiscordMessage', foreign_key: 'channel_id', primary_key: 'discord_id'
end

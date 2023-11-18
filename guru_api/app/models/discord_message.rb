class DiscordMessage < ApplicationRecord
  belongs_to :author, class_name: 'DiscordUser', foreign_key: 'author_id'
  belongs_to :channel, class_name: 'DiscordChannel', foreign_key: 'channel_id'
  belongs_to :guild, class_name: 'DiscordGuild', foreign_key: 'guild_id'
end

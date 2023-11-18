class DiscordUser < ApplicationRecord
  has_many :messages, class_name: 'DiscordMessage', foreign_key: 'author_id', primary_key: 'discord_id'
  has_many :threads, class_name: 'DiscordThread', foreign_key: 'owner_id', primary_key: 'discord_id'
end

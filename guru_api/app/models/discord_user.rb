class DiscordUser < ApplicationRecord
  has_many :messages, class_name: 'DiscordMessage', foreign_key: 'author_id'
  has_many :threads, class_name: 'DiscordThread', foreign_key: 'owner_id'
end

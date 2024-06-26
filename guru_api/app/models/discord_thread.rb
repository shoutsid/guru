class DiscordThread < ApplicationRecord
  include KafkaEventPublisher
  self.inheritance_column = :_type_disabled
  self.primary_key = 'discord_id'

  belongs_to :owner, class_name: 'DiscordUser', foreign_key: 'owner_id', primary_key: 'discord_id'
  belongs_to :parent_thread, class_name: 'DiscordThread', foreign_key: 'parent_id', primary_key: 'discord_id', optional: true
end

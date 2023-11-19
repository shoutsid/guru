class OpenAiThread < ApplicationRecord
  include KafkaEventPublisher
  self.primary_key = 'external_id'

  has_many :messages, class_name: 'OpenAiMessage', foreign_key: 'thread_id', primary_key: 'external_id'
  has_many :concept_origins, as: :conceptable, primary_key: 'external_id'
end

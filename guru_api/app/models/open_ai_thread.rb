class OpenAiThread < ApplicationRecord
  include KafkaEventPublisher
  has_many :messages, class_name: 'OpenAiMessage', foreign_key: 'thread_id', primary_key: 'external_id'
  has_many :concept_origins, as: :conceptable
end

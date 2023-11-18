class OpenAiMessage < ApplicationRecord
  belongs_to :assistant, class_name: 'OpenAiAssistant', foreign_key: 'assistant_id', primary_key: 'external_id'
  belongs_to :thread, class_name: 'OpenAiThread', foreign_key: 'thread_id', primary_key: 'external_id', optional: true
  has_many :concept_origins, as: :conceptable
end

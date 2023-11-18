class OpenAiAssistant < ApplicationRecord
  has_many :messages, class_name: 'OpenAiMessage', foreign_key: 'assistant_id', primary_key: 'external_id'
end

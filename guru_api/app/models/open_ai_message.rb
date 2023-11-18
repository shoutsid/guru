class OpenAiMessage < ApplicationRecord
  belongs_to :assistant, class_name: 'OpenAiAssistant', foreign_key: 'assistant_id'
  belongs_to :thread, class_name: 'OpenAiThread', foreign_key: 'thread_id', optional: true
end

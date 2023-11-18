class OpenAiThread < ApplicationRecord
  has_many :messages, class_name: 'OpenAiMessage', foreign_key: 'thread_id', primary_key: 'external_id'
end

class OpenAiThread < ApplicationRecord
    has_many :messages, foreign_key: :thread_id, class_name: 'OpenAiMessage', dependent: :destroy, inverse_of: :thread

    # validates :openai_id, uniqueness: true
    # serialize :metadata, type: Hash
    # {
    #   "id": "thread_abc123",
    #   "object": "thread",
    #   "created_at": 1698107661,
    #   "metadata": {}
    # }
    def convert_to_openai_object
        {
            "id": self.openai_id,
            "object": "thread",
            "created_at": self.openai_created_at,
            "metadata": self.metadata
        }
    end
end

class OpenAiThread < ApplicationRecord
    validates :openai_id, presence: true, uniqueness: true

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

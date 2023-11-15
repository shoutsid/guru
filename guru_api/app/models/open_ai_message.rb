class OpenAiMessage < ApplicationRecord
    validates :openai_id, presence: true, uniqueness: true
    # serialize :file_ids, type: Array
    # serialize :metadata, type: Hash
    # serialize :content, type: Hash
    # {
    #   "id": "msg_abc123",
    #   "object": "thread.message",
    #   "created_at": 1698983503,
    #   "thread_id": "thread_abc123",
    #   "role": "assistant",
    #   "content": [
    #     {
    #       "type": "text",
    #       "text": {
    #         "value": "Hi! How can I help you today?",
    #         "annotations": []
    #       }
    #     }
    #   ],
    #   "file_ids": [],
    #   "assistant_id": "asst_abc123",
    #   "run_id": "run_abc123",
    #   "metadata": {}
    # }
    def convert_to_openai_object
        {
            "id": self.openai_id,
            "object": "thread.message",
            "created_at": self.openai_created_at,
            "thread_id": self.openai_thread_id,
            "role": self.role,
            "content": self.content,
            "file_ids": self.file_ids,
            "assistant_id": self.openai_assistant_id,
            "run_id": self.openai_run_id,
            "metadata": self.metadata
        }
    end
end

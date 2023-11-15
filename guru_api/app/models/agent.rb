class Agent < ApplicationRecord
    # serialize :skills, type: Array
    # serialize :file_ids, type: Array
    # serialize :metadata, type: Hash
    # {
    #   "id": "asst_abc123",
    #   "object": "assistant",
    #   "created_at": 1698984975,
    #   "name": "Math Tutor",
    #   "description": null,
    #   "model": "gpt-4",
    #   "instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
    #   "tools": [
    #     {
    #       "type": "code_interpreter"
    #     }
    #   ],
    #   "file_ids": [],
    #   "metadata": {}
    # }
    def convert_to_openai_object
        {
            "id": self.openai_id,
            "object": "assistant",
            "created_at": self.openai_created_at,
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "instructions": self.system_message,
            "tools": self.tools,
            "file_ids": self.file_ids,
            "metadata": self.metadata
        }
    end
end

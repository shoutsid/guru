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

  # (Abstract method) Send a message to another agent.
  def send(message, recipient, request_reply = nil)
  end

  # (Abstract async method) Send a message to another agent.
  def a_send(message, recipient, request_reply = nil)
  end

  # (Abstract method) Receive a message from another agent.
  def receive(message, sender, request_reply = nil)
  end

  # (Abstract async method) Receive a message from another agent.
  def a_receive(message, sender, request_reply = nil)
  end

  # (Abstract method) Reset the agent.
  def reset
  end

  # (Abstract method) Generate a reply based on the received messages.
  def generate_reply(messages = nil, sender = nil, **kwargs)
  end

  # (Abstract async method) Generate a reply based on the received messages.
  def a_generate_reply(messages = nil, sender = nil, **kwargs)
  end
end

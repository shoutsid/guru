# frozen_string_literal: true

class OpenAiAssistantConsumer < ApplicationConsumer
  def consume
    OpenAiAssistant.insert_all messages.payloads
  end

  # Run anything upon partition being revoked
  # def revoked
  # end

  # Define here any teardown things you want when Karafka server stops
  # def shutdown
  # end
end

class ChatController < ApplicationController
  before_action :set_open_ai_thread, only: %i[ completion ]
  # POST /chat/completion?thread_id=1&id=1
  def completion
    # POST request to localhost:8000/chat/completion?thread_id=1&id=1
    # with body: { "message": "Hello, I'm a human", "role": "user" }
    response = HTTParty.post('http://localhost:8000/ai/response?' + 'thread_id=' + @open_ai_thread.id.to_s,
                        body: request.raw_post,
                        headers: { 'Content-Type' => 'application/json' })
    return render json: response.body
  end

  private
  def set_open_ai_thread
    @open_ai_thread = OpenAiThread.find(params[:thread_id])
  end
end
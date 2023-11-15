class MessagesController < ApplicationController
  before_action :set_open_ai_thread, only: %i[ index show create edit update destroy ]
  before_action :set_open_ai_message, only: %i[ show edit update destroy ]

  def index
    @open_ai_messages = OpenAiMessage.where(open_ai_thread_id: params[:thread_id])
  end

  def show
  end

  def new
    @open_ai_message = OpenAiMessage.new
  end

  def edit
  end

  def create
    @open_ai_message = OpenAiMessage.new(open_ai_message_params)

    respond_to do |format|
      if @open_ai_message.save
        format.json { render :show, status: :created, location: thread_message_url(@open_ai_message, thread_id: @open_ai_thread.id) }
      else
        format.json { render json: @open_ai_message.errors, status: :unprocessable_entity }
      end
    end
  end

  def update
    respond_to do |format|
      if @open_ai_message.update(open_ai_message_params)
        format.json { render :show, status: :ok, location: thread_message_url(@open_ai_message, thread_id: @open_ai_thread.id) }
      else
        format.json { render json: @open_ai_message.errors, status: :unprocessable_entity }
      end
    end
  end

  def destroy
    @open_ai_message.destroy!

    respond_to do |format|
      format.json { head :no_content }
    end
  end

  private
  def set_open_ai_thread
    @open_ai_thread = OpenAiThread.find(params[:thread_id])
  end

  def set_open_ai_message
    @open_ai_message = OpenAiMessage.find_by(id: params[:id], open_ai_thread_id: params[:thread_id])
  end

  def open_ai_message_params
    params.require(:message).permit(:openai_id, :object, :openai_created_at, :openai_thread_id, :role, :content, :file_ids, :openai_assitant_id, :metadata, :run_id)
  end
end

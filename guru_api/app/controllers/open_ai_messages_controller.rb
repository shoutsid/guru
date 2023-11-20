class OpenAiMessagesController < ApplicationController
  before_action :set_open_ai_message, only: %i[ show edit update destroy ]

  def index
    @open_ai_messages = OpenAiMessage.all
    if params[:thread_id]
      @open_ai_messages = @open_ai_messages.where(thread_id: params[:thread_id])
    end
    if params[:assistant_id]
      @open_ai_messages = @open_ai_messages.where(assistant_id: params[:assistant_id])
    end
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
        format.html { redirect_to open_ai_message_url(@open_ai_message), notice: "Open ai message was successfully created." }
        format.json { render :show, status: :created, location: @open_ai_message }
      else
        format.html { render :new, status: :unprocessable_entity }
        format.json { render json: @open_ai_message.errors, status: :unprocessable_entity }
      end
    end
  end

  def update
    respond_to do |format|
      if @open_ai_message.update(open_ai_message_params)
        format.html { redirect_to open_ai_message_url(@open_ai_message), notice: "Open ai message was successfully updated." }
        format.json { render :show, status: :ok, location: @open_ai_message }
      else
        format.html { render :edit, status: :unprocessable_entity }
        format.json { render json: @open_ai_message.errors, status: :unprocessable_entity }
      end
    end
  end

  def destroy
    @open_ai_message.destroy!

    respond_to do |format|
      format.html { redirect_to open_ai_messages_url, notice: "Open ai message was successfully destroyed." }
      format.json { head :no_content }
    end
  end

  private

  def set_open_ai_message
    @open_ai_message = OpenAiMessage.find(params[:id])
  end

  def open_ai_message_params
    params.require(:open_ai_message).permit(:external_id, :thread_id, :role, :content, :file_ids, :assistant_id, :run_id, :metadata)
  end
end

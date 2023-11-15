class OpenAiMessagesController < ApplicationController
  before_action :set_open_ai_message, only: %i[ show edit update destroy ]

  # GET /open_ai_messages or /open_ai_messages.json
  def index
    @open_ai_messages = OpenAiMessage.all
  end

  # GET /open_ai_messages/1 or /open_ai_messages/1.json
  def show
  end

  # GET /open_ai_messages/new
  def new
    @open_ai_message = OpenAiMessage.new
  end

  # GET /open_ai_messages/1/edit
  def edit
  end

  # POST /open_ai_messages or /open_ai_messages.json
  def create
    @open_ai_message = OpenAiMessage.new(open_ai_message_params)

    respond_to do |format|
      if @open_ai_message.save
        # format.html { redirect_to open_ai_message_url(@open_ai_message), notice: "Open ai message was successfully created." }
        format.json { render :show, status: :created, location: @open_ai_message }
      else
        # format.html { render :new, status: :unprocessable_entity }
        format.json { render json: @open_ai_message.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /open_ai_messages/1 or /open_ai_messages/1.json
  def update
    respond_to do |format|
      if @open_ai_message.update(open_ai_message_params)
        # format.html { redirect_to open_ai_message_url(@open_ai_message), notice: "Open ai message was successfully updated." }
        format.json { render :show, status: :ok, location: @open_ai_message }
      else
        # format.html { render :edit, status: :unprocessable_entity }
        format.json { render json: @open_ai_message.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /open_ai_messages/1 or /open_ai_messages/1.json
  def destroy
    @open_ai_message.destroy!

    respond_to do |format|
      # format.html { redirect_to open_ai_messages_url, notice: "Open ai message was successfully destroyed." }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_open_ai_message
      @open_ai_message = OpenAiMessage.find(params[:id])
    end

    # Only allow a list of trusted parameters through.
    def open_ai_message_params
      params.require(:open_ai_message).permit(:openai_id, :object, :openai_created_at, :openai_thread_id, :role, :content, :file_ids, :openai_assitant_id, :metadata, :run_id)
    end
end

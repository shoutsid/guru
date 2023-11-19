class OpenAiAssistantsController < ApplicationController
  before_action :set_open_ai_assistant, only: %i[ show update destroy ]

  def index
    @open_ai_assistants = OpenAiAssistant.all
  end

  def show
  end

  def create
    @open_ai_assistant = OpenAiAssistant.new(open_ai_assistant_params)

    if @open_ai_assistant.save
      render :show, status: :created, location: @open_ai_assistant
    else
      render json: @open_ai_assistant.errors, status: :unprocessable_entity
    end
  end

  def update
    if @open_ai_assistant.update(open_ai_assistant_params)
      render :show, status: :ok, location: @open_ai_assistant
    else
      render json: @open_ai_assistant.errors, status: :unprocessable_entity
    end
  end

  def destroy
    @open_ai_assistant.destroy!
  end

  private
  def set_open_ai_assistant
    @open_ai_assistant = OpenAiAssistant.find(params[:id])
  end

  def open_ai_assistant_params
    params.require(:open_ai_assistant).permit(:external_id, :name, :description, :model, :instructions, :tools, :file_ids, :metadata)
  end
end

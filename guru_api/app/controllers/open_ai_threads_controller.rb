class OpenAiThreadsController < ApplicationController
  before_action :set_open_ai_thread, only: %i[ show update destroy ]

  def index
    @open_ai_threads = OpenAiThread.all
  end

  def show
  end

  def create
    @open_ai_thread = OpenAiThread.new(open_ai_thread_params)

    if @open_ai_thread.save
      render :show, status: :created, location: @open_ai_thread
    else
      render json: @open_ai_thread.errors, status: :unprocessable_entity
    end
  end

  def update
    if @open_ai_thread.update(open_ai_thread_params)
      render :show, status: :ok, location: @open_ai_thread
    else
      render json: @open_ai_thread.errors, status: :unprocessable_entity
    end
  end

  def destroy
    @open_ai_thread.destroy!
  end

  private
  def set_open_ai_thread
    @open_ai_thread = OpenAiThread.find_by!(external_id: params[:id])
  end

  def open_ai_thread_params
    params.require(:open_ai_thread).permit(:external_id, :metadata)
  end
end

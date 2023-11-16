class ThreadsController < ApplicationController
  before_action :set_open_ai_thread, only: %i[ show edit update destroy ]

  def index
    @open_ai_threads = OpenAiThread.all
  end

  def show
  end

  def new
    @open_ai_thread = OpenAiThread.new
  end

  def edit
  end

  def create
    @open_ai_thread = OpenAiThread.new(open_ai_thread_params)
    respond_to do |format|
      if @open_ai_thread.save
        format.json { render :show, status: :created, location: thread_url(@open_ai_thread) }
      else
        format.json { render json: @open_ai_thread.errors, status: :unprocessable_entity }
      end
    end
  end

  def update
    respond_to do |format|
      if @open_ai_thread.update(open_ai_thread_params)
        format.json { render :show, status: :ok, location: thread_url(@open_ai_thread) }
      else
        format.json { render json: @open_ai_thread.errors, status: :unprocessable_entity }
      end
    end
  end

  def destroy
    @open_ai_thread.destroy!

    respond_to do |format|
      format.json { head :no_content }
    end
  end

  private
  def set_open_ai_thread
    @open_ai_thread = OpenAiThread.find(params[:id])
  end

  def open_ai_thread_params
    params.fetch(:thread, {}).permit(:openai_id, :object, :openai_created_at, :meta_data)
  end
end
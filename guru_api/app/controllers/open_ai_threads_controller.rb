class OpenAiThreadsController < ApplicationController
  before_action :set_open_ai_thread, only: %i[ show edit update destroy ]

  # GET /open_ai_threads or /open_ai_threads.json
  def index
    @open_ai_threads = OpenAiThread.all
  end

  # GET /open_ai_threads/1 or /open_ai_threads/1.json
  def show
  end

  # GET /open_ai_threads/new
  def new
    @open_ai_thread = OpenAiThread.new
  end

  # GET /open_ai_threads/1/edit
  def edit
  end

  # POST /open_ai_threads or /open_ai_threads.json
  def create
    @open_ai_thread = OpenAiThread.new(open_ai_thread_params)

    respond_to do |format|
      if @open_ai_thread.save
        # format.html { redirect_to open_ai_thread_url(@open_ai_thread), notice: "Open ai thread was successfully created." }
        format.json { render :show, status: :created, location: @open_ai_thread }
      else
        # format.html { render :new, status: :unprocessable_entity }
        format.json { render json: @open_ai_thread.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /open_ai_threads/1 or /open_ai_threads/1.json
  def update
    respond_to do |format|
      if @open_ai_thread.update(open_ai_thread_params)
        # format.html { redirect_to open_ai_thread_url(@open_ai_thread), notice: "Open ai thread was successfully updated." }
        format.json { render :show, status: :ok, location: @open_ai_thread }
      else
        # format.html { render :edit, status: :unprocessable_entity }
        format.json { render json: @open_ai_thread.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /open_ai_threads/1 or /open_ai_threads/1.json
  def destroy
    @open_ai_thread.destroy!

    respond_to do |format|
      # format.html { redirect_to open_ai_threads_url, notice: "Open ai thread was successfully destroyed." }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_open_ai_thread
      @open_ai_thread = OpenAiThread.find(params[:id])
    end

    # Only allow a list of trusted parameters through.
    def open_ai_thread_params
      params.require(:open_ai_thread).permit(:openai_id, :object, :openai_created_at, :meta_data)
    end
end

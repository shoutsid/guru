class DiscordThreadsController < ApplicationController
  before_action :set_discord_thread, only: %i[ show update destroy ]

  def index
    @discord_threads = DiscordThread.all
  end

  def show
  end

  def create
    @discord_thread = DiscordThread.new(discord_thread_params)

    if @discord_thread.save
      render :show, status: :created, location: @discord_thread
    else
      render json: @discord_thread.errors, status: :unprocessable_entity
    end
  end

  def update
    if @discord_thread.update(discord_thread_params)
      render :show, status: :ok, location: @discord_thread
    else
      render json: @discord_thread.errors, status: :unprocessable_entity
    end
  end

  def destroy
    @discord_thread.destroy!
  end

  private
  def set_discord_thread
    @discord_thread = DiscordThread.find(params[:id])
  end

  def discord_thread_params
    params.require(:discord_thread).permit(:discord_id, :name, :type, :owner_id, :parent_id, :archived, :auto_archive_duration)
  end
end

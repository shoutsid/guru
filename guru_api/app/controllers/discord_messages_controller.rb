class DiscordMessagesController < ApplicationController
  before_action :set_discord_message, only: %i[ show update destroy ]

  def index
    @discord_messages = DiscordMessage.all
  end

  def show
  end

  def create
    @discord_message = DiscordMessage.new(discord_message_params)

    if @discord_message.save
      render :show, status: :created, location: @discord_message
    else
      render json: @discord_message.errors, status: :unprocessable_entity
    end
  end

  def update
    if @discord_message.update(discord_message_params)
      render :show, status: :ok, location: @discord_message
    else
      render json: @discord_message.errors, status: :unprocessable_entity
    end
  end

  def destroy
    @discord_message.destroy!
  end

  private

  def set_discord_message
    @discord_message = DiscordMessage.find(params[:id])
  end

  def discord_message_params
    params.require(:discord_message).permit(:id, :discord_id, :content, :author_id, :channel_id, :guild_id)
  end
end

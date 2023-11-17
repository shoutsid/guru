class DiscordChannelsController < ApplicationController
  before_action :set_discord_channel, only: %i[ show update destroy ]

  def index
    @discord_channels = DiscordChannel.all
  end

  def show
  end

  def create
    @discord_channel = DiscordChannel.new(discord_channel_params)

    if @discord_channel.save
      render :show, status: :created, location: @discord_channel
    else
      render json: @iscord_channel.errors, status: :unprocessable_entity
    end
  end

  def update
    if @discord_channel.update(discord_channel_params)
      render :show, status: :ok, location: @discord_channel
    else
      render json: @discord_channel.errors, status: :unprocessable_entity
    end
  end

  def destroy
    @discord_channel.destroy!
  end

  private
  def set_discord_channel
    @discord_channel = DiscordChannel.find_by!(discord_id: params[:id])
  end

  def discord_channel_params
    params.require(:discord_channel).permit(:discord_id, :name, :type, :position, :topic, :guild_id)
  end
end

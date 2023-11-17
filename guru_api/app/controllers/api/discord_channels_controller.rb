class Api::DiscordChannelsController < ApplicationController
  before_action :set_api_discord_channel, only: %i[ show update destroy ]

  # GET /api/discord_channels
  # GET /api/discord_channels.json
  def index
    @api_discord_channels = Api::DiscordChannel.all
  end

  # GET /api/discord_channels/1
  # GET /api/discord_channels/1.json
  def show
  end

  # POST /api/discord_channels
  # POST /api/discord_channels.json
  def create
    @api_discord_channel = Api::DiscordChannel.new(api_discord_channel_params)

    if @api_discord_channel.save
      render :show, status: :created, location: @api_discord_channel
    else
      render json: @api_discord_channel.errors, status: :unprocessable_entity
    end
  end

  # PATCH/PUT /api/discord_channels/1
  # PATCH/PUT /api/discord_channels/1.json
  def update
    if @api_discord_channel.update(api_discord_channel_params)
      render :show, status: :ok, location: @api_discord_channel
    else
      render json: @api_discord_channel.errors, status: :unprocessable_entity
    end
  end

  # DELETE /api/discord_channels/1
  # DELETE /api/discord_channels/1.json
  def destroy
    @api_discord_channel.destroy!
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_api_discord_channel
      @api_discord_channel = Api::DiscordChannel.find(params[:id])
    end

    # Only allow a list of trusted parameters through.
    def api_discord_channel_params
      params.require(:api_discord_channel).permit(:discord_id, :name, :type, :position, :topic, :guild_id)
    end
end

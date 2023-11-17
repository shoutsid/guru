class DiscordGuildsController < ApplicationController
  before_action :set_discord_guild, only: %i[ show update destroy ]

  # GET /discord_guilds
  # GET /discord_guilds.json
  def index
    @discord_guilds = DiscordGuild.all
  end

  # GET /discord_guilds/1
  # GET /discord_guilds/1.json
  def show
  end

  # POST /discord_guilds
  # POST /discord_guilds.json
  def create
    @discord_guild = DiscordGuild.new(discord_guild_params)

    if @discord_guild.save
      render :show, status: :created, location: @discord_guild
    else
      render json: @discord_guild.errors, status: :unprocessable_entity
    end
  end

  # PATCH/PUT /discord_guilds/1
  # PATCH/PUT /discord_guilds/1.json
  def update
    if @discord_guild.update(discord_guild_params)
      render :show, status: :ok, location: @discord_guild
    else
      render json: @discord_guild.errors, status: :unprocessable_entity
    end
  end

  # DELETE /discord_guilds/1
  # DELETE /discord_guilds/1.json
  def destroy
    @discord_guild.destroy!
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_discord_guild
      @discord_guild = DiscordGuild.find(params[:id])
    end

    # Only allow a list of trusted parameters through.
    def discord_guild_params
      params.require(:discord_guild).permit(:discord_id, :name, :member_count)
    end
end

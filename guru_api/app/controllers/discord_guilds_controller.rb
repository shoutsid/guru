class DiscordGuildsController < ApplicationController
  before_action :set_discord_guild, only: %i[ show update destroy ]

  def index
    @discord_guilds = DiscordGuild.all
  end

  def show
  end

  def create
    @discord_guild = DiscordGuild.new(discord_guild_params)

    if @discord_guild.save
      render :show, status: :created, location: @discord_guild
    else
      render json: @discord_guild.errors, status: :unprocessable_entity
    end
  end

  def update
    if @discord_guild.update(discord_guild_params)
      render :show, status: :ok, location: @discord_guild
    else
      render json: @discord_guild.errors, status: :unprocessable_entity
    end
  end

  def destroy
    @discord_guild.destroy!
  end

  private

  def set_discord_guild
    @discord_guild = DiscordGuild.find(params[:id])
  end

  def discord_guild_params
    params.require(:discord_guild).permit(:id, :discord_id, :name, :member_count)
  end
end

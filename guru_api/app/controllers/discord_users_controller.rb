class DiscordUsersController < ApplicationController
  before_action :set_discord_user, only: %i[ show update destroy ]

  def index
    @discord_users = DiscordUser.all
  end

  def show
  end

  def create
    @discord_user = DiscordUser.new(discord_user_params)

    if @discord_user.save
      render :show, status: :created, location: @discord_user
    else
      render json: @discord_user.errors, status: :unprocessable_entity
    end
  end

  def update
    if @discord_user.update(discord_user_params)
      render :show, status: :ok, location: @discord_user
    else
      render json: @discord_user.errors, status: :unprocessable_entity
    end
  end

  def destroy
    @discord_user.destroy!
  end

  private
  def set_discord_user
    @discord_user = DiscordUser.find(params[:id])
  end

  def discord_user_params
    params.require(:discord_user).permit(:discord_id, :name, :discriminator, :avatar, :bot, :system)
  end
end

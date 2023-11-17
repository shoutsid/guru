require "test_helper"

class DiscordUsersControllerTest < ActionDispatch::IntegrationTest
  setup do
    @discord_user = discord_users(:one)
  end

  test "should get index" do
    get discord_users_url, as: :json
    assert_response :success
  end

  test "should create discord_user" do
    assert_difference("DiscordUser.count") do
      post discord_users_url, params: { discord_user: { avatar: @discord_user.avatar, bot: @discord_user.bot, discord_id: @discord_user.discord_id, discriminator: @discord_user.discriminator, name: @discord_user.name, system: @discord_user.system } }, as: :json
    end

    assert_response :created
  end

  test "should show discord_user" do
    get discord_user_url(@discord_user), as: :json
    assert_response :success
  end

  test "should update discord_user" do
    patch discord_user_url(@discord_user), params: { discord_user: { avatar: @discord_user.avatar, bot: @discord_user.bot, discord_id: @discord_user.discord_id, discriminator: @discord_user.discriminator, name: @discord_user.name, system: @discord_user.system } }, as: :json
    assert_response :success
  end

  test "should destroy discord_user" do
    assert_difference("DiscordUser.count", -1) do
      delete discord_user_url(@discord_user), as: :json
    end

    assert_response :no_content
  end
end

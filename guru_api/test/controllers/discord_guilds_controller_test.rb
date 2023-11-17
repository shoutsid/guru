require "test_helper"

class DiscordGuildsControllerTest < ActionDispatch::IntegrationTest
  setup do
    @discord_guild = discord_guilds(:one)
  end

  test "should get index" do
    get discord_guilds_url, as: :json
    assert_response :success
  end

  test "should create discord_guild" do
    assert_difference("DiscordGuild.count") do
      post discord_guilds_url, params: { discord_guild: { discord_id: @discord_guild.discord_id, member_count: @discord_guild.member_count, name: @discord_guild.name } }, as: :json
    end

    assert_response :created
  end

  test "should show discord_guild" do
    get discord_guild_url(@discord_guild), as: :json
    assert_response :success
  end

  test "should update discord_guild" do
    patch discord_guild_url(@discord_guild), params: { discord_guild: { discord_id: @discord_guild.discord_id, member_count: @discord_guild.member_count, name: @discord_guild.name } }, as: :json
    assert_response :success
  end

  test "should destroy discord_guild" do
    assert_difference("DiscordGuild.count", -1) do
      delete discord_guild_url(@discord_guild), as: :json
    end

    assert_response :no_content
  end
end

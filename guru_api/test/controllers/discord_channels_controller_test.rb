require "test_helper"

class DiscordChannelsControllerTest < ActionDispatch::IntegrationTest
  setup do
    @api_discord_channel = api_discord_channels(:one)
  end

  test "should get index" do
    get api_discord_channels_url, as: :json
    assert_response :success
  end

  test "should create api_discord_channel" do
    assert_difference("DiscordChannel.count") do
      post api_discord_channels_url, params: { api_discord_channel: { discord_id: @api_discord_channel.discord_id, guild_id: @api_discord_channel.guild_id, name: @api_discord_channel.name, position: @api_discord_channel.position, topic: @api_discord_channel.topic, type: @api_discord_channel.type } }, as: :json
    end

    assert_response :created
  end

  test "should show api_discord_channel" do
    get api_discord_channel_url(@api_discord_channel), as: :json
    assert_response :success
  end

  test "should update api_discord_channel" do
    patch api_discord_channel_url(@api_discord_channel), params: { api_discord_channel: { discord_id: @api_discord_channel.discord_id, guild_id: @api_discord_channel.guild_id, name: @api_discord_channel.name, position: @api_discord_channel.position, topic: @api_discord_channel.topic, type: @api_discord_channel.type } }, as: :json
    assert_response :success
  end

  test "should destroy api_discord_channel" do
    assert_difference("DiscordChannel.count", -1) do
      delete api_discord_channel_url(@api_discord_channel), as: :json
    end

    assert_response :no_content
  end
end

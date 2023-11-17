require "test_helper"

class DiscordMessagesControllerTest < ActionDispatch::IntegrationTest
  setup do
    @discord_message = discord_messages(:one)
  end

  test "should get index" do
    get discord_messages_url, as: :json
    assert_response :success
  end

  test "should create discord_message" do
    assert_difference("DiscordMessage.count") do
      post discord_messages_url, params: { discord_message: { author_id: @discord_message.author_id, channel_id: @discord_message.channel_id, content: @discord_message.content, discord_id: @discord_message.discord_id, guild_id: @discord_message.guild_id } }, as: :json
    end

    assert_response :created
  end

  test "should show discord_message" do
    get discord_message_url(@discord_message), as: :json
    assert_response :success
  end

  test "should update discord_message" do
    patch discord_message_url(@discord_message), params: { discord_message: { author_id: @discord_message.author_id, channel_id: @discord_message.channel_id, content: @discord_message.content, discord_id: @discord_message.discord_id, guild_id: @discord_message.guild_id } }, as: :json
    assert_response :success
  end

  test "should destroy discord_message" do
    assert_difference("DiscordMessage.count", -1) do
      delete discord_message_url(@discord_message), as: :json
    end

    assert_response :no_content
  end
end

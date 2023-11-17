require "test_helper"

class DiscordThreadsControllerTest < ActionDispatch::IntegrationTest
  setup do
    @discord_thread = discord_threads(:one)
  end

  test "should get index" do
    get discord_threads_url, as: :json
    assert_response :success
  end

  test "should create discord_thread" do
    assert_difference("DiscordThread.count") do
      post discord_threads_url, params: { discord_thread: { archived: @discord_thread.archived, auto_archive_duration: @discord_thread.auto_archive_duration, discord_id: @discord_thread.discord_id, name: @discord_thread.name, owner_id: @discord_thread.owner_id, parent_id: @discord_thread.parent_id, type: @discord_thread.type } }, as: :json
    end

    assert_response :created
  end

  test "should show discord_thread" do
    get discord_thread_url(@discord_thread), as: :json
    assert_response :success
  end

  test "should update discord_thread" do
    patch discord_thread_url(@discord_thread), params: { discord_thread: { archived: @discord_thread.archived, auto_archive_duration: @discord_thread.auto_archive_duration, discord_id: @discord_thread.discord_id, name: @discord_thread.name, owner_id: @discord_thread.owner_id, parent_id: @discord_thread.parent_id, type: @discord_thread.type } }, as: :json
    assert_response :success
  end

  test "should destroy discord_thread" do
    assert_difference("DiscordThread.count", -1) do
      delete discord_thread_url(@discord_thread), as: :json
    end

    assert_response :no_content
  end
end

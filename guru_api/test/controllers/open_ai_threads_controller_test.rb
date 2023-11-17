require "test_helper"

class OpenAiThreadsControllerTest < ActionDispatch::IntegrationTest
  setup do
    @open_ai_thread = open_ai_threads(:one)
  end

  test "should get index" do
    get open_ai_threads_url, as: :json
    assert_response :success
  end

  test "should create open_ai_thread" do
    assert_difference("OpenAiThread.count") do
      post open_ai_threads_url, params: { open_ai_thread: { external_id: @open_ai_thread.external_id, metadata: @open_ai_thread.metadata } }, as: :json
    end

    assert_response :created
  end

  test "should show open_ai_thread" do
    get open_ai_thread_url(@open_ai_thread), as: :json
    assert_response :success
  end

  test "should update open_ai_thread" do
    patch open_ai_thread_url(@open_ai_thread), params: { open_ai_thread: { external_id: @open_ai_thread.external_id, metadata: @open_ai_thread.metadata } }, as: :json
    assert_response :success
  end

  test "should destroy open_ai_thread" do
    assert_difference("OpenAiThread.count", -1) do
      delete open_ai_thread_url(@open_ai_thread), as: :json
    end

    assert_response :no_content
  end
end

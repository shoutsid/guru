require "test_helper"

class OpenAiThreadsControllerTest < ActionDispatch::IntegrationTest
  setup do
    @open_ai_thread = open_ai_threads(:one)
  end

  test "should get index" do
    get open_ai_threads_url
    assert_response :success
  end

  test "should get new" do
    get new_open_ai_thread_url
    assert_response :success
  end

  test "should create open_ai_thread" do
    assert_difference("OpenAiThread.count") do
      post open_ai_threads_url, params: { open_ai_thread: { meta_data: @open_ai_thread.meta_data, object: @open_ai_thread.object, openai_created_at: @open_ai_thread.openai_created_at, openai_id: @open_ai_thread.openai_id } }
    end

    assert_redirected_to open_ai_thread_url(OpenAiThread.last)
  end

  test "should show open_ai_thread" do
    get open_ai_thread_url(@open_ai_thread)
    assert_response :success
  end

  test "should get edit" do
    get edit_open_ai_thread_url(@open_ai_thread)
    assert_response :success
  end

  test "should update open_ai_thread" do
    patch open_ai_thread_url(@open_ai_thread), params: { open_ai_thread: { meta_data: @open_ai_thread.meta_data, object: @open_ai_thread.object, openai_created_at: @open_ai_thread.openai_created_at, openai_id: @open_ai_thread.openai_id } }
    assert_redirected_to open_ai_thread_url(@open_ai_thread)
  end

  test "should destroy open_ai_thread" do
    assert_difference("OpenAiThread.count", -1) do
      delete open_ai_thread_url(@open_ai_thread)
    end

    assert_redirected_to open_ai_threads_url
  end
end

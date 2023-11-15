require "test_helper"

class OpenAiMessagesControllerTest < ActionDispatch::IntegrationTest
  setup do
    @open_ai_message = open_ai_messages(:one)
  end

  test "should get index" do
    get open_ai_messages_url
    assert_response :success
  end

  test "should get new" do
    get new_open_ai_message_url
    assert_response :success
  end

  test "should create open_ai_message" do
    assert_difference("OpenAiMessage.count") do
      post open_ai_messages_url, params: { open_ai_message: { content: @open_ai_message.content, file_ids: @open_ai_message.file_ids, metadata: @open_ai_message.metadata, object: @open_ai_message.object, openai_assitant_id: @open_ai_message.openai_assitant_id, openai_created_at: @open_ai_message.openai_created_at, openai_id: @open_ai_message.openai_id, openai_thread_id: @open_ai_message.openai_thread_id, role: @open_ai_message.role, run_id: @open_ai_message.run_id } }
    end

    assert_redirected_to open_ai_message_url(OpenAiMessage.last)
  end

  test "should show open_ai_message" do
    get open_ai_message_url(@open_ai_message)
    assert_response :success
  end

  test "should get edit" do
    get edit_open_ai_message_url(@open_ai_message)
    assert_response :success
  end

  test "should update open_ai_message" do
    patch open_ai_message_url(@open_ai_message), params: { open_ai_message: { content: @open_ai_message.content, file_ids: @open_ai_message.file_ids, metadata: @open_ai_message.metadata, object: @open_ai_message.object, openai_assitant_id: @open_ai_message.openai_assitant_id, openai_created_at: @open_ai_message.openai_created_at, openai_id: @open_ai_message.openai_id, openai_thread_id: @open_ai_message.openai_thread_id, role: @open_ai_message.role, run_id: @open_ai_message.run_id } }
    assert_redirected_to open_ai_message_url(@open_ai_message)
  end

  test "should destroy open_ai_message" do
    assert_difference("OpenAiMessage.count", -1) do
      delete open_ai_message_url(@open_ai_message)
    end

    assert_redirected_to open_ai_messages_url
  end
end

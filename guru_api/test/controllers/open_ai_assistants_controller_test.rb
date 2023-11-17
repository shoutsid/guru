require "test_helper"

class OpenAiAssistantsControllerTest < ActionDispatch::IntegrationTest
  setup do
    @open_ai_assistant = open_ai_assistants(:one)
  end

  test "should get index" do
    get open_ai_assistants_url, as: :json
    assert_response :success
  end

  test "should create open_ai_assistant" do
    assert_difference("OpenAiAssistant.count") do
      post open_ai_assistants_url, params: { open_ai_assistant: { description: @open_ai_assistant.description, external_id: @open_ai_assistant.external_id, file_ids: @open_ai_assistant.file_ids, instructions: @open_ai_assistant.instructions, metadata: @open_ai_assistant.metadata, model: @open_ai_assistant.model, name: @open_ai_assistant.name, tools: @open_ai_assistant.tools } }, as: :json
    end

    assert_response :created
  end

  test "should show open_ai_assistant" do
    get open_ai_assistant_url(@open_ai_assistant), as: :json
    assert_response :success
  end

  test "should update open_ai_assistant" do
    patch open_ai_assistant_url(@open_ai_assistant), params: { open_ai_assistant: { description: @open_ai_assistant.description, external_id: @open_ai_assistant.external_id, file_ids: @open_ai_assistant.file_ids, instructions: @open_ai_assistant.instructions, metadata: @open_ai_assistant.metadata, model: @open_ai_assistant.model, name: @open_ai_assistant.name, tools: @open_ai_assistant.tools } }, as: :json
    assert_response :success
  end

  test "should destroy open_ai_assistant" do
    assert_difference("OpenAiAssistant.count", -1) do
      delete open_ai_assistant_url(@open_ai_assistant), as: :json
    end

    assert_response :no_content
  end
end

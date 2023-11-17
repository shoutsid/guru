require "application_system_test_case"

class OpenAiMessagesTest < ApplicationSystemTestCase
  setup do
    @open_ai_message = open_ai_messages(:one)
  end

  test "visiting the index" do
    visit open_ai_messages_url
    assert_selector "h1", text: "Open ai messages"
  end

  test "should create open ai message" do
    visit open_ai_messages_url
    click_on "New open ai message"

    fill_in "Assistant", with: @open_ai_message.assistant_id
    fill_in "Content", with: @open_ai_message.content
    fill_in "External", with: @open_ai_message.external_id
    fill_in "File ids", with: @open_ai_message.file_ids
    fill_in "Metadata", with: @open_ai_message.metadata
    fill_in "Role", with: @open_ai_message.role
    fill_in "Run", with: @open_ai_message.run_id
    fill_in "Thread", with: @open_ai_message.thread_id
    click_on "Create Open ai message"

    assert_text "Open ai message was successfully created"
    click_on "Back"
  end

  test "should update Open ai message" do
    visit open_ai_message_url(@open_ai_message)
    click_on "Edit this open ai message", match: :first

    fill_in "Assistant", with: @open_ai_message.assistant_id
    fill_in "Content", with: @open_ai_message.content
    fill_in "External", with: @open_ai_message.external_id
    fill_in "File ids", with: @open_ai_message.file_ids
    fill_in "Metadata", with: @open_ai_message.metadata
    fill_in "Role", with: @open_ai_message.role
    fill_in "Run", with: @open_ai_message.run_id
    fill_in "Thread", with: @open_ai_message.thread_id
    click_on "Update Open ai message"

    assert_text "Open ai message was successfully updated"
    click_on "Back"
  end

  test "should destroy Open ai message" do
    visit open_ai_message_url(@open_ai_message)
    click_on "Destroy this open ai message", match: :first

    assert_text "Open ai message was successfully destroyed"
  end
end

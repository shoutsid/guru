require "application_system_test_case"

class OpenAiThreadsTest < ApplicationSystemTestCase
  setup do
    @open_ai_thread = open_ai_threads(:one)
  end

  test "visiting the index" do
    visit open_ai_threads_url
    assert_selector "h1", text: "Open ai threads"
  end

  test "should create open ai thread" do
    visit open_ai_threads_url
    click_on "New open ai thread"

    fill_in "Meta data", with: @open_ai_thread.meta_data
    fill_in "Object", with: @open_ai_thread.object
    fill_in "Openai created at", with: @open_ai_thread.openai_created_at
    fill_in "Openai", with: @open_ai_thread.openai_id
    click_on "Create Open ai thread"

    assert_text "Open ai thread was successfully created"
    click_on "Back"
  end

  test "should update Open ai thread" do
    visit open_ai_thread_url(@open_ai_thread)
    click_on "Edit this open ai thread", match: :first

    fill_in "Meta data", with: @open_ai_thread.meta_data
    fill_in "Object", with: @open_ai_thread.object
    fill_in "Openai created at", with: @open_ai_thread.openai_created_at
    fill_in "Openai", with: @open_ai_thread.openai_id
    click_on "Update Open ai thread"

    assert_text "Open ai thread was successfully updated"
    click_on "Back"
  end

  test "should destroy Open ai thread" do
    visit open_ai_thread_url(@open_ai_thread)
    click_on "Destroy this open ai thread", match: :first

    assert_text "Open ai thread was successfully destroyed"
  end
end

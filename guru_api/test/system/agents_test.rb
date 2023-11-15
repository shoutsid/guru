require "application_system_test_case"

class AgentsTest < ApplicationSystemTestCase
  setup do
    @agent = agents(:one)
  end

  test "visiting the index" do
    visit agents_url
    assert_selector "h1", text: "Agents"
  end

  test "should create agent" do
    visit agents_url
    click_on "New agent"

    fill_in "Description", with: @agent.description
    fill_in "File ids", with: @agent.file_ids
    fill_in "Metadata", with: @agent.metadata
    fill_in "Model", with: @agent.model
    fill_in "Name", with: @agent.name
    fill_in "Openai created at", with: @agent.openai_created_at
    fill_in "Openai", with: @agent.openai_id
    fill_in "Openai object", with: @agent.openai_object
    fill_in "System message", with: @agent.system_message
    fill_in "Tools", with: @agent.tools
    click_on "Create Agent"

    assert_text "Agent was successfully created"
    click_on "Back"
  end

  test "should update Agent" do
    visit agent_url(@agent)
    click_on "Edit this agent", match: :first

    fill_in "Description", with: @agent.description
    fill_in "File ids", with: @agent.file_ids
    fill_in "Metadata", with: @agent.metadata
    fill_in "Model", with: @agent.model
    fill_in "Name", with: @agent.name
    fill_in "Openai created at", with: @agent.openai_created_at
    fill_in "Openai", with: @agent.openai_id
    fill_in "Openai object", with: @agent.openai_object
    fill_in "System message", with: @agent.system_message
    fill_in "Tools", with: @agent.tools
    click_on "Update Agent"

    assert_text "Agent was successfully updated"
    click_on "Back"
  end

  test "should destroy Agent" do
    visit agent_url(@agent)
    click_on "Destroy this agent", match: :first

    assert_text "Agent was successfully destroyed"
  end
end

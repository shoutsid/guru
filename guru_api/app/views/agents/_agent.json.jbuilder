json.extract! agent, :id, :name, :openai_id, :openai_object, :openai_created_at, :description, :model, :system_message, :tools, :file_ids, :metadata, :created_at, :updated_at
json.url agent_url(agent, format: :json)

json.extract! open_ai_assistant, :id, :external_id, :name, :description, :model, :instructions, :tools, :file_ids, :metadata, :created_at, :updated_at
json.url open_ai_assistant_url(open_ai_assistant, format: :json)

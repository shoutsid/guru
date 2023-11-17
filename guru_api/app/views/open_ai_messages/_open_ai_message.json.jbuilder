json.extract! open_ai_message, :id, :external_id, :thread_id, :role, :content, :file_ids, :assistant_id, :run_id, :metadata, :created_at, :updated_at
json.url open_ai_message_url(open_ai_message, format: :json)

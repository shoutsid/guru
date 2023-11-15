json.extract! open_ai_message, :id, :openai_id, :object, :openai_created_at, :openai_thread_id, :role, :content, :file_ids, :openai_assitant_id, :metadata, :run_id, :created_at, :updated_at
json.url open_ai_message_url(open_ai_message, format: :json)

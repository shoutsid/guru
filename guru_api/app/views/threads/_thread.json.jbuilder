json.extract! open_ai_thread, :id, :openai_id, :object, :openai_created_at, :meta_data, :created_at, :updated_at
json.url thread_url(open_ai_thread, format: :json)

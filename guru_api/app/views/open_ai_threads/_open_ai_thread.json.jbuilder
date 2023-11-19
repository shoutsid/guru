json.extract! open_ai_thread, :external_id, :metadata, :created_at, :updated_at
json.url open_ai_message_url(open_ai_message, format: :json)

json.concept_origins open_ai_thread.concept_origins do |concept_origin|
  json.partial! 'concept_origins/concept_origin', concept_origin: concept_origin
end
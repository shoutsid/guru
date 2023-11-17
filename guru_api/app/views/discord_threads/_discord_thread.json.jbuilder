json.extract! discord_thread, :id, :discord_id, :name, :type, :owner_id, :parent_id, :archived, :auto_archive_duration, :created_at, :updated_at
json.url discord_thread_url(discord_thread, format: :json)

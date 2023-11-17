json.extract! discord_message, :id, :discord_id, :content, :author_id, :channel_id, :guild_id, :created_at, :updated_at
json.url discord_message_url(discord_message, format: :json)

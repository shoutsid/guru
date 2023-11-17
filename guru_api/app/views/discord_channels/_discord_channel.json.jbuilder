json.extract! discord_channel, :id, :discord_id, :name, :type, :position, :topic, :guild_id, :created_at, :updated_at
json.url discord_channel_url(discord_channel, format: :json)

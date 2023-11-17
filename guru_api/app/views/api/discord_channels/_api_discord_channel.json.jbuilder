json.extract! api_discord_channel, :id, :discord_id, :name, :type, :position, :topic, :guild_id, :created_at, :updated_at
json.url api_discord_channel_url(api_discord_channel, format: :json)

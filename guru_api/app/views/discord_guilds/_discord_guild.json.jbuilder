json.extract! discord_guild, :discord_id, :name, :member_count, :created_at, :updated_at
json.url discord_guild_url(discord_guild, format: :json)

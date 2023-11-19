json.extract! discord_user, :discord_id, :name, :discriminator, :avatar, :bot, :system, :created_at, :updated_at
json.url discord_user_url(discord_user, format: :json)

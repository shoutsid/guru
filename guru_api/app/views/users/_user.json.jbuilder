json.extract! user, :id, :username, :discriminator, :avatar, :created_at, :updated_at
json.url user_url(user, format: :json)

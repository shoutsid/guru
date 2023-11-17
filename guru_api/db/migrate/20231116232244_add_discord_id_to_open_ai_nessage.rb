class AddDiscordIdToOpenAiNessage < ActiveRecord::Migration[7.1]
  def change
    add_column :open_ai_messages, :discord_id, :string
  end
end

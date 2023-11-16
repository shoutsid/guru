class AddDiscordChannelToOpenAiThreads < ActiveRecord::Migration[7.1]
  def change
    add_column :open_ai_threads, :discord_channel, :string
  end
end

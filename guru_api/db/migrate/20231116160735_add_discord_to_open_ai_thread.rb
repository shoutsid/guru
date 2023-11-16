class AddDiscordToOpenAiThread < ActiveRecord::Migration[7.1]
  def change
    add_column :open_ai_threads, :discord, :boolean, default: false
  end
end

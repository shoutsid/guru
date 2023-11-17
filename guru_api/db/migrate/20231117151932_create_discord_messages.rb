class CreateDiscordMessages < ActiveRecord::Migration[7.1]
  def change
    create_table :discord_messages do |t|
      t.bigint :discord_id
      t.text :content
      t.bigint :author_id
      t.bigint :channel_id
      t.bigint :guild_id

      t.timestamps
    end
    add_index :discord_messages, :discord_id
  end
end

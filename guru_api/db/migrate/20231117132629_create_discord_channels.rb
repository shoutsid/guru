class CreateDiscordChannels < ActiveRecord::Migration[7.1]
  def change
    create_table :discord_channels do |t|
      t.bigint :discord_id
      t.string :name
      t.string :type
      t.integer :position
      t.text :topic
      t.bigint :guild_id

      t.timestamps
    end
    add_index :discord_channels, :discord_id
    add_index :discord_channels, :guild_id
  end
end

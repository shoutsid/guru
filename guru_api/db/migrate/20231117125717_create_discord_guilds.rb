class CreateDiscordGuilds < ActiveRecord::Migration[7.1]
  def change
    create_table :discord_guilds do |t|
      t.bigint :discord_id
      t.string :name
      t.integer :member_count

      t.timestamps
    end
  end
end

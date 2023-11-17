class CreateDiscordUsers < ActiveRecord::Migration[7.1]
  def change
    create_table :discord_users do |t|
      t.bigint :discord_id
      t.string :name
      t.string :discriminator
      t.string :avatar
      t.boolean :bot
      t.boolean :system

      t.timestamps
    end
    add_index :discord_users, :discord_id
  end
end

class CreateDiscordThreads < ActiveRecord::Migration[7.1]
  def change
    create_table :discord_threads do |t|
      t.bigint :discord_id
      t.string :name
      t.string :type
      t.bigint :owner_id
      t.bigint :parent_id
      t.boolean :archived
      t.integer :auto_archive_duration

      t.timestamps
    end
    add_index :discord_threads, :discord_id
  end
end

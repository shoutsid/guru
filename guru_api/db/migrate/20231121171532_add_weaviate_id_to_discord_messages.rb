class AddWeaviateIdToDiscordMessages < ActiveRecord::Migration[7.1]
  def up
    enable_extension 'pgcrypto'
    add_column :discord_messages, :weaviate_id, :uuid, default: 'gen_random_uuid()', null: false
    add_index :discord_messages, :weaviate_id, unique: true
  end

  def down
    disable_extension 'pgcrypto'
    remove_column :discord_messages, :weaviate_id
    remove_index :discord_messages, :weaviate_id
  end
end

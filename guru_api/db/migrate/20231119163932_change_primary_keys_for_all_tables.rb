class ChangePrimaryKeysForAllTables < ActiveRecord::Migration[7.1]
  def up
    # Mapping of tables and their new primary keys
    new_primary_keys = {
      discord_guilds: :discord_id,
      discord_channels: :discord_id,
      discord_messages: :discord_id,
      discord_threads: :discord_id,
      discord_users: :discord_id,
      open_ai_assistants: :external_id,
      open_ai_messages: :external_id,
      open_ai_threads: :external_id
    }

    new_primary_keys.each do |table, pk_column|
      execute "ALTER TABLE #{table} DROP CONSTRAINT #{table}_pkey CASCADE;"
      remove_column table, :id
      execute "ALTER TABLE #{table} ADD PRIMARY KEY (#{pk_column});"
    end
  end

  def down
    raise ActiveRecord::IrreversibleMigration
    # Reverse the changes if needed
    # This section needs to be filled in based on your rollback strategy
  end
end
class CreateOpenAiMessages < ActiveRecord::Migration[7.1]
  def change
    create_table :open_ai_messages do |t|
      t.string :external_id
      t.string :thread_id
      t.string :role
      t.text :content
      t.text :file_ids
      t.string :assistant_id
      t.string :run_id
      t.jsonb :metadata

      t.timestamps
    end
    add_index :open_ai_messages, :external_id
  end
end

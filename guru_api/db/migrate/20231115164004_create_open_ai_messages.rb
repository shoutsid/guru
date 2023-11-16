class CreateOpenAiMessages < ActiveRecord::Migration[7.1]
  def change
    create_table :open_ai_messages do |t|
      t.string :openai_id
      t.string :object
      t.integer :openai_created_at
      t.integer :openai_updated_at
      t.string :openai_thread_id
      t.string :role
      t.text :content
      t.text :file_ids
      t.string :openai_assitant_id
      t.text :metadata
      t.string :run_id

      t.timestamps
    end
  end
end
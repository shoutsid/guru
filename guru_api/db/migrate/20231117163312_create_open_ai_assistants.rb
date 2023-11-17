class CreateOpenAiAssistants < ActiveRecord::Migration[7.1]
  def change
    create_table :open_ai_assistants do |t|
      t.string :external_id
      t.string :name
      t.text :description
      t.string :model
      t.text :instructions
      t.text :tools
      t.text :file_ids
      t.jsonb :metadata

      t.timestamps
    end
    add_index :open_ai_assistants, :external_id
  end
end

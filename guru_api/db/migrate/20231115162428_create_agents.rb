class CreateAgents < ActiveRecord::Migration[7.1]
  def change
    create_table :agents do |t|
      t.string :name
      t.string :openai_id
      t.string :openai_object
      t.integer :openai_created_at
      t.text :description
      t.string :model
      t.text :system_message
      t.text :tools, default: ""
      t.text :file_ids, default: ""
      t.text :metadata, default: ""

      t.timestamps
    end
  end
end

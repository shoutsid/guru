class CreateOpenAiThreads < ActiveRecord::Migration[7.1]
  def change
    create_table :open_ai_threads do |t|
      t.string :openai_id
      t.string :object
      t.integer :openai_created_at
      t.integer :openai_updated_at
      t.text :meta_data


      # discord links to remove and replace with modeling
      t.string :discord_channel
      t.boolean :discord, default: false

      t.timestamps
    end
  end
end

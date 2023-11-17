class CreateOpenAiThreads < ActiveRecord::Migration[7.1]
  def change
    create_table :open_ai_threads do |t|
      t.string :external_id
      t.jsonb :metadata

      t.timestamps
    end
    add_index :open_ai_threads, :external_id
  end
end

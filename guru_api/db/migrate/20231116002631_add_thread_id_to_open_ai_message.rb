class AddThreadIdToOpenAiMessage < ActiveRecord::Migration[7.1]
  def change
    add_column :open_ai_messages, :thread_id, :integer, null: false
    add_index :open_ai_messages, :thread_id
  end
end

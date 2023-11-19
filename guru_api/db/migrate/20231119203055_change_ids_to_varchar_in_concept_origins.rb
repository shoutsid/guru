class ChangeIdsToVarcharInConceptOrigins < ActiveRecord::Migration[7.1]
  def up
    change_column :concept_origins, :conceptable_id, :string
    change_column :concept_origins, :originable_id, :string
  end

  def down
    # Reverting to integer assumes that there is no data to preserve,
    # or that there's a separate process to handle it
    change_column :concept_origins, :conceptable_id, :integer, using: 'conceptable_id::integer'
    change_column :concept_origins, :originable_id, :integer, using: 'originable_id::integer'
  end
end

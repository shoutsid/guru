class CreateConceptOrigins < ActiveRecord::Migration[7.1]
  def change
    create_table :concept_origins do |t|
      t.references :conceptable, polymorphic: true, null: false
      t.references :originable, polymorphic: true, null: false

      t.timestamps
    end
  end
end

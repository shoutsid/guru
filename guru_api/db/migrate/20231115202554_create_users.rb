class CreateUsers < ActiveRecord::Migration[7.1]
  def change
    create_table :users do |t|
      t.string :username
      t.string :discriminator
      t.string :avatar

      t.timestamps
    end
  end
end

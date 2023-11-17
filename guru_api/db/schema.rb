# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[7.1].define(version: 2023_11_16_232244) do
  create_table "agents", force: :cascade do |t|
    t.string "name"
    t.string "openai_id"
    t.string "openai_object"
    t.integer "openai_created_at"
    t.text "description"
    t.string "model"
    t.text "system_message"
    t.text "tools", default: ""
    t.text "file_ids", default: ""
    t.text "metadata", default: ""
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "emotion", force: :cascade do |t|
    t.string "emotion", null: false
  end

  create_table "entity", force: :cascade do |t|
    t.string "text", null: false
    t.string "label", null: false
  end

  create_table "open_ai_messages", force: :cascade do |t|
    t.string "openai_id"
    t.string "object"
    t.integer "openai_created_at"
    t.integer "openai_updated_at"
    t.string "openai_thread_id"
    t.string "role"
    t.text "content"
    t.text "file_ids"
    t.string "openai_assitant_id"
    t.text "metadata"
    t.string "run_id"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.integer "thread_id", null: false
    t.string "discord_id"
    t.index ["thread_id"], name: "index_open_ai_messages_on_thread_id"
  end

  create_table "open_ai_threads", force: :cascade do |t|
    t.string "openai_id"
    t.string "object"
    t.integer "openai_created_at"
    t.integer "openai_updated_at"
    t.text "meta_data"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.boolean "discord", default: false
    t.string "discord_channel"
  end

  create_table "opinion", force: :cascade do |t|
    t.float "sentiment_score", null: false
  end

  create_table "topic", force: :cascade do |t|
    t.string "keywords", null: false
  end

  create_table "users", force: :cascade do |t|
    t.string "username"
    t.string "discriminator"
    t.string "avatar"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

end

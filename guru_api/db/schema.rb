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

ActiveRecord::Schema[7.1].define(version: 2023_11_19_203055) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

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

  create_table "concept_origins", force: :cascade do |t|
    t.string "conceptable_type", null: false
    t.string "conceptable_id", null: false
    t.string "originable_type", null: false
    t.string "originable_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["conceptable_type", "conceptable_id"], name: "index_concept_origins_on_conceptable"
    t.index ["originable_type", "originable_id"], name: "index_concept_origins_on_originable"
  end

  create_table "discord_channels", primary_key: "discord_id", id: :bigint, default: nil, force: :cascade do |t|
    t.string "name"
    t.string "type"
    t.integer "position"
    t.text "topic"
    t.bigint "guild_id"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["discord_id"], name: "index_discord_channels_on_discord_id"
    t.index ["guild_id"], name: "index_discord_channels_on_guild_id"
  end

  create_table "discord_guilds", primary_key: "discord_id", id: :bigint, default: nil, force: :cascade do |t|
    t.string "name"
    t.integer "member_count"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "discord_messages", primary_key: "discord_id", id: :bigint, default: nil, force: :cascade do |t|
    t.text "content"
    t.bigint "author_id"
    t.bigint "channel_id"
    t.bigint "guild_id"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["discord_id"], name: "index_discord_messages_on_discord_id"
  end

  create_table "discord_threads", primary_key: "discord_id", id: :bigint, default: nil, force: :cascade do |t|
    t.string "name"
    t.string "type"
    t.bigint "owner_id"
    t.bigint "parent_id"
    t.boolean "archived"
    t.integer "auto_archive_duration"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["discord_id"], name: "index_discord_threads_on_discord_id"
  end

  create_table "discord_users", primary_key: "discord_id", id: :bigint, default: nil, force: :cascade do |t|
    t.string "name"
    t.string "discriminator"
    t.string "avatar"
    t.boolean "bot"
    t.boolean "system"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["discord_id"], name: "index_discord_users_on_discord_id"
  end

  create_table "open_ai_assistants", primary_key: "external_id", id: :string, force: :cascade do |t|
    t.string "name"
    t.text "description"
    t.string "model"
    t.text "instructions"
    t.text "tools"
    t.text "file_ids"
    t.jsonb "metadata"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["external_id"], name: "index_open_ai_assistants_on_external_id"
  end

  create_table "open_ai_messages", primary_key: "external_id", id: :string, force: :cascade do |t|
    t.string "thread_id"
    t.string "role"
    t.text "content"
    t.text "file_ids"
    t.string "assistant_id"
    t.string "run_id"
    t.jsonb "metadata"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["external_id"], name: "index_open_ai_messages_on_external_id"
  end

  create_table "open_ai_threads", primary_key: "external_id", id: :string, force: :cascade do |t|
    t.jsonb "metadata"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["external_id"], name: "index_open_ai_threads_on_external_id"
  end

end

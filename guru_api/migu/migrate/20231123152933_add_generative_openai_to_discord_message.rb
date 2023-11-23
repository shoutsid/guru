class AddGenerativeOpenaiToDiscordMessage < Migu::Migration
  def self.time
    "2023-11-23 15:29:33 +0000"
  end

  def up
    $weaviate_client.schema.update(
      class_name: 'DiscordMessage',
      module_config: {
        "generative-openai": {
          "model": "gpt-3.5-turbo"
        }
      }
    )
  end

  def down
    $weaviate_client.schema.update(
      class_name: 'DiscordMessage',
      module_config: {
        "generative-openai": nil
      }
    )
  end
end

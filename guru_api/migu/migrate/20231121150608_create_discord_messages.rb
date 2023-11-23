require 'weaviate'

class CreateDiscordMessages < Migu::Migration
  def self.time
    "2023-11-21 15:06:08 +0000"
  end

  def up
    $weaviate_client.schema.create(
        class_name: 'DiscordMessage',
        description: 'Information about a Discord message',
        vectorizer: 'text2vec-openai',
        module_config: {
          'qna-openai': {
            'model': 'text-davinci-002',
          }
        },
        properties: [
          {
            'dataType': ['string'],
            'name': 'content',
            'description': 'The content of the message',
          },
          {
            'dataType': ['int'],
            'name': 'author_id',
            'description': 'The ID of the author of the message',
          },
          {
            'dataType': ['int'],
            'name': 'channel_id',
            'description': 'The ID of the channel the message was sent in',
          },
          {
            'dataType': ['int'],
            'name': 'guild_id',
            'description': 'The ID of the guild the message was sent in',
          },
          {
            'dataType': ['date'],
            'name': 'created_at',
            'description': 'The date the message was created',
          },
          {
            'dataType': ['date'],
            'name': 'updated_at',
            'description': 'The date the message was last updated',
          },
        ]
    )
  end

  def down
    $weaviate_client.schema.delete(class_name: 'DiscordMessage')
  end
end

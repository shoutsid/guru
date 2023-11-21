require 'weaviate'

Migu.configuration do |config|
  config.before do
    url = ENV.fetch("WEAVIATE_URL",  "http://localhost:8080")
    $weaviate_client = Weaviate::Client.new(
      url: url
    )
    $weaviate_client.schema.list
  end

  config.after do
    $weaviate_client.schema.list
  end
end

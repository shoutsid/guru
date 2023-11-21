url = ENV.fetch("WEAVIATE_URL") { "http://localhost:8080" }
$weaviate_client = Weaviate::Client.new(
  url: url
)
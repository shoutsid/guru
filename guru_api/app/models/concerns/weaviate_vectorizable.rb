
module WeaviateVectorizable
  extend ActiveSupport::Concern

  included do
    after_commit :update_weaviate_vector, on: [:create, :update]
  end

  private

  def update_weaviate_vector
    vectorized_data = vectorize_data
    send_to_weaviate(vectorized_data)
  end

  def vectorize_data
    # Dynamic vectorization based on the model's attributes
    data_for_vectorization = self.attributes.except('created_at', 'updated_at')
    # Actual vectorization logic using 'migu' gem
    Migu.vectorize(data_for_vectorization)
  end

  def send_to_weaviate(vectorized_data)
    # Actual method to send data to Weaviate using 'weaviate-ruby' gem
    weaviate_client = WeaviateClient.new
    weaviate_client.create_object(vectorized_data)
  end
end

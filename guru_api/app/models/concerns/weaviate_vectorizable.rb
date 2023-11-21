
module WeaviateVectorizable
  extend ActiveSupport::Concern

  class ApiError < StandardError; end

  included do
    after_create :find_and_create_weaviate_object
    after_update :find_and_update_weaviate_object
    WEAVIATE_EXCLUDED_ATTRIBUTES = ['id', 'weaviate_id', 'created_at', 'updated_at']
  end

  def weaviate_object
    $weaviate_client.objects.get(id: self.weaviate_id, class_name: self.class.name)
  end

  def weaviate_object_exists?
    $weaviate_client.objects.exists?(id: self.weaviate_id, class_name: self.class.name)
  end

  def weaviate_attributes
    self.attributes.except(*WEAVIATE_EXCLUDED_ATTRIBUTES)
  end

  class_methods do
    def ask(question)
      $weaviate_client.query.get(
        class_name: self.name,
        with_hybrid: "{ query: \"#{question}\", alpha: 0.5 }",
        fields: (column_names - WEAVIATE_EXCLUDED_ATTRIBUTES).join(' ')
      )
    end
  end

  private

  def find_and_create_weaviate_object
    unless weaviate_object_exists?
      vectorize_and_send_create_to_weaviate
    end
  end

  def find_and_update_weaviate_object
    if weaviate_object_exists?
      vectorize_and_send_update_to_weaviate
    else
      vectorize_and_send_create_to_weaviate
    end
  end

  def vectorize_and_send_create_to_weaviate
    puts("vectorize_and_send_create_to_weaviate: #{self.weaviate_id}")
    response = $weaviate_client.objects.create(id: self.weaviate_id, class_name: self.class.name, properties: weaviate_attributes)

    if response.fetch('error', nil).present?
       raise ApiError, response.fetch('error')
    end
  end

  def vectorize_and_send_update_to_weaviate
    puts("vectorize_and_send_update_to_weaviate: #{self.weaviate_id}")
    response = $weaviate_client.objects.update(id: self.weaviate_id, class_name: self.class.name, properties: weaviate_attributes)

    if response.fetch('error', nil).present?
      raise ApiError, response.fetch('error')
    end
  end
end

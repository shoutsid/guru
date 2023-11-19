module KafkaEventPublisher
  extend ActiveSupport::Concern

  included do
    after_create :publish_create_event
    after_update :publish_update_event
    after_destroy :publish_destroy_event
  end

  private

  def publish_create_event
    KafkaProducer.publish("#{self.class.model_name.param_key}_create", self.as_json)
  end

  def publish_update_event
    KafkaProducer.publish("#{self.class.model_name.param_key}_update", self.as_json)
  end

  def publish_destroy_event
    KafkaProducer.publish("#{self.class.model_name.param_key}_destroy", { id: self.id })
  end
end

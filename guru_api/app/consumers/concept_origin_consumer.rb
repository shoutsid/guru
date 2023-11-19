# frozen_string_literal: true

class ConceptOriginConsumer < ApplicationConsumer
  def consume
    # TODO: sort out how to handle multiple of the same messages
    messages.payloads.each do |payload|
      puts("ConceptOriginConsumer: #{payload}")
      conceptable = payload['conceptable_class'].constantize.find(payload['conceptable_id'])
      originable = payload['originable_class'].constantize.find(payload['originable_id'])
      conceptable.concept_origins.find_or_create_by!(
        originable: originable
      )
    end
  end
end
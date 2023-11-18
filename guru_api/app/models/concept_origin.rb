class ConceptOrigin < ApplicationRecord
  belongs_to :conceptable, polymorphic: true
  belongs_to :originable, polymorphic: true
end

Rails.application.routes.draw do

  # JSON only
  resources :users, defaults: { format: :json }
  resources :threads, defaults: { format: :json } do
    resources :messages, defaults: { format: :json }
  end
  resources :agents, defaults: { format: :json }

  get "up" => "rails/health#show", as: :rails_health_check
end

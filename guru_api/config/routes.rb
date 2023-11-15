Rails.application.routes.draw do
  # json only
  resources :open_ai_messages, defaults: { format: :json }
  resources :open_ai_threads, defaults: { format: :json }
  resources :agents, defaults: { format: :json }

  get "up" => "rails/health#show", as: :rails_health_check
end

Rails.application.routes.draw do

  # JSON only
  resources :users, defaults: { format: :json }
  resources :threads, defaults: { format: :json } do
    resources :messages, defaults: { format: :json }
  end
  resources :agents, defaults: { format: :json }

  post '/chat/completion', to: 'chat#completion'

  get "up" => "rails/health#show", as: :rails_health_check
end

class ApplicationController < ActionController::Base
  # API controllers don't need CSRF protection
  protect_from_forgery with: :null_session
end

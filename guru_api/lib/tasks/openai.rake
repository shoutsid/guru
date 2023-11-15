namespace :openai do
  desc 'List all OpenAI assistants'
  task update_assistants: :environment do
    client = OpenAI::Client.new
    assistants = client.assistants.list
    puts 'List of OpenAI Assistants:'
    assistants["data"].each do |assistant|
      puts "---------------------------"
      puts "Object: #{assistant}"
      puts "---------------------------"
      Agent.find_or_create_by(openai_id: assistant["id"]) do |agent|
        agent.openai_object = "assistant"
        agent.openai_created_at = assistant["created_at"]
        agent.description = assistant["description"]
        agent.model = assistant["model"]
        agent.system_message = assistant["instructions"]
        agent.tools = assistant["tools"]
        agent.file_ids = assistant["file_ids"]
        agent.metadata = assistant["metadata"]
      end
    end
  end

  desc 'List all OpenAI threads'
  task update_threads: :environment do
    OpenAiThread.all.pluck(:openai_id).each do |thread_id|
      client = OpenAI::Client.new
      threads = client.threads.retrieve(thread_id)
      puts 'List of OpenAI Threads:'
      threads["data"].each do |thread|
        puts "---------------------------"
        puts "Object: #{thread}"
        puts "---------------------------"
        OpenAiThread.find_or_create_by(openai_id: thread["id"]) do |openai_thread|
          openai_thread.openai_object = "thread"
          openai_thread.openai_created_at = thread["created_at"]
          openai_thread.metadata = thread["metadata"]
        end
      end
    end
  end
end

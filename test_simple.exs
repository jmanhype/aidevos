# Simple test script for instructor integration
# Start the application first
{:ok, _} = Application.ensure_all_started(:realworld)

# Test with a simple call
IO.puts("Starting test...")

# Using alias
alias Realworld.DurableObjects.Instructor.CodePlan

result = Instructor.chat_completion(
  model: "gpt-4o-mini",
  response_model: CodePlan,
  max_retries: 2,
  messages: [
    %{role: "system", content: "You are a helpful assistant."},
    %{role: "user", content: "Plan how to implement a simple hello world function."}
  ]
)

IO.puts("Result:")
IO.inspect(result)

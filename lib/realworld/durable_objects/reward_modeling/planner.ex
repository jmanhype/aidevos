defmodule Realworld.DurableObjects.RewardModeling.Planner do
  alias Realworld.DurableObjects.Instructor.CodePlan
  
  def plan(object, prompt) do
    system_prompt = """
    You are an expert code modification planner. Your role is to analyze the given code and prompt, 
    and determine what checks will be needed during the evaluation phase.
    
    For each request, determine:
    1. If constraint checks are needed (code must follow specific constraints or requirements)
    2. If factuality checks are needed (code interacts with or represents real-world facts)
    
    Provide a step-by-step plan for implementing the requested modifications.
    """
    
    prompt_text = """
    # Current Object Information
    Name: #{object.name}
    Description: #{object.description}
    Current Version: #{object.version}
    
    # Current Code Content
    ```elixir
    #{object.code_content}
    ```
    
    # API Schema (if available)
    #{if object.api_schema, do: "```json\n#{object.api_schema}\n```", else: "No API schema provided."}
    
    # Requested Modification
    #{prompt}
    
    Based on this information, determine what checks will be needed and outline a step-by-step plan.
    """
    
    try do
      case Instructor.chat_completion(
        model: "gpt-4-turbo",
        response_model: CodePlan,
        max_retries: 2,
        messages: [
          %{role: "system", content: system_prompt},
          %{role: "user", content: prompt_text}
        ]
      ) do
        {:ok, plan} -> {:ok, plan}
        {:error, error} -> {:error, "Planning failed: #{inspect(error)}"}
      end
    rescue
      e -> {:error, "Planning failed with exception: #{inspect(e)}"}
    end
  end
end

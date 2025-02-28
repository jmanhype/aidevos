defmodule Realworld.DurableObjects.RewardModeling.ConstraintChecker do
  alias Realworld.DurableObjects.Instructor.ConstraintCheck
  
  def check(original_code, modified_code, api_schema) do
    prompt = """
    # Constraint Validation
    
    You are tasked with validating that modified code adheres to constraints in the original code and API schema.
    
    ## Original Code
    ```elixir
    #{original_code}
    ```
    
    ## Modified Code
    ```elixir
    #{modified_code}
    ```
    
    ## API Schema (if available)
    #{if api_schema && api_schema != "", do: "```json\n#{api_schema}\n```", else: "No API schema provided."}
    
    ## Validation Task
    
    Analyze the modified code to ensure:
    1. It maintains all API contracts defined in the schema
    2. Public interfaces remain compatible with the original code
    3. Type specifications are consistent
    4. All mandatory constraints are enforced
    5. No regressions are introduced
    
    Provide a score from 0.0 to 1.0, a list of issues found, and a detailed analysis.
    """
    
    try do
      case Instructor.chat_completion(
        model: "gpt-4-turbo",
        response_model: ConstraintCheck,
        max_retries: 2,
        messages: [
          %{role: "user", content: prompt}
        ]
      ) do
        {:ok, result} -> result
        {:error, error} -> 
          %ConstraintCheck{
            score: 0.0,
            issues: ["Failed to evaluate constraints: #{inspect(error)}"],
            analysis: "The constraint evaluation process failed."
          }
      end
    rescue
      e -> 
        %ConstraintCheck{
          score: 0.0,
          issues: ["Failed to evaluate constraints due to exception: #{inspect(e)}"],
          analysis: "The constraint evaluation process encountered an exception."
        }
    end
  end
end

defmodule Realworld.DurableObjects.RewardModeling.FactualityChecker do
  alias Realworld.DurableObjects.Instructor.FactualityCheck
  
  def check(prompt, original_code, modified_code) do
    prompt_text = """
    # Factuality Validation
    
    You are tasked with validating the factual correctness of modified code.
    
    ## Original Prompt
    #{prompt}
    
    ## Original Code
    ```elixir
    #{original_code}
    ```
    
    ## Modified Code
    ```elixir
    #{modified_code}
    ```
    
    ## Validation Task
    
    Analyze the modified code to ensure:
    1. All implemented algorithms are correct
    2. Mathematical operations are accurate
    3. Any domain-specific knowledge is accurate and correctly applied
    4. Any references to external systems or APIs are accurate
    5. All comments and documentation accurately reflect the code
    
    Provide a score from 0.0 to 1.0, a list of factual issues found, and a detailed analysis.
    """
    
    try do
      case Instructor.chat_completion(
        model: "gpt-4-turbo",
        response_model: FactualityCheck,
        max_retries: 2,
        messages: [
          %{role: "user", content: prompt_text}
        ]
      ) do
        {:ok, result} -> result
        {:error, error} -> 
          %FactualityCheck{
            score: 0.0,
            issues: ["Failed to evaluate factuality: #{inspect(error)}"],
            analysis: "The factuality evaluation process failed."
          }
      end
    rescue
      e -> 
        %FactualityCheck{
          score: 0.0,
          issues: ["Failed to evaluate factuality due to exception: #{inspect(e)}"],
          analysis: "The factuality evaluation process encountered an exception."
        }
    end
  end
end

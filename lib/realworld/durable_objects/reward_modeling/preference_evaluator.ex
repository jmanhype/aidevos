defmodule Realworld.DurableObjects.RewardModeling.PreferenceEvaluator do
  alias Realworld.DurableObjects.Instructor.PreferenceEvaluation
  
  def evaluate(prompt, original_code, modified_code) do
    prompt_text = """
    # Human Preference Evaluation
    
    You are tasked with evaluating code modifications based on human preferences.
    
    ## Original Request
    #{prompt}
    
    ## Original Code
    ```elixir
    #{original_code}
    ```
    
    ## Modified Code
    ```elixir
    #{modified_code}
    ```
    
    ## Evaluation Task
    
    Evaluate the modified code on the following human preference dimensions:
    1. Readability - Is the code easy to read and understand?
    2. Maintainability - Is the code structured for easy maintenance?
    3. Elegance - Is the solution elegant and well-designed?
    4. Completeness - Does the code fully address the requirements in the prompt?
    5. Documentation - Is the code well-documented?
    
    Provide a score from 0.0 to 1.0, a detailed rationale, and lists of strengths and weaknesses.
    """
    
    try do
      case Instructor.chat_completion(
        model: "gpt-4-turbo",
        response_model: PreferenceEvaluation,
        max_retries: 2,
        messages: [
          %{role: "user", content: prompt_text}
        ]
      ) do
        {:ok, result} -> result
        {:error, error} -> 
          %PreferenceEvaluation{
            score: 0.0,
            rationale: "Evaluation failed: #{inspect(error)}",
            strengths: [],
            weaknesses: ["Unable to evaluate human preferences"]
          }
      end
    rescue
      e -> 
        %PreferenceEvaluation{
          score: 0.0,
          rationale: "Evaluation failed due to exception: #{inspect(e)}",
          strengths: [],
          weaknesses: ["The preference evaluation process encountered an exception"]
        }
    end
  end
end

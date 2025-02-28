defmodule Realworld.DurableObjects.Changes.ModifyCode do
  alias Realworld.DurableObjects.Instructor.CodeModification
  alias Realworld.DurableObjects.RewardModeling.Planner
  alias Realworld.DurableObjects.RewardModeling.ConstraintChecker
  alias Realworld.DurableObjects.RewardModeling.FactualityChecker
  alias Realworld.DurableObjects.RewardModeling.PreferenceEvaluator
  alias Realworld.DurableObjects.RewardModeling.Judger
  
  # Minimum score thresholds for accepting code modifications
  @min_constraint_score 0.7
  @min_factuality_score 0.8
  @min_preference_score 0.6
  
  @doc """
  Attempts to modify a Durable Object based on a natural language prompt.
  
  The process includes:
  1. Planning the modification
  2. Generating the modified code
  3. Evaluating the modification for constraints, factuality, and human preferences
  4. Accepting or rejecting the modification based on evaluation scores
  
  ## Parameters
  
  - object: The durable object to modify
  - prompt: Natural language prompt describing the desired modifications
  
  ## Returns
  
  `{:ok, modification}` if successful, `{:error, reason}` otherwise
  """
  def modify(object, prompt) do
    # First, plan the modification
    case Planner.plan(object, prompt) do
      {:ok, plan} ->
        case generate_code_modification(object, prompt, plan) do
          {:ok, modification} ->
            # Evaluate the modification against our criteria
            evaluation = evaluate_modification(object, prompt, modification, plan)
            
            # Use Judger to decide whether to accept the modification
            if Judger.accept?(evaluation) do
              {:ok, modification}
            else
              {:error, "Modification does not meet quality standards. Scores: #{inspect(evaluation)}"}
            end
            
          error -> error
        end
        
      {:error, reason} ->
        {:error, reason}
    end
  end
  
  @doc """
  Generates a code modification based on the object, prompt, and plan.
  """
  defp generate_code_modification(object, prompt, plan) do
    system_prompt = """
    You are an expert code modification AI. Your task is to modify the provided code according to the user's request.
    
    Follow these guidelines:
    1. Make only the changes necessary to fulfill the request
    2. Preserve the overall structure and style of the original code
    3. Add thorough comments explaining your changes
    4. Ensure the modified code is correct and maintains compatibility
    5. Consider the plan that was generated to guide your modifications
    
    Plan for modification:
    #{inspect(plan)}
    """
    
    user_prompt = """
    # Current Object Code
    ```elixir
    #{object.code_content}
    ```
    
    # Modification Request
    #{prompt}
    
    Please provide the modified code that addresses this request.
    """
    
    try do
      case Instructor.chat_completion(
        model: "gpt-4-turbo",
        response_model: CodeModification,
        max_retries: 3,
        messages: [
          %{role: "system", content: system_prompt},
          %{role: "user", content: user_prompt}
        ]
      ) do
        {:ok, modification} -> {:ok, modification}
        {:error, error} -> {:error, "Code modification failed: #{inspect(error)}"}
      end
    rescue
      e -> {:error, "Code modification failed with exception: #{inspect(e)}"}
    end
  end
  
  defp evaluate_modification(object, prompt, modification, plan) do
    # Run the different evaluation checks based on the plan
    evaluation_results = %{}
    
    # Always run preference evaluation
    preference_result = PreferenceEvaluator.evaluate(
      prompt, 
      object.code_content, 
      modification.modified_code
    )
    
    evaluation_results = Map.put(evaluation_results, :preference, preference_result)
    
    # Run constraint check if needed
    evaluation_results = if plan.constraint_check_needed do
      constraint_result = ConstraintChecker.check(
        object.code_content, 
        modification.modified_code, 
        object.api_schema
      )
      Map.put(evaluation_results, :constraint, constraint_result)
    else
      evaluation_results
    end
    
    # Run factuality check if needed
    evaluation_results = if plan.factuality_check_needed do
      factuality_result = FactualityChecker.check(
        prompt, 
        object.code_content, 
        modification.modified_code
      )
      Map.put(evaluation_results, :factuality, factuality_result)
    else
      evaluation_results
    end
    
    # Make a final judgement on the modification
    judger_result = Judger.judge(
      evaluation_results,
      %{
        constraint_threshold: @min_constraint_score,
        factuality_threshold: @min_factuality_score,
        preference_threshold: @min_preference_score
      }
    )
    
    {:ok, judger_result}
  end
end

defmodule Realworld.DurableObjects.RewardModeling.Judger do
  @moduledoc """
  The Judger combines the results from multiple evaluation dimensions (human preferences,
  constraints, factuality) and makes a final decision on whether a code modification
  should be accepted.
  
  It applies configurable thresholds for each evaluation dimension and calculates a
  weighted score to determine acceptance.
  """
  
  # Default weights for the different evaluation dimensions
  @default_weights %{
    preference: 0.4,
    constraint: 0.3,
    factuality: 0.3
  }
  
  @doc """
  Checks if an evaluation result should be accepted.
  
  ## Parameters
  
  - evaluation: The evaluation result, typically from the judge/2 function
  
  ## Returns
  
  Boolean indicating whether the evaluation is accepted
  """
  def accept?({:ok, evaluation}) do
    Map.get(evaluation, :accepted, false)
  end
  
  def accept?(_) do
    false
  end
  
  @doc """
  Judge a modification based on evaluation results and configured thresholds.
  
  ## Parameters
  
  - evaluation_results: Map containing results for the different evaluation dimensions
  - thresholds: Map containing acceptance thresholds for each dimension
  
  ## Returns
  
  A map containing:
  - accepted: Whether the modification is accepted
  - score: The weighted score
  - rejection_reason: If rejected, the reason why
  """
  def judge(evaluation_results, thresholds) do
    # Extract scores from evaluation results
    preference_score = get_dimension_score(evaluation_results, :preference)
    constraint_score = get_dimension_score(evaluation_results, :constraint)
    factuality_score = get_dimension_score(evaluation_results, :factuality)
    
    # Calculate weighted score
    weights = @default_weights
    weighted_score = 
      (preference_score * weights.preference) +
      (constraint_score * (Map.get(weights, :constraint, 0))) +
      (factuality_score * (Map.get(weights, :factuality, 0)))
    
    # Normalize by actual weight sum
    actual_weight_sum = 
      weights.preference + 
      (if Map.has_key?(evaluation_results, :constraint), do: weights.constraint, else: 0) +
      (if Map.has_key?(evaluation_results, :factuality), do: weights.factuality, else: 0)
    
    normalized_score = weighted_score / actual_weight_sum
    
    # Check individual dimension thresholds
    {passed, rejection_reason} = cond do
      Map.has_key?(evaluation_results, :constraint) && 
      constraint_score < thresholds.constraint_threshold ->
        {false, "Constraint score #{constraint_score} below threshold #{thresholds.constraint_threshold}"}
        
      Map.has_key?(evaluation_results, :factuality) && 
      factuality_score < thresholds.factuality_threshold ->
        {false, "Factuality score #{factuality_score} below threshold #{thresholds.factuality_threshold}"}
        
      preference_score < thresholds.preference_threshold ->
        {false, "Preference score #{preference_score} below threshold #{thresholds.preference_threshold}"}
        
      true ->
        {true, nil}
    end
    
    # Return judgment result
    %{
      accepted: passed,
      score: normalized_score,
      individual_scores: %{
        preference: preference_score,
        constraint: constraint_score,
        factuality: factuality_score
      },
      rejection_reason: rejection_reason
    }
  end
  
  # Helper function to safely get a dimension score from evaluation results
  defp get_dimension_score(evaluation_results, dimension) do
    case Map.get(evaluation_results, dimension) do
      nil -> 1.0  # If dimension wasn't evaluated, assume perfect score
      result -> Map.get(result, :score, 1.0)
    end
  end
end

defmodule Realworld.DurableObjects.RewardModeling.Judger do
  @moduledoc """
  Judges whether generated code meets quality standards.
  
  This module combines the results from the ConstraintChecker, FactualityChecker,
  and PreferenceEvaluator to determine if the generated code is acceptable.
  """
  
  @doc """
  Judges whether generated code meets quality standards.
  
  ## Parameters
  
  - evaluation: The evaluation results from the checkers
  - thresholds: The minimum score thresholds for each category
  
  ## Returns
  
  `{:ok, %{accepted: boolean, rejection_reason: string}}` if successful, `{:error, reason}` otherwise
  """
  def judge(evaluation, thresholds) do
    # Extract scores
    constraint_score = evaluation.constraint_score
    factuality_score = evaluation.factuality_score
    preference_score = evaluation.preference_score
    
    # Extract thresholds
    constraint_threshold = thresholds.constraint_threshold
    factuality_threshold = thresholds.factuality_threshold
    preference_threshold = thresholds.preference_threshold
    
    # Determine if the code meets all thresholds
    cond do
      constraint_score < constraint_threshold ->
        {:ok, %{
          accepted: false,
          rejection_reason: "Constraint score #{constraint_score} below threshold #{constraint_threshold}",
          scores: %{
            constraint: constraint_score,
            factuality: factuality_score,
            preference: preference_score
          },
          feedback: %{
            constraint: evaluation.constraint_feedback,
            factuality: evaluation.factuality_feedback,
            preference: evaluation.preference_feedback
          },
          detailed_reason: """
          The code does not meet constraint requirements:
          
          #{evaluation.constraint_feedback}
          
          Key issues:
          - Constraint score: #{constraint_score} (threshold: #{constraint_threshold})
          - Factuality score: #{factuality_score} (threshold: #{factuality_threshold})
          - Preference score: #{preference_score} (threshold: #{preference_threshold})
          """
        }}
        
      factuality_score < factuality_threshold ->
        {:ok, %{
          accepted: false,
          rejection_reason: "Factuality score #{factuality_score} below threshold #{factuality_threshold}",
          scores: %{
            constraint: constraint_score,
            factuality: factuality_score,
            preference: preference_score
          },
          feedback: %{
            constraint: evaluation.constraint_feedback,
            factuality: evaluation.factuality_feedback,
            preference: evaluation.preference_feedback
          },
          detailed_reason: """
          The code does not meet factuality requirements:
          
          #{evaluation.factuality_feedback}
          
          Key issues:
          - Constraint score: #{constraint_score} (threshold: #{constraint_threshold})
          - Factuality score: #{factuality_score} (threshold: #{factuality_threshold})
          - Preference score: #{preference_score} (threshold: #{preference_threshold})
          """
        }}
        
      preference_score < preference_threshold ->
        {:ok, %{
          accepted: false,
          rejection_reason: "Preference score #{preference_score} below threshold #{preference_threshold}",
          scores: %{
            constraint: constraint_score,
            factuality: factuality_score,
            preference: preference_score
          },
          feedback: %{
            constraint: evaluation.constraint_feedback,
            factuality: evaluation.factuality_feedback,
            preference: evaluation.preference_feedback
          },
          detailed_reason: """
          The code does not meet preference requirements:
          
          #{evaluation.preference_feedback}
          
          Key issues:
          - Constraint score: #{constraint_score} (threshold: #{constraint_threshold})
          - Factuality score: #{factuality_score} (threshold: #{factuality_threshold})
          - Preference score: #{preference_score} (threshold: #{preference_threshold})
          """
        }}
        
      true ->
        {:ok, %{
          accepted: true,
          acceptance_reason: "All scores meet thresholds",
          scores: %{
            constraint: constraint_score,
            factuality: factuality_score,
            preference: preference_score
          },
          feedback: %{
            constraint: evaluation.constraint_feedback,
            factuality: evaluation.factuality_feedback,
            preference: evaluation.preference_feedback
          }
        }}
    end
  end
end

# Test script for the self-modifying objects system using Instructor
# Start the application first to ensure all modules are loaded
Application.ensure_all_started(:realworld)

alias Realworld.DurableObjects.Instructor.CodePlan
alias Realworld.DurableObjects.Instructor.CodeModification
alias Realworld.DurableObjects.Instructor.ConstraintCheck
alias Realworld.DurableObjects.Instructor.FactualityCheck
alias Realworld.DurableObjects.Instructor.PreferenceEvaluation
alias Realworld.DurableObjects.RewardModeling.Judger

IO.puts("=== Testing the Code Planning Phase ===")

# 1. Test code planning
{:ok, plan} = Instructor.chat_completion(
  model: "gpt-4o-mini",
  response_model: CodePlan,
  max_retries: 2,
  messages: [
    %{role: "system", content: "You are a code planning assistant."},
    %{role: "user", content: "Plan how to implement a simple calculator function that supports addition and subtraction."}
  ]
)

IO.puts("\nCode Plan:")
IO.inspect(plan)

# 2. Test code modification
IO.puts("\n=== Testing the Code Modification Phase ===")

{:ok, modification} = Instructor.chat_completion(
  model: "gpt-4o-mini",
  response_model: CodeModification,
  max_retries: 2,
  messages: [
    %{role: "system", content: "You are a code modification assistant."},
    %{role: "user", content: """
      Generate a modification that implements a simple calculator function based on this plan:
      
      #{inspect(plan.steps)}
      
      The function should take three parameters: operation, a, and b.
      It should return the result of applying the operation to a and b.
      """
    }
  ]
)

IO.puts("\nCode Modification:")
IO.inspect(modification)

# 3. Test constraint checking
IO.puts("\n=== Testing the Constraint Checking Phase ===")

{:ok, constraint_check} = Instructor.chat_completion(
  model: "gpt-4o-mini",
  response_model: ConstraintCheck,
  max_retries: 2,
  messages: [
    %{role: "system", content: "You are a constraint checking assistant."},
    %{role: "user", content: """
      Check if the following code modification satisfies these constraints:
      1. The function should handle both addition and subtraction
      2. The function should be pure (no side effects)
      3. The function should handle numeric inputs only
      
      Code modification:
      #{modification.code}
      """
    }
  ]
)

IO.puts("\nConstraint Check:")
IO.inspect(constraint_check)

# 4. Test factuality checking
IO.puts("\n=== Testing the Factuality Checking Phase ===")

{:ok, factuality_check} = Instructor.chat_completion(
  model: "gpt-4o-mini",
  response_model: FactualityCheck,
  max_retries: 2,
  messages: [
    %{role: "system", content: "You are a factuality checking assistant."},
    %{role: "user", content: """
      Verify if the following code modification correctly implements these requirements:
      1. A calculator function that supports addition and subtraction
      2. Takes operation, a, and b as parameters
      3. Returns the result of the operation
      
      Code modification:
      #{modification.code}
      """
    }
  ]
)

IO.puts("\nFactuality Check:")
IO.inspect(factuality_check)

# 5. Test preference evaluation
IO.puts("\n=== Testing the Preference Evaluation Phase ===")

{:ok, preference_evaluation} = Instructor.chat_completion(
  model: "gpt-4o-mini",
  response_model: PreferenceEvaluation,
  max_retries: 2,
  messages: [
    %{role: "system", content: "You are a preference evaluation assistant."},
    %{role: "user", content: """
      Evaluate the following code modification for human preferences:
      1. Code readability
      2. Maintainability
      3. Simplicity
      
      Code modification:
      #{modification.code}
      """
    }
  ]
)

IO.puts("\nPreference Evaluation:")
IO.inspect(preference_evaluation)

# 6. Test the judger
IO.puts("\n=== Testing the Judger ===")

# Combine evaluations
evaluation_results = %{
  constraint: %{score: constraint_check.score},
  factuality: %{score: factuality_check.score},
  preference: %{score: preference_evaluation.score}
}

thresholds = %{
  constraint_threshold: 0.7,
  factuality_threshold: 0.7,
  preference_threshold: 0.7
}

judgment = Judger.judge(evaluation_results, thresholds)

IO.puts("\nJudgment Result:")
IO.inspect(judgment)

acceptance = Judger.accept?({:ok, judgment})
IO.puts("\nModification Accepted: #{acceptance}")

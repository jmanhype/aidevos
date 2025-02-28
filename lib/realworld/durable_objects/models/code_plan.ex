defmodule Realworld.DurableObjects.Models.CodePlan do
  # Temporarily removed: use Instructor.Defined

  @derive Jason.Encoder
  defstruct [
    :constraint_check_needed,
    :factuality_check_needed,
    :steps,
    :reasoning
  ]

  @type t :: %__MODULE__{
    constraint_check_needed: boolean(),
    factuality_check_needed: boolean(),
    steps: [String.t()],
    reasoning: String.t()
  }
end

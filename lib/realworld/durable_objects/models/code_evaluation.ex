defmodule Realworld.DurableObjects.Models.CodeEvaluation do
  # Temporarily removed: use Instructor.Defined

  @derive Jason.Encoder
  defstruct [
    :human_preference_score,
    :factuality_score,
    :constraint_score,
    :weighted_score,
    :issues,
    :recommendations
  ]

  @type t :: %__MODULE__{
    human_preference_score: float(),
    factuality_score: float(),
    constraint_score: float(),
    weighted_score: float(),
    issues: [String.t()],
    recommendations: [String.t()]
  }
end

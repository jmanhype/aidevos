defmodule Realworld.DurableObjects.Instructor.PreferenceEvaluation do
  @moduledoc """
  Instructor schema for human preference evaluation results.
  """
  use Ecto.Schema
  use Instructor
  import Ecto.Changeset

  @llm_doc """
  ## Field Descriptions:
  - score: A score from 0.0 to 1.0 reflecting human preference for the modified code
  - rationale: Rationale for the preference score
  - strengths: Strengths of the modified code from a human perspective
  - weaknesses: Weaknesses of the modified code from a human perspective
  """
  @primary_key false
  embedded_schema do
    field(:score, :float)
    field(:rationale, :string)
    field(:strengths, {:array, :string})
    field(:weaknesses, {:array, :string})
  end

  @impl true
  def validate_changeset(changeset) do
    changeset
    |> validate_required([:score, :rationale, :strengths, :weaknesses])
    |> validate_number(:score, greater_than_or_equal_to: 0.0, less_than_or_equal_to: 1.0)
  end
end

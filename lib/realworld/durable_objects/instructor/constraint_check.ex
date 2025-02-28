defmodule Realworld.DurableObjects.Instructor.ConstraintCheck do
  @moduledoc """
  Instructor schema for constraint validation results.
  """
  use Ecto.Schema
  use Instructor
  import Ecto.Changeset

  @llm_doc """
  ## Field Descriptions:
  - score: A score from 0.0 to 1.0 indicating how well the code meets constraints
  - issues: A list of issues where constraints were not met
  - analysis: Detailed analysis of constraint adherence
  """
  @primary_key false
  embedded_schema do
    field(:score, :float)
    field(:issues, {:array, :string})
    field(:analysis, :string)
  end

  @impl true
  def validate_changeset(changeset) do
    changeset
    |> validate_required([:score, :issues, :analysis])
    |> validate_number(:score, greater_than_or_equal_to: 0.0, less_than_or_equal_to: 1.0)
  end
end

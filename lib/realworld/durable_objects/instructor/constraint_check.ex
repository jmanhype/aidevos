defmodule Realworld.DurableObjects.Instructor.ConstraintCheck do
  @moduledoc """
  Defines the structure for constraint check results.
  """
  
  use Ecto.Schema
  use Instructor
  import Ecto.Changeset
  
  @llm_doc """
  ## Field Descriptions:
  - score: A score from 0.0 to 1.0 indicating how well the code meets constraints
  - feedback: Detailed feedback on constraint compliance
  - issues: List of specific constraint issues found
  - recommendations: List of recommendations for improving constraint compliance
  """
  @primary_key false
  embedded_schema do
    field(:score, :float)
    field(:feedback, :string)
    field(:issues, {:array, :string})
    field(:recommendations, {:array, :string})
  end
  
  @impl true
  def validate_changeset(changeset) do
    changeset
    |> validate_required([:score, :feedback])
    |> validate_number(:score, greater_than_or_equal_to: 0.0, less_than_or_equal_to: 1.0)
  end
end

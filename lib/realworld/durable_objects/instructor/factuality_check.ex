defmodule Realworld.DurableObjects.Instructor.FactualityCheck do
  @moduledoc """
  Instructor schema for factuality validation results.
  """
  use Ecto.Schema
  use Instructor
  import Ecto.Changeset

  @llm_doc """
  ## Field Descriptions:
  - score: A score from 0.0 to 1.0 indicating the factual correctness of the code
  - issues: List of factual issues or inaccuracies found
  - analysis: Detailed analysis of factual correctness
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

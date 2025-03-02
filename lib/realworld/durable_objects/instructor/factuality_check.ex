defmodule Realworld.DurableObjects.Instructor.FactualityCheck do
  @moduledoc """
  Defines the structure for factuality check results.
  """
  
  use Ecto.Schema
  use Instructor
  import Ecto.Changeset
  
  @llm_doc """
  ## Field Descriptions:
  - score: A score from 0.0 to 1.0 indicating the factual correctness of the code
  - feedback: Detailed feedback on factual correctness
  - issues: List of specific factual issues found
  - recommendations: List of recommendations for improving factual correctness
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

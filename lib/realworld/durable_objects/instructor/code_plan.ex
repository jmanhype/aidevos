defmodule Realworld.DurableObjects.Instructor.CodePlan do
  @moduledoc """
  Instructor schema for code modification plans.
  """
  use Ecto.Schema
  use Instructor
  import Ecto.Changeset

  @llm_doc """
  ## Field Descriptions:
  - constraint_check_needed: Whether the code modification will require constraint validation
  - factuality_check_needed: Whether the code modification will require factuality validation
  - steps: A list of steps that should be taken to implement the modification
  - reasoning: The reasoning behind the plan decisions
  """
  @primary_key false
  embedded_schema do
    field(:constraint_check_needed, :boolean)
    field(:factuality_check_needed, :boolean)
    field(:steps, {:array, :string})
    field(:reasoning, :string)
  end

  @impl true
  def validate_changeset(changeset) do
    changeset
    |> validate_required([:constraint_check_needed, :factuality_check_needed, :steps, :reasoning])
    |> validate_length(:steps, min: 1, message: "must include at least one implementation step")
    |> validate_length(:reasoning, min: 10, message: "reasoning should be substantial")
  end
end

defmodule Realworld.DurableObjects.Instructor.CodeModification do
  @moduledoc """
  Instructor schema for code modifications.
  """
  use Ecto.Schema
  use Instructor
  import Ecto.Changeset

  @llm_doc """
  ## Field Descriptions:
  - modified_code: The complete modified code implementing the requested changes
  - modification_summary: A list of key points summarizing what was changed
  - approach: The approach taken to implement the changes
  - considerations: A list of key considerations made during the modification
  - risks: A list of potential risks or edge cases with the implementation
  - tests: A list of suggested tests for the modifications
  """
  @primary_key false
  embedded_schema do
    field(:modified_code, :string)
    field(:modification_summary, {:array, :string})
    field(:approach, :string)
    field(:considerations, {:array, :string})
    field(:risks, {:array, :string})
    field(:tests, {:array, :string})
  end

  @impl true
  def validate_changeset(changeset) do
    changeset
    |> validate_required([:modified_code, :modification_summary])
    |> validate_length(:modified_code, min: 10, message: "code must be more substantial")
    |> validate_length(:modification_summary, min: 1, message: "must include at least one summary point")
  end
end

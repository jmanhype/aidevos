defmodule Realworld.DurableObjects.Models.CodeModification do
  # Temporarily removed: use Instructor.Defined

  @derive Jason.Encoder
  defstruct [
    :modified_code,
    :modification_summary,
    :approach,
    :considerations,
    :risks,
    :tests
  ]

  @type t :: %__MODULE__{
    modified_code: String.t(),
    modification_summary: String.t(),
    approach: String.t(),
    considerations: [String.t()],
    risks: [String.t()],
    tests: [test_t()]
  }

  @type test_t :: %{
    name: String.t(),
    purpose: String.t(),
    code: String.t()
  }
end

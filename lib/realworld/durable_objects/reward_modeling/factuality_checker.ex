defmodule Realworld.DurableObjects.RewardModeling.FactualityChecker do
  @moduledoc """
  Evaluates the factual correctness of generated code.
  
  This module checks if the generated code:
  - Is syntactically correct
  - Uses existing libraries and functions correctly
  - Follows logical patterns and best practices
  - Contains complete implementations without truncation
  - Has accurate documentation
  """
  
  alias Realworld.DurableObjects.Instructor.CodeGeneration
  alias Realworld.DurableObjects.Instructor.FactualityCheck
  
  @doc """
  Evaluates the factual correctness of generated code.
  
  ## Parameters
  
  - name: Name of the object being created
  - description: Description of the object's purpose
  - generation: The CodeGeneration struct with generated code
  
  ## Returns
  
  `{:ok, %{score: float, feedback: string}}` if successful, `{:error, reason}` otherwise
  """
  def evaluate(name, description, %CodeGeneration{} = generation) do
    system_prompt = """
    You are an expert Elixir code reviewer focused on factual correctness.
    Your task is to evaluate the factual correctness of generated code.
    
    Factual correctness includes:
    1. Syntactic correctness - the code follows Elixir syntax rules
    2. Semantic correctness - the code uses existing libraries and functions correctly
    3. Logical correctness - the code follows logical patterns and best practices
    4. Completeness - all functions are fully implemented without truncation
    5. Documentation accuracy - documentation correctly describes functionality
    6. Type specification accuracy - type specs match function implementations
    7. Error handling - proper error handling for edge cases
    8. Test coverage - tests actually verify the functionality
    
    Provide a score from 0.0 to 1.0 where:
    - 0.0-0.3: Major factual errors that make the code unusable
    - 0.4-0.6: Some factual errors that need significant correction
    - 0.7-0.8: Minor factual errors that need minor correction
    - 0.9-1.0: No significant factual errors, code is correct and complete
    
    Also provide detailed feedback on any factual errors found and how to correct them.
    """
    
    prompt_text = """
    # Object Information
    Name: #{name}
    Description: #{description}
    
    # Generated Code
    Code Content:
    ```elixir
    #{generation.code_content}
    ```
    
    API Schema:
    ```
    #{generation.api_schema || "None provided"}
    ```
    
    File Structure:
    #{inspect(generation.file_structure, pretty: true)}
    
    Please evaluate the factual correctness of this generated code.
    Be thorough in your analysis and look for any issues that would affect the code's functionality.
    """
    
    try do
      case Instructor.chat_completion(
        model: "gpt-4-turbo",
        response_model: FactualityCheck,
        messages: [
          %{role: "system", content: system_prompt},
          %{role: "user", content: prompt_text}
        ]
      ) do
        {:ok, evaluation} -> {:ok, evaluation}
        {:error, error} -> {:error, "Factuality evaluation failed: #{inspect(error)}"}
      end
    rescue
      e -> {:error, "Factuality evaluation failed with exception: #{inspect(e)}"}
    end
  end
end

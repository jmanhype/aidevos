defmodule Realworld.DurableObjects.RewardModeling.ConstraintChecker do
  @moduledoc """
  Evaluates whether generated code meets defined constraints.
  
  This module checks if the generated code:
  - Follows the specified architecture
  - Adheres to project-specific constraints
  - Meets security requirements
  - Follows performance guidelines
  """
  
  alias Realworld.DurableObjects.Instructor.CodeGeneration
  alias Realworld.DurableObjects.Instructor.ConstraintCheck
  
  @doc """
  Evaluates whether generated code meets defined constraints.
  
  ## Parameters
  
  - name: Name of the object being created
  - description: Description of the object's purpose
  - generation: The CodeGeneration struct with generated code
  
  ## Returns
  
  `{:ok, %{score: float, feedback: string}}` if successful, `{:error, reason}` otherwise
  """
  def evaluate(name, description, %CodeGeneration{} = generation) do
    system_prompt = """
    You are an expert Elixir code reviewer focused on constraint validation.
    Your task is to evaluate whether the generated code meets the defined constraints.
    
    Constraints may include:
    1. Architecture requirements - following a specific architectural pattern
    2. Security requirements - proper authentication, authorization, input validation
    3. Performance guidelines - efficient algorithms, proper resource usage
    4. Code style - following Elixir best practices and conventions
    5. Error handling - proper error handling and reporting
    6. Testing - proper test coverage
    
    Provide a score from 0.0 to 1.0 where:
    - 0.0-0.3: Major constraint violations that make the code unusable
    - 0.4-0.6: Some constraint violations that need significant correction
    - 0.7-0.8: Minor constraint violations that need minor correction
    - 0.9-1.0: No significant constraint violations, code meets all constraints
    
    Also provide detailed feedback on any constraint violations found and how to correct them.
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
    
    Please evaluate whether this generated code meets the defined constraints.
    Be thorough in your analysis and look for any issues that would affect the code's compliance.
    """
    
    try do
      case Instructor.chat_completion(
        model: "gpt-4-turbo",
        response_model: ConstraintCheck,
        messages: [
          %{role: "system", content: system_prompt},
          %{role: "user", content: prompt_text}
        ]
      ) do
        {:ok, evaluation} -> {:ok, evaluation}
        {:error, error} -> {:error, "Constraint evaluation failed: #{inspect(error)}"}
      end
    rescue
      e -> {:error, "Constraint evaluation failed with exception: #{inspect(e)}"}
    end
  end
end

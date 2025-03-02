defmodule Realworld.DurableObjects.RewardModeling.PreferenceEvaluator do
  @moduledoc """
  Evaluates whether generated code meets user preferences.
  
  This module checks if the generated code:
  - Follows best practices for code style and organization
  - Is well-documented and readable
  - Provides a good developer experience
  - Meets the user's stated requirements
  """
  
  alias Realworld.DurableObjects.Instructor.CodeGeneration
  alias Realworld.DurableObjects.Instructor.PreferenceEvaluation
  
  @doc """
  Evaluates whether generated code meets user preferences.
  
  ## Parameters
  
  - name: Name of the object being created
  - description: Description of the object's purpose
  - generation: The CodeGeneration struct with generated code
  
  ## Returns
  
  `{:ok, %{score: float, feedback: string}}` if successful, `{:error, reason}` otherwise
  """
  def evaluate(name, description, %CodeGeneration{} = generation) do
    system_prompt = """
    You are an expert Elixir code reviewer focused on user preferences and code quality.
    Your task is to evaluate whether the generated code meets user preferences and quality standards.
    
    User preferences and quality standards include:
    1. Code readability - clear, concise, and well-organized code
    2. Documentation - comprehensive and accurate documentation
    3. Developer experience - intuitive APIs and error messages
    4. Maintainability - modular design and separation of concerns
    5. Testability - code that is easy to test
    6. Performance - efficient algorithms and resource usage
    
    Provide a score from 0.0 to 1.0 where:
    - 0.0-0.3: Major quality issues that make the code difficult to use or maintain
    - 0.4-0.6: Some quality issues that need significant improvement
    - 0.7-0.8: Minor quality issues that need minor improvement
    - 0.9-1.0: No significant quality issues, code meets high quality standards
    
    Also provide detailed feedback on any quality issues found and how to improve them.
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
    
    Please evaluate whether this generated code meets user preferences and quality standards.
    Be thorough in your analysis and look for any issues that would affect the code's quality.
    """
    
    try do
      case Instructor.chat_completion(
        model: "gpt-4-turbo",
        response_model: PreferenceEvaluation,
        messages: [
          %{role: "system", content: system_prompt},
          %{role: "user", content: prompt_text}
        ]
      ) do
        {:ok, evaluation} -> {:ok, evaluation}
        {:error, error} -> {:error, "Preference evaluation failed: #{inspect(error)}"}
      end
    rescue
      e -> {:error, "Preference evaluation failed with exception: #{inspect(e)}"}
    end
  end
end

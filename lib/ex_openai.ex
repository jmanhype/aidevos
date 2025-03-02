defmodule ExOpenAI do
  @moduledoc """
  A client for interacting with the OpenAI API.
  """
  use Application
  
  @doc """
  Starts the ExOpenAI application.
  Required by OTP applications.
  """
  def start(_type, _args) do
    # Simply return a successful supervisor tree start
    {:ok, self()}
  end
  
  @doc """
  Sends chat completion requests to OpenAI's API.
  
  ## Parameters
  
  - options: Map of options including model, messages, temperature, etc.
  
  ## Returns
  
  - `{:ok, response}` on success
  - `{:error, reason}` on failure
  
  ## Examples
  
      ExOpenAI.chat_completions(%{
        model: "gpt-4",
        messages: [
          %{role: "system", content: "You are a helpful assistant."},
          %{role: "user", content: "Hello!"}
        ],
        temperature: 0.7
      })
  """
  def chat_completions(options) do
    api_key = System.get_env("OPENAI_API_KEY")
    
    if is_nil(api_key) or api_key == "" do
      {:error, "No OpenAI API key found in environment variable OPENAI_API_KEY"}
    else
      url = "https://api.openai.com/v1/chat/completions"
      
      headers = [
        {"Authorization", "Bearer #{api_key}"},
        {"Content-Type", "application/json"}
      ]
      
      # Convert the options map to JSON
      {:ok, body} = Jason.encode(options)
      
      # Use a longer timeout (120 seconds) for complex code generation
      case HTTPoison.post(url, body, headers, [timeout: 120_000, recv_timeout: 120_000]) do
        {:ok, %HTTPoison.Response{status_code: 200, body: response_body}} ->
          case Jason.decode(response_body) do
            {:ok, decoded} ->
              {:ok, decoded}
            {:error, error} ->
              {:error, "Failed to parse OpenAI response: #{inspect(error)}"}
          end
        
        {:ok, %HTTPoison.Response{status_code: status_code, body: response_body}} ->
          case Jason.decode(response_body) do
            {:ok, decoded} ->
              error_message = decoded["error"]["message"] || "Unknown error"
              {:error, "OpenAI API error (#{status_code}): #{error_message}"}
            {:error, _} ->
              {:error, "OpenAI API error (#{status_code}): #{response_body}"}
          end
        
        {:error, %HTTPoison.Error{reason: reason}} ->
          {:error, "HTTP request failed: #{inspect(reason)}"}
      end
    end
  end
end

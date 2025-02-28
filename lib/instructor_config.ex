defmodule Realworld.InstructorConfig do
  @moduledoc """
  Configuration module for Instructor.
  
  This module initializes the Instructor library with the OpenAI API key
  from environment variables and sets up any necessary configuration.
  """
  use GenServer
  
  def start_link(_) do
    GenServer.start_link(__MODULE__, [], name: __MODULE__)
  end
  
  @impl true
  def init(_) do
    api_key = System.get_env("OPENAI_API_KEY")
    
    if api_key do
      # Configure Instructor via Application environment
      # This is how the library expects to be configured based on its source code
      Application.put_env(:instructor, :openai, [api_key: api_key])
      {:ok, %{api_key: "configured"}}
    else
      # Log a warning but still start the GenServer
      IO.puts("WARNING: OPENAI_API_KEY environment variable not set. Instructor may not work properly.")
      {:ok, %{api_key: nil}}
    end
  end
end

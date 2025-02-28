defmodule Realworld.DurableObjects do
  @moduledoc """
  The DurableObjects context provides functions for creating, modifying, deploying,
  and managing Durable Objects.
  """
  
  alias Realworld.DurableObjects.Object
  
  @doc """
  Lists all durable objects.
  """
  def list_objects do
    Ash.read!(Object, :read)
  end
  
  @doc """
  Gets a durable object by ID.
  
  Returns nil if the object does not exist.
  """
  def get_object(id) do
    case Ash.get(Object, id) do
      %Object{} = object -> object
      nil -> nil
    end
  rescue
    _ -> nil
  end
  
  @doc """
  Creates a new durable object.
  
  ## Parameters
  
  - params: Map of object properties
  
  ## Returns
  
  `{:ok, object}` on success, `{:error, changeset}` on failure
  """
  def create_object(params) do
    Ash.create(Object, params)
  end
  
  @doc """
  Updates a durable object with the given params.
  
  ## Parameters
  
  - object: The object to update
  - params: Map of properties to update
  
  ## Returns
  
  `{:ok, object}` on success, `{:error, changeset}` on failure
  """
  def update_object(object, params) do
    Ash.update(object, params)
  end
  
  @doc """
  Modifies a durable object using AI.
  
  ## Parameters
  
  - object: The object to modify
  - prompt: The prompt describing the desired modifications
  
  ## Returns
  
  `{:ok, object}` on success, `{:error, reason}` on failure
  """
  def modify_object(object, prompt) do
    Ash.update(object, :modify, %{prompt: prompt})
  end
  
  @doc """
  Deploys a durable object to the specified environment.
  
  ## Parameters
  
  - object: The object to deploy
  - environment: The target environment (e.g., "development", "production")
  
  ## Returns
  
  `{:ok, object}` on success, `{:error, reason}` on failure
  """
  def deploy_object(object, environment) do
    Ash.update(object, :deploy, %{environment: environment})
  end
  
  @doc """
  Rolls back a durable object to a previous version.
  
  ## Parameters
  
  - object: The object to roll back
  - version: The version to roll back to
  
  ## Returns
  
  `{:ok, object}` on success, `{:error, reason}` on failure
  """
  def rollback_object(object, version) do
    Ash.update(object, :rollback, %{version: version})
  end
end

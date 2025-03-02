defmodule Realworld.DurableObjects do
  @moduledoc """
  The DurableObjects context provides functions for creating, modifying, deploying,
  and managing Durable Objects.
  """
  
  alias Realworld.DurableObjects.Object
  alias Realworld.DurableObjects.Changes.CreateObject
  
  @doc """
  Lists all durable objects.
  """
  def list_objects do
    Ash.read!(Object, [])
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
  Creates a new durable object from scratch using AI.
  
  ## Parameters
  
  - name: Name of the object to create
  - description: Description of the object's purpose
  - prompt: Detailed requirements for the object
  
  ## Returns
  
  `{:ok, object}` on success, `{:error, reason}` on failure
  """
  def create_object_from_scratch(name, description, prompt) do
    case CreateObject.create(name, description, prompt) do
      {:ok, creation_result} ->
        # Convert structs to maps for JSON encoding
        creation_plan_map = if is_struct(creation_result.creation_plan) do
          Map.from_struct(creation_result.creation_plan)
        else
          creation_result.creation_plan
        end
        
        file_structure_map = if is_list(creation_result.file_structure) do
          Enum.map(creation_result.file_structure, fn item ->
            if is_struct(item), do: Map.from_struct(item), else: item
          end)
        else
          creation_result.file_structure
        end
        
        dependencies = creation_result.dependencies || []
        
        # Create the object in the database
        Ash.create(Object, %{
          name: name,
          description: description,
          code_content: creation_result.code_content,
          api_schema: creation_result.api_schema,
          version: 1,
          status: "draft",
          file_paths: creation_result.file_paths,
          creation_plan: Jason.encode!(creation_plan_map),
          file_structure: Jason.encode!(file_structure_map),
          dependencies: Jason.encode!(dependencies)
        })
      
      {:error, reason} ->
        {:error, reason}
    end
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

  @doc """
  Activates a draft object, changing its status to "active".
  
  ## Parameters
  
  - object: The object to activate (must be in "draft" status)
  
  ## Returns
  
  `{:ok, object}` on success, `{:error, reason}` on failure
  """
  def activate_object(object) do
    if object.status == "draft" do
      update_object(object, %{status: "active"})
    else
      {:error, "Object is not in draft status"}
    end
  end
  
  @doc """
  Activates a draft object by its name.
  
  ## Parameters
  
  - name: Name of the object to activate
  - opts: Additional options
  
  ## Returns
  
  `{:ok, object}` on success, `{:error, reason}` on failure
  """
  def activate_object_by_name(name, _opts \\ []) do
    # Find the object by name
    objects = Ash.read!(Object, filter: [name: [equals: name]])
    
    case objects do
      [object | _] ->
        # Activate the found object
        activate_object(object)
      
      [] ->
        {:error, "Object not found with name: #{name}"}
    end
  end
end

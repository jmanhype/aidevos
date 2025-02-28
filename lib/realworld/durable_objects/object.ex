defmodule Realworld.DurableObjects.Object do
  use Ash.Resource,
    domain: Realworld.DurableObjects.Registry,
    data_layer: AshPostgres.DataLayer

  postgres do
    table "durable_objects"
    repo Realworld.Repo
  end

  attributes do
    uuid_primary_key :id

    attribute :name, :string do
      allow_nil? false
      constraints [min_length: 2, max_length: 255]
    end

    attribute :description, :string do
      constraints [max_length: 1000]
    end

    attribute :code_content, :string do
      allow_nil? false
    end

    attribute :api_schema, :string, default: ""

    attribute :version, :integer, default: 1
    attribute :status, :string, default: "draft"
    attribute :last_modified, :utc_datetime, default: &DateTime.utc_now/0
    
    attribute :modification_history, {:array, :map}, default: []
    attribute :deployment_history, {:array, :map}, default: []
    attribute :rollback_history, {:array, :map}, default: []
  end

  actions do
    defaults [:create, :read, :update, :destroy]
    
    # Modified by AI action
    update :modify do
      require_atomic? false
      
      argument :prompt, :string do
        allow_nil? false
      end
      
      argument :options, :map, default: %{}
      
      change fn changeset, args -> modify_with_ai(changeset, args) end
    end
    
    # Deploy object to environment
    update :deploy do
      require_atomic? false
      
      argument :environment, :string do
        allow_nil? false
      end
      
      change fn changeset, args -> 
        if args.environment in ["development", "testing", "staging", "production"] do
          deploy_object(changeset, args)
        else
          Ash.Changeset.add_error(
            changeset, 
            :environment, 
            "must be one of: development, testing, staging, production"
          )
        end
      end
    end
    
    # Rollback to previous version
    update :rollback do
      require_atomic? false
      
      argument :version, :integer do
        allow_nil? false
      end
      
      change fn changeset, args -> rollback_object(changeset, args) end
    end
  end
  
  defp modify_with_ai(changeset, %{prompt: prompt, options: _options}) do
    object = changeset.data
    
    case Realworld.DurableObjects.Changes.ModifyCode.modify(object, prompt) do
      {:ok, modification} ->
        history_entry = %{
          timestamp: DateTime.utc_now(),
          prompt: prompt,
          previous_version: object.version,
          summary: modification.modification_summary
        }
        
        Ash.Changeset.change_attributes(changeset, %{
          code_content: modification.modified_code,
          version: object.version + 1,
          last_modified: DateTime.utc_now(),
          modification_history: [history_entry | object.modification_history]
        })
        
      {:error, reason} ->
        Ash.Changeset.add_error(changeset, :code_content, reason)
    end
  end
  
  defp deploy_object(changeset, %{environment: environment}) do
    object = changeset.data
    
    case Realworld.DurableObjects.Changes.DeployObject.deploy(object, environment) do
      {:ok, updated_object} ->
        Ash.Changeset.change_attributes(changeset, %{
          status: updated_object.status,
          deployment_history: updated_object.deployment_history
        })
        
      {:error, updated_object, reason} ->
        changeset
        |> Ash.Changeset.change_attributes(%{
          status: updated_object.status,
          deployment_history: updated_object.deployment_history
        })
        |> Ash.Changeset.add_error(:deployment, reason)
    end
  end
  
  defp rollback_object(changeset, %{version: version}) do
    object = changeset.data
    
    case Realworld.DurableObjects.Changes.RollbackObject.rollback(object, version) do
      {:ok, updated_object} ->
        Ash.Changeset.change_attributes(changeset, %{
          code_content: updated_object.code_content,
          version: updated_object.version,
          status: updated_object.status,
          rollback_history: updated_object.rollback_history
        })
        
      {:error, _object, reason} ->
        Ash.Changeset.add_error(changeset, :rollback, reason)
    end
  end
end

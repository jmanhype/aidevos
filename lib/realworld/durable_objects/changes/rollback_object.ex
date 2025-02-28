defmodule Realworld.DurableObjects.Changes.RollbackObject do
  @moduledoc """
  Handles rolling back a Durable Object to a previous version.
  This process includes:
  1. Retrieving the historical version data
  2. Validating that the historical code can still be loaded
  3. Updating the object to the historical version
  4. Recording the rollback operation in history
  """
  
  def rollback(object, target_version) do
    # Validate target version
    cond do
      # Can't roll back to a future version
      target_version > object.version ->
        {:error, object, "Cannot roll back to a future version"}
        
      # No need to roll back to current version
      target_version == object.version ->
        {:error, object, "Already at version #{target_version}"}
        
      # Valid rollback target
      true ->
        # Find historical version data
        case find_historical_version(object, target_version) do
          {:ok, historical_data} ->
            # Validate the historical code
            case validate_historical_code(historical_data.code_content) do
              :ok ->
                rollback_record = %{
                  timestamp: DateTime.utc_now(),
                  from_version: object.version,
                  to_version: target_version,
                  reason: "Manual rollback"
                }
                
                # Create updated object
                updated_object = 
                  object
                  |> Map.put(:code_content, historical_data.code_content)
                  |> Map.put(:version, target_version)
                  |> Map.put(:status, "rolled_back")
                  |> Map.update(:rollback_history, [rollback_record], fn history -> [rollback_record | history] end)
                
                {:ok, updated_object}
                
              {:error, reason} ->
                {:error, object, "Historical code validation failed: #{reason}"}
            end
            
          {:error, reason} ->
            {:error, object, reason}
        end
    end
  end
  
  defp find_historical_version(object, target_version) do
    # In a real implementation, this would retrieve the historical version from the database
    # For this simplified implementation, we'll simulate finding the version in the object's history
    
    # Check if we have modification history
    if object.modification_history && length(object.modification_history) > 0 do
      # Find the entry for the target version
      target_entry = Enum.find(object.modification_history, fn entry -> 
        entry.previous_version + 1 == target_version
      end)
      
      if target_entry do
        {:ok, %{
          code_content: object.code_content, # In a real impl, this would be the historical code
          version: target_version
        }}
      else
        {:error, "Version #{target_version} not found in history"}
      end
    else
      {:error, "No modification history available"}
    end
  end
  
  defp validate_historical_code(code_content) do
    try do
      {_result, _bindings} = Code.eval_string("""
        defmodule TempRollbackModule do
          #{code_content}
        end
      """)
      
      # Clean up
      :code.purge(TempRollbackModule)
      :code.delete(TempRollbackModule)
      
      :ok
    rescue
      error -> {:error, Exception.message(error)}
    end
  end
end

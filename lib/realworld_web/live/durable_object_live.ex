defmodule RealworldWeb.DurableObjectLive do
  use RealworldWeb, :live_view
  alias Realworld.DurableObjects

  @impl true
  def mount(_params, _session, socket) do
    objects = list_objects()
    
    # Preload the first object if available
    selected_object = if length(objects) > 0, do: List.first(objects), else: nil
    
    {:ok, assign(socket, 
      objects: objects,
      page_title: "Durable Objects",
      selected_object: selected_object,
      form_visible: false,
      form_type: nil,
      creating_from_scratch: false,
      creation_status: nil,
      execution_result: nil
    )}
  end

  @impl true
  def handle_params(%{"id" => id}, _uri, socket) do
    case get_object(id) do
      nil ->
        {:noreply, push_navigate(socket, to: ~p"/durable-objects")}
      object ->
        {:noreply, assign(socket, selected_object: object)}
    end
  end
  
  def handle_params(_params, _uri, socket) do
    {:noreply, assign(socket, selected_object: nil)}
  end

  @impl true
  def handle_event("new_object", _params, socket) do
    {:noreply, assign(socket, form_visible: true, form_type: :new)}
  end
  
  def handle_event("new_object_from_scratch", _params, socket) do
    {:noreply, assign(socket, form_visible: true, form_type: :new_from_scratch)}
  end
  
  def handle_event("select_object", %{"id" => id}, socket) do
    IO.puts("Selecting object with ID: #{id}")
    
    # Get all objects to verify the ID exists
    all_objects = list_objects()
    IO.puts("Available objects: #{inspect(Enum.map(all_objects, fn obj -> {obj.id, obj.name} end))}")
    
    case get_object(id) do
      nil ->
        IO.puts("Object not found with ID: #{id}")
        {:noreply, put_flash(socket, :error, "Object not found")}
      object ->
        IO.puts("Object found: #{inspect(object.name)}")
        {:noreply, assign(socket, selected_object: object)}
    end
  end
  
  def handle_event("create_object", %{"object" => object_params}, socket) do
    case create_object(object_params) do
      {:ok, object} ->
        {:noreply, 
          socket
          |> assign(objects: list_objects(), form_visible: false)
          |> put_flash(:info, "Object #{object.name} created successfully!")
        }
      
      {:error, changeset} ->
        {:noreply, 
          socket
          |> assign(changeset: changeset)
          |> put_flash(:error, "Failed to create object. Please check the errors.")
        }
    end
  end
  
  def handle_event("create_object_from_scratch", %{"object" => params}, socket) do
    name = params["name"]
    description = params["description"]
    prompt = params["prompt"]
    
    # Start async task to create the object
    task = Task.async(fn ->
      case create_object_from_scratch(name, description, prompt) do
        {:ok, object} -> {:ok, object}
        {:error, reason} -> {:error, reason}
      end
    end)
    
    # Return with updated socket
    {:noreply, 
      socket
      |> assign(
        creating_from_scratch: true, 
        creation_status: "Planning object creation...",
        form_visible: false
      )
    }
  end
  
  def handle_event("execute_object", %{"id" => id}, socket) do
    case get_object(id) do
      nil ->
        {:noreply, put_flash(socket, :error, "Object not found")}
      object ->
        result = execute_object_code(object.code_content)
        {:noreply, assign(socket, execution_result: result)}
    end
  end
  
  @impl true
  def handle_info({ref, {:ok, object}}, socket) when is_reference(ref) do
    # Flush the DOWN message
    Process.demonitor(ref, [:flush])
    
    {:noreply,
      socket
      |> assign(
        creating_from_scratch: false,
        creation_status: nil,
        objects: list_objects()
      )
      |> put_flash(:info, "Object #{object.name} created successfully from scratch!")
    }
  end
  
  def handle_info({ref, {:error, reason}}, socket) when is_reference(ref) do
    # Flush the DOWN message
    Process.demonitor(ref, [:flush])
    
    {:noreply,
      socket
      |> assign(
        creating_from_scratch: false,
        creation_status: nil
      )
      |> put_flash(:error, "Failed to create object from scratch: #{reason}")
    }
  end
  
  # Handle the DOWN message in case the task crashes
  def handle_info({:DOWN, _ref, :process, _pid, reason}, socket) do
    {:noreply,
      socket
      |> assign(
        creating_from_scratch: false,
        creation_status: nil
      )
      |> put_flash(:error, "Creation process crashed: #{inspect(reason)}")
    }
  end
  
  def handle_event("cancel_form", _params, socket) do
    {:noreply, assign(socket, form_visible: false)}
  end
  
  def handle_event("modify_object", _params, socket) do
    {:noreply, assign(socket, form_visible: true, form_type: :modify)}
  end
  
  def handle_event("submit_modification", %{"modification" => %{"prompt" => prompt}}, socket) do
    object = socket.assigns.selected_object
    
    case modify_object(object, prompt) do
      {:ok, updated_object} ->
        {:noreply, 
          socket
          |> assign(
            selected_object: updated_object, 
            objects: list_objects(), 
            form_visible: false
          )
          |> put_flash(:info, "Object modified successfully!")
        }
      
      {:error, reason} ->
        {:noreply, 
          socket
          |> put_flash(:error, "Failed to modify object: #{reason}")
        }
    end
  end
  
  def handle_event("deploy_object", %{"environment" => environment}, socket) do
    object = socket.assigns.selected_object
    
    case deploy_object(object, environment) do
      {:ok, updated_object} ->
        {:noreply,
          socket
          |> assign(
            selected_object: updated_object,
            objects: list_objects()
          )
          |> put_flash(:info, "Object deployed to #{environment} successfully!")
        }
      
      {:error, reason} ->
        {:noreply,
          socket
          |> put_flash(:error, "Deployment failed: #{reason}")
        }
    end
  end
  
  def handle_event("rollback_object", %{"version" => version}, socket) do
    {version, _} = Integer.parse(version)
    object = socket.assigns.selected_object
    
    case rollback_object(object, version) do
      {:ok, updated_object} ->
        {:noreply,
          socket
          |> assign(
            selected_object: updated_object,
            objects: list_objects()
          )
          |> put_flash(:info, "Object rolled back to version #{version} successfully!")
        }
      
      {:error, reason} ->
        {:noreply,
          socket
          |> put_flash(:error, "Rollback failed: #{reason}")
        }
    end
  end
  
  def handle_event("activate_object", _params, socket) do
    object = socket.assigns.selected_object
    
    case activate_object(object) do
      {:ok, updated_object} ->
        {:noreply,
          socket
          |> assign(
            selected_object: updated_object,
            objects: list_objects()
          )
          |> put_flash(:info, "Object activated successfully!")
        }
      
      {:error, reason} ->
        {:noreply,
          socket
          |> put_flash(:error, "Activation failed: #{reason}")
        }
    end
  end
  
  # Helper functions for the UI
  
  def status_class(status) do
    case status do
      "deployed" -> "bg-green-100 text-green-800"
      "draft" -> "bg-gray-100 text-gray-800"
      "failed" -> "bg-red-100 text-red-800"
      _ -> "bg-gray-100 text-gray-800"
    end
  end
  
  # Helper functions to interact with the Durable Objects API
  
  defp list_objects do
    DurableObjects.list_objects()
  end
  
  defp get_object(id) do
    IO.puts("Fetching object with ID: #{id}")
    
    # Try to get the object directly
    case DurableObjects.get_object(id) do
      %Realworld.DurableObjects.Object{} = object -> 
        IO.puts("Found object: #{object.name}")
        object
      nil -> 
        IO.puts("Object not found in database")
        # As a fallback, try to find it in the list of objects
        all_objects = list_objects()
        Enum.find(all_objects, fn obj -> obj.id == id end)
    end
  end
  
  defp create_object(params) do
    DurableObjects.create_object(params)
  end
  
  defp create_object_from_scratch(name, description, prompt) do
    DurableObjects.create_object_from_scratch(name, description, prompt)
  end
  
  defp modify_object(object, prompt) do
    DurableObjects.modify_object(object, prompt)
  end
  
  defp deploy_object(object, environment) do
    DurableObjects.deploy_object(object, environment)
  end
  
  defp rollback_object(object, version) do
    DurableObjects.rollback_object(object, version)
  end
  
  defp activate_object(object) do
    DurableObjects.activate_object(object)
  end
  
  defp execute_object_code(code_content) do
    try do
      {result, _} = Code.eval_string(code_content)
      
      # Capture any IO output
      output = ExUnit.CaptureIO.capture_io(fn ->
        Code.eval_string(code_content)
      end)
      
      if output && output != "" do
        output
      else
        inspect(result)
      end
    rescue
      e -> "Error: #{inspect(e)}"
    catch
      kind, reason -> "#{kind}: #{inspect(reason)}"
    end
  end
end

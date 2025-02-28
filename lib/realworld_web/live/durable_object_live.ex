defmodule RealworldWeb.DurableObjectLive do
  use RealworldWeb, :live_view
  alias Realworld.DurableObjects

  @impl true
  def mount(_params, _session, socket) do
    objects = list_objects()
    
    {:ok, assign(socket, 
      objects: objects,
      page_title: "Durable Objects",
      selected_object: nil,
      form_visible: false,
      form_type: nil
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
    DurableObjects.get_object(id)
  end
  
  defp create_object(params) do
    DurableObjects.create_object(params)
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
end

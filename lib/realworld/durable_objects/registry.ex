defmodule Realworld.DurableObjects.Registry do
  use Ash.Domain

  resources do
    resource Realworld.DurableObjects.Object
  end
end

defmodule Realworld.Accounts do
  use Ash.Domain, otp_app: :realworld

  authorization do
    authorize :by_default
  end

  resources do
    resource Realworld.Accounts.Token

    resource Realworld.Accounts.User
  end
  
  @doc """
  Lists all users in the system.
  
  ## Returns
  
  List of User structs
  """
  def list_users do
    Ash.read!(Realworld.Accounts.User, [])
  end
  
  @doc """
  Counts the total number of users in the system.
  
  ## Returns
  
  Integer count of users
  """
  def count_users do
    length(list_users())
  end
end

defmodule Realworld.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    # Configure ExTwilio
    Application.put_env(:ex_twilio, :account_sid, System.get_env("TWILIO_ACCOUNT_SID"))
    Application.put_env(:ex_twilio, :auth_token, System.get_env("TWILIO_AUTH_TOKEN"))
    
    children = [
      # Start the Telemetry supervisor
      RealworldWeb.Telemetry,
      # Start the PubSub system
      {Phoenix.PubSub, name: Realworld.PubSub},
      # Start the Endpoint (http/https)
      RealworldWeb.Endpoint,
      # Start a worker by calling: Realworld.Worker.start_link(arg)
      # {Realworld.Worker, arg}
      Realworld.Repo,
      {AshAuthentication.Supervisor, otp_app: :realworld},
      # Start the Instructor configuration process
      Realworld.InstructorConfig,
      # Start the VoiceCallsETS GenServer
      Realworld.VoiceCallsETS
    ]

    # See https://hexdocs.pm/elixir/Supervisor.html
    # for other strategies and supported options
    opts = [strategy: :one_for_one, name: Realworld.Supervisor]
    Supervisor.start_link(children, opts)
  end

  # Tell Phoenix to update the endpoint configuration
  # whenever the application is updated.
  @impl true
  def config_change(changed, _new, removed) do
    RealworldWeb.Endpoint.config_change(changed, removed)
    :ok
  end
end

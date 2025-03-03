# This file is responsible for configuring your application
# and its dependencies with the aid of the Config module.
#
# This configuration file is loaded before any dependency and
# is restricted to this project.

# General application configuration
import Config

# Configures the endpoint
config :realworld, RealworldWeb.Endpoint,
  url: [host: "localhost"],
  render_errors: [view: RealworldWeb.ErrorView, accepts: ~w(html json), layout: false],
  pubsub_server: Realworld.PubSub,
  live_view: [signing_salt: "WoMwX3/2"]

# Configures the mailer
#
# By default it uses the "Local" adapter which stores the emails
# locally. You can see the emails in your browser, at "/dev/mailbox".
#
# For production it's recommended to configure a different adapter
# at the `config/runtime.exs`.
config :realworld, Realworld.Mailer,
  adapter: Bamboo.TestAdapter,
  from_email: System.get_env("FROM_EMAIL") || "noreply@example.com"

# Swoosh API client is needed for adapters other than SMTP.
config :swoosh, :api_client, false

# Configure external service integrations
config :realworld, :twilio,
  account_sid: System.get_env("TWILIO_ACCOUNT_SID"),
  auth_token: System.get_env("TWILIO_AUTH_TOKEN"),
  phone_number: System.get_env("TWILIO_PHONE_NUMBER")

config :realworld, :slack,
  bot_token: System.get_env("SLACK_BOT_TOKEN"),
  test_channel: System.get_env("SLACK_TEST_CHANNEL")

config :realworld, :github,
  token: System.get_env("GITHUB_TOKEN"),
  repo: System.get_env("GITHUB_REPO"),
  test_issue: System.get_env("GITHUB_TEST_ISSUE")

config :realworld, :test_accounts,
  phone: System.get_env("TEST_PHONE_NUMBER"),
  email: System.get_env("TEST_EMAIL"),
  cli_user: System.get_env("AUTODEV_USER")

# Configure ex_twilio
config :ex_twilio,
  account_sid: System.get_env("TWILIO_ACCOUNT_SID"),
  auth_token: System.get_env("TWILIO_AUTH_TOKEN")

# Configure esbuild (the version is required)
config :esbuild,
  version: "0.14.29",
  default: [
    args:
      ~w(js/app.js --bundle --target=es2017 --outdir=../priv/static/assets --external:/fonts/* --external:/images/*),
    cd: Path.expand("../assets", __DIR__),
    env: %{"NODE_PATH" => Path.expand("../deps", __DIR__)}
  ]

# Configures Elixir's Logger
config :logger, :console,
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id]

# Use Jason for JSON parsing in Phoenix
config :phoenix, :json_library, Jason

config :realworld, :ash_domains, [Realworld.Accounts, Realworld.Articles, Realworld.Profiles, Realworld.DurableObjects.Registry, Realworld.AutoDev]

config :realworld, ecto_repos: [Realworld.Repo]

config :realworld,
  token_signing_secret: System.get_env("TOKEN_SIGNING_SECRET") || "REPLACE_IN_PRODUCTION_WITH_SECURE_SECRET"

config :realworld, :twilio,
  account_sid: System.get_env("TWILIO_ACCOUNT_SID"),
  auth_token: System.get_env("TWILIO_AUTH_TOKEN"),
  phone_number: System.get_env("TWILIO_PHONE_NUMBER")

config :realworld, :slack,
  bot_token: System.get_env("SLACK_BOT_TOKEN"),
  test_channel: System.get_env("SLACK_TEST_CHANNEL")

config :realworld, :github,
  token: System.get_env("GITHUB_TOKEN"),
  repo: System.get_env("GITHUB_REPO"),
  test_issue: System.get_env("GITHUB_TEST_ISSUE")

config :realworld, :test_accounts,
  phone: System.get_env("TEST_PHONE_NUMBER"),
  email: System.get_env("TEST_EMAIL"),
  cli_user: System.get_env("AUTODEV_USER")

# Import environment specific config. This must remain at the bottom
# of this file so it overrides the configuration defined above.
import_config "#{config_env()}.exs"

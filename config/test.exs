import Config

# We don't run a server during test. If one is required,
# you can enable the server option below.
config :realworld, RealworldWeb.Endpoint,
  http: [ip: {127, 0, 0, 1}, port: 4002],
  secret_key_base: "jAJcw6eSIxJXZkGZFsHQDmRlA/Yw9+NkXwpKm/9Oc/Ub8FnXRFEDVPuqgSUGBBcL",
  server: false

# In test we don't send emails.
config :realworld, Realworld.Mailer, 
  adapter: Bamboo.TestAdapter,
  from_email: System.get_env("FROM_EMAIL") || "noreply@example.com"

# Print only warnings and errors during test
config :logger, level: :warning

# Initialize plugs at runtime for faster test compilation
config :phoenix, :plug_init_mode, :runtime

# Configure the database for test
config :realworld, Realworld.Repo,
  username: "speed",
  password: "",
  hostname: "localhost",
  database: "realworld_test#{System.get_env("MIX_TEST_PARTITION")}",
  pool: Ecto.Adapters.SQL.Sandbox,
  pool_size: 10

# Configure external service test settings
config :ex_twilio,
  account_sid: System.get_env("TWILIO_ACCOUNT_SID"),
  auth_token: System.get_env("TWILIO_AUTH_TOKEN")

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

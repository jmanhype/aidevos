# WeatherForecast

## Installation
1. Add WeatherForecast to your list of dependencies in `mix.exs`:
```elixir
{:weather_forecast, "~> 0.1.0"}
```
2. Run `mix deps.get`

## Configuration
Ensure you have set the `WEATHER_API_KEY` environment variable to your API key for the weather service.

## Architecture

```mermaid
flowchart TD
    A[Client Application] --> B[WeatherForecast Module]
    B --> C[HTTP Client]
    C --> D[Weather API]
    D --> C
    C --> B
    B --> E[Response Parser]
    E --> B
    B --> A
    
    F[Environment Variables] --> B
    F --> F1[WEATHER_API_KEY]
```

## Usage
To fetch the weather forecast for a city:
```elixir
WeatherForecast.fetch_forecast("New York")
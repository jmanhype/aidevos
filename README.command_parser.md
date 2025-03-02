# Command Parser Architecture

This document explains the architecture and implementation of the command parsing system used in the Autonomous Development System.

## Overview

The Command Parser is a crucial component that translates natural language commands (from voice calls, SMS, or text input) into structured command objects that can be processed by the system. It uses a combination of pattern matching, keyword extraction, and context analysis to understand user intent.

## Architecture

The Command Parser is implemented in the `Realworld.VoiceCommands.CommandParser` module and consists of the following components:

1. **Input Normalization**: Cleans and standardizes the input text for consistent parsing
2. **Intent Recognition**: Identifies the primary intent of the command
3. **Parameter Extraction**: Extracts relevant parameters from the command
4. **Command Object Creation**: Creates a structured command object based on the intent and parameters

## Command Types

The parser recognizes several types of commands, each represented by a specific command struct:

1. **CreateCommand**: For creating new objects
   ```elixir
   %CreateCommand{name: "WeatherWidget", description: "A widget that displays weather information"}
   ```

2. **ModifyCommand**: For modifying existing objects
   ```elixir
   %ModifyCommand{name: "WeatherWidget", modification: "Add support for displaying the 5-day forecast"}
   ```

3. **MonitorCommand**: For setting up event monitoring
   ```elixir
   %MonitorCommand{event: "user_signup", notification_method: "call"}
   ```

4. **InfoCommand**: For retrieving information about objects
   ```elixir
   %InfoCommand{name: "WeatherWidget"}
   ```

5. **ListCommand**: For listing objects or users
   ```elixir
   %ListCommand{type: "objects"}
   ```

6. **CountCommand**: For counting objects or users
   ```elixir
   %CountCommand{type: "objects"}
   ```

## Parsing Process

The parsing process follows these steps:

1. **Normalize Text**: Convert to lowercase, trim whitespace, and standardize formatting
2. **Identify Command Type**: Analyze the text to determine the command type
3. **Extract Parameters**: Extract relevant parameters based on the command type
4. **Validate Command**: Ensure the command has all required parameters
5. **Create Command Object**: Create a structured command object for processing

## Implementation

The main parsing function is `parse/1`, which takes a string input and returns a command object:

```elixir
def parse(text, opts \\ []) do
  # Normalize text for easier parsing
  normalized_text = text
  |> String.downcase()
  |> String.trim()
  
  # Identify command type and extract parameters
  cond do
    String.starts_with?(normalized_text, "create") ->
      parse_create_command(normalized_text)
      
    String.starts_with?(normalized_text, "modify") ->
      parse_modify_command(normalized_text)
      
    Regex.match?(~r/(call|text|notify) me when/, normalized_text) ->
      parse_monitor_command(normalized_text)
      
    # ... other command types
      
    true ->
      {:error, "Unknown command: #{text}"}
  end
end
```

## Integration with Command Processor

The Command Parser works closely with the Command Processor, which is responsible for executing the parsed commands:

1. The Command Parser converts text into command objects
2. The Command Processor takes these command objects and executes the appropriate actions
3. The result is then communicated back to the user

## Example Usage

```elixir
# Parse a command
command = CommandParser.parse("create WeatherWidget A widget that displays weather information")

# Process the command
result = CommandProcessor.process(command)

# Handle the result
case result do
  {:ok, response} -> 
    # Success
  {:error, reason} -> 
    # Error
end
```

## Extending the Parser

To add support for new command types:

1. Define a new command struct in the appropriate module
2. Add a new condition in the `parse/1` function to recognize the command
3. Implement a parsing function for the new command type
4. Update the Command Processor to handle the new command type

## Error Handling

The parser includes robust error handling to deal with ambiguous or incomplete commands:

1. If a command is ambiguous, the parser may ask for clarification
2. If a command is missing required parameters, an error is returned
3. If a command is not recognized, a helpful error message is provided

## Future Improvements

Planned improvements to the Command Parser include:

1. Enhanced natural language understanding using machine learning
2. Support for more complex command structures
3. Context-aware parsing that remembers previous commands
4. Improved error messages and suggestions for invalid commands

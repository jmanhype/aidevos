# SimpleCalculator

SimpleCalculator is an Elixir module providing basic arithmetic operations. It handles addition, subtraction, multiplication, and division with basic error handling for division by zero.

## Architecture

```mermaid
classDiagram
    class SimpleCalculator {
        +add(a, b)
        +subtract(a, b)
        +multiply(a, b)
        +divide(a, b)
    }
    
    class Result {
        +{:ok, result}
        +{:error, reason}
    }
    
    SimpleCalculator ..> Result : returns
```

## Installation

To use SimpleCalculator in your Mix project, add the following dependency to your `mix.exs` file:

```elixir
{:simple_calculator, "~> 0.1.0"}
```

Then run `mix deps.get`.

## Usage

Here are some examples of how to use the SimpleCalculator:

```elixir
SimpleCalculator.add(1, 2) # Returns 3
SimpleCalculator.subtract(5, 3) # Returns 2
SimpleCalculator.multiply(4, 3) # Returns 12
SimpleCalculator.divide(10, 0) # Returns {:error, 'division by zero'}
SimpleCalculator.divide(10, 2) # Returns {:ok, 5.0}
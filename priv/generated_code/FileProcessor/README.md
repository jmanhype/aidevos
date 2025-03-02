# FileProcessor

A comprehensive Elixir library for processing, validating, and transforming different file formats including CSV, JSON, and XML.

## Architecture

```mermaid
flowchart TD
    A[Client Application] --> B[FileProcessor]
    B --> C{File Type}
    C -->|CSV| D[CSV Processor]
    C -->|JSON| E[JSON Processor]
    C -->|XML| F[XML Processor]
    
    D --> G[Validation]
    E --> G
    F --> G
    
    G --> H[Transformation]
    H --> I[Result]
    I --> A
    
    J[File System] --> B
```

## Installation

Add `file_processor` to your list of dependencies in `mix.exs`:

```elixir
def deps do
  [{:file_processor, "~> 0.1.0"}]
end
```

## Usage

To process a file, call:

```elixir
FileProcessor.process_file("path/to/file.csv", :csv)
```

Supported file types are CSV, JSON, and XML.

## Configuration

No additional configuration is required for basic usage.

## Testing

Run tests with `mix test`.
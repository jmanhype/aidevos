# Self-Modifying Durable Objects with Agentic Reward Modeling

This extension to the RealWorld application demonstrates a system for safely self-modifying code using Ash Framework resources and OpenAI-based reward modeling.

## Key Concepts

### 1. Durable Objects

Durable Objects are persistent, versioned pieces of code that can be modified, deployed, and rolled back. Each object is represented as an Ash Resource with:

- Identifier and metadata
- Code content and optional API schema
- Version history and modification records
- Status tracking (draft, deployed, failed, deprecated)

### 2. Agentic Reward Modeling (ARM)

The Self-Modifying Objects system incorporates ARM to ensure that code modifications align with human preferences and maintain correctness:

- **Human Preference Evaluation**: Measures readability, maintainability, elegance, documentation quality
- **Constraint Checking**: Ensures modifications adhere to constraints in the original code and API schema
- **Factuality Verification**: Validates the correctness of implemented algorithms and domain-specific knowledge

### 3. Safety Mechanisms

Multiple layers of safety are built into the system:

- **Validation Chain**: Every modification passes through planning, generation, and multi-dimensional evaluation
- **Threshold-Based Acceptance**: Modifications are only accepted if they meet configurable quality thresholds
- **Version Control**: Complete history with rollback capabilities
- **Memory-Aware Mutations**: System records all modifications and evaluations for transparency and auditing

## Implementation Details

### Core Components

1. **Object Resource**: Defines the Durable Object structure and relationships
2. **Instructor Models**: Structured inputs and outputs using instructor_ex
3. **Reward Evaluator**: Components that analyze code modifications across different dimensions
4. **Code Modification Pipeline**: Orchestrates the planning, generation, and evaluation steps
5. **Creation Pipeline**: Generates new code and files from scratch based on requirements
6. **Deployment System**: Safely loads and tests modified code
7. **LiveView Interface**: User interface for managing objects and modifications

### Key Files

- `lib/realworld/durable_objects/object.ex`: Core resource definition
- `lib/realworld/durable_objects/models/*.ex`: Structured data models
- `lib/realworld/durable_objects/reward_modeling/*.ex`: Evaluation components
- `lib/realworld/durable_objects/changes/*.ex`: Code mutation, creation, and deployment logic
- `lib/realworld/durable_objects/file_system.ex`: File system integration for code files
- `lib/realworld_web/live/durable_object_live.ex`: Phoenix LiveView 

## Getting Started

### Setup

1. Make sure dependencies are installed:
   ```bash
   mix deps.get
   ```

2. Create and migrate the database:
   ```bash
   mix ecto.setup
   ```

3. Start the Phoenix server:
   ```bash
   mix phx.server
   ```

4. Visit [`localhost:4000/durable-objects`](http://localhost:4000/durable-objects) to manage your Durable Objects

### Configuration

Configure OpenAI API keys in your environment:

```bash
export OPENAI_API_KEY=your_api_key_here
```

### Creating a Self-Modifying Object

#### Method 1: Manual Creation
1. Use the web interface to create a new Durable Object with initial code
2. Provide a modification prompt describing the desired changes
3. The system will plan, generate, and evaluate the modifications
4. If the changes meet quality thresholds, the object will be updated
5. Deploy the object to make it active in the system

#### Method 2: Creation From Scratch
1. Click "Create From Scratch" on the Durable Objects page
2. Provide a name, description, and detailed requirements
3. The system will:
   - Plan the implementation based on requirements
   - Generate code and file structure
   - Evaluate the generated code against constraints and preferences
   - Create the object and write files to the file system
4. Once created, you can further modify or deploy the object

## Use Cases

- **Self-extending APIs**: APIs that can evolve based on usage patterns
- **Adaptive Data Models**: Resources that adjust their structure based on data trends
- **Learning System Components**: System parts that improve through feedback loops
- **AI-assisted Refactoring**: Code that gets continuously improved with minimal human intervention
- **Rapid Prototyping**: Quickly generate new components from natural language descriptions

## Future Enhancements

- **Local Model Support**: Integration with local LLMs for offline operation
- **Learning from Rejections**: System improvement based on failed modifications
- **Multi-Agent Review**: Multiple specialized evaluation agents for different aspects
- **User Feedback Loop**: Incorporating explicit user feedback into the reward model
- **Project Generation**: Create entire projects with multiple interconnected components

## Security Considerations

This system allows code to modify itself, which inherently carries risks. Always:

1. Run in a sandboxed environment
2. Limit the scope of what self-modifying objects can access
3. Monitor for unusual behavior
4. Maintain multiple backups and rollback capabilities
5. Consider a human-in-the-loop approach for critical systems

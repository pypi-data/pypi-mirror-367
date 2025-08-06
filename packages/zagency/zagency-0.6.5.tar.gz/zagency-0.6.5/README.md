# zagency

A framework for building AI agents with LLM integration, tool discovery, and comprehensive evaluation capabilities.

## Installation

```bash
pip install zagency
```

For development:
```bash
pip install -e .
```

## Quick Start

```python
from zagency import Agent, LiteLLM, tool

class MyAgent(Agent):
    @tool
    def calculate(self, expression: str) -> float:
        """Evaluate a mathematical expression"""
        return eval(expression)
    
    def step(self, environment):
        # Agent logic here
        state = self.ingest_state(environment)
        if state.get("task"):
            result = self.invoke([{"role": "user", "content": state["task"]}])
            environment.update_state({"result": result}, agent=self)
        return {"status": "completed"}

# Initialize and run
lm = LiteLLM(model="gpt-4")
agent = MyAgent(lm)
```

## Core Components

### Agents
Base class for all agents with automatic tool discovery:
- Inherit from `Agent` class
- Implement `step()` method for agent logic
- Use `@tool` decorator to expose methods to LLM
- Access LLM through `self.invoke()`

### Environments
State management between agents:
- **Environment**: All agents share the same state
- **IsolatedEnvironment**: Each agent has private state with shared globals
- **CodingEnvironment**: Specialized for code editing tasks

### Language Models
Built on LiteLLM for multi-provider support:
```python
from zagency import LiteLLM

# Supports OpenAI, Anthropic, and more
lm = LiteLLM(model="gpt-4")
lm = LiteLLM(model="claude-3-opus")
```

### Tools
Decorated methods automatically become LLM-callable:
```python
@tool
def search_files(self, pattern: str) -> list:
    """Search for files matching pattern"""
    return Path(".").glob(pattern)
```

## Evaluation Framework

### Scorers
Evaluate different aspects of agent behavior:
- **AgentScorer**: Internal metrics (tokens, decisions)
- **EnvironmentScorer**: State changes
- **TraceScorer**: End-to-end performance

### Running Evaluations
```python
from zagency.core import Evaluation

eval = Evaluation(
    name="my_eval",
    scorers=[MyScorer(), AnotherScorer()]
)

results = eval.run(
    agent=agent,
    environment_class=Environment,
    dataset=test_cases,
    max_steps_per_datum=50
)
```

## Advanced Usage

### Multi-Agent Systems
```python
from zagency.handler import StepHandler

handler = StepHandler(environment)
handler.add_agent(agent1)
handler.add_agent(agent2)
handler.run(max_steps=100)
```

### Custom Environments
```python
class MyEnvironment(Environment):
    def get_state(self, agent=None):
        # Return state for requesting agent
        return self._state
    
    def update_state(self, updates, agent=None):
        # Handle state updates
        self._state.update(updates)
```

## Project Structure

```
zagency/
├── core/
│   ├── agent.py          # Base Agent class
│   ├── environment.py    # Environment implementations
│   ├── lm.py            # Language model abstraction
│   ├── scorer.py        # Scoring system
│   └── evaluation.py    # Evaluation framework
├── environments/        # Specialized environments
├── handler/            # Agent orchestration
└── tests/             # Test suite
```

## Key Features

- **Automatic tool discovery** via decorators
- **Multi-LLM support** through LiteLLM
- **Flexible state management** with environments
- **Comprehensive evaluation** framework
- **Token usage tracking** and cost monitoring
- **Rich console output** support

## Dependencies

- torch, litellm, rich, pydantic
- whisper, pyannote.audio (for audio capabilities)
- ffmpeg-python (for media processing)

## Development

```bash
# Run tests
pytest tests/

# Build package
make build

# Clean artifacts
make cleanup
```

## License

MIT License

## Links

- [Full Documentation](NEW_FRAMEWORK.md)
- [API Reference](https://github.com/lowercaselabs/zagency)
- [Examples](https://github.com/lowercaselabs/zagency/examples)
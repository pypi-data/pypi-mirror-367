# django-agentkore

A Django extension for scaffolding and managing LLM-based agents in your Django projects.

## Features

- Django management command for agent scaffolding (`startagent`)
- Base agent classes and utilities
- Agent auto-discovery in Django projects
- Easily integrate AI agents into your Django applications

## Installation

```bash
pip install agentkore
```

### Using uv

You can also install using [uv](https://github.com/astral-sh/uv), a fast Python package installer and resolver:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install agentkore
uv pip install agentkore
```

## Setting up in your Django project

1. Add `agentkore` to your `INSTALLED_APPS` in your Django settings:

```python
INSTALLED_APPS = [
    # ... other apps
    'agentkore',
]
```

2. Run the `startagent` command to create a new agent:

```bash
python manage.py startagent myagent
```

This will create the following structure:
```
agents/
  myagent/
    __init__.py
    agent.py
    prompt_templates/
      base.txt
    tests/
      __init__.py
      test_myagent.py
```

## Using your agent

```python
from agents.myagent import MyagentAgent

# Create an instance of your agent
agent = MyagentAgent()

# Process a user prompt
response = agent.run("What's the weather like today?")
```

## Auto-discovering agents

The `AgentRegistry` class can automatically discover all agents in your project:

```python
from agentkore.kore import discover_agents

# Discover all agents in the 'agents' directory
agents = discover_agents()

# Get a list of all available agent names
agent_names = list(agents.keys())
```

## Creating Custom Agents

Extend the `BaseAgent` class to implement your own AI agents:

```python
from agentkore.kore import BaseAgent
import openai

class WeatherAgent(BaseAgent):
    def run(self, prompt, context=None):
        # Use OpenAI to process weather queries
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a weather assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
```

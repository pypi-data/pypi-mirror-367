from django.core.management.base import BaseCommand, CommandError
import os
import shutil
from pathlib import Path


class Command(BaseCommand):
    help = 'Creates a new AI agent scaffold in your Django project'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='The name of the agent to create')
        parser.add_argument(
            '--directory',
            dest='directory',
            default='agents',
            help='Directory where the agent should be created (default: "agents")',
        )

    def handle(self, *args, **options):
        agent_name = options['name']
        directory = options['directory']

        # Make sure the agent name is valid
        if not agent_name.isidentifier():
            raise CommandError(f"'{agent_name}' is not a valid Python identifier")

        # Create directory structure
        base_dir = Path(directory)
        agent_dir = base_dir / agent_name

        if agent_dir.exists():
            raise CommandError(f"Agent directory '{agent_dir}' already exists")

        # Create directories
        os.makedirs(agent_dir, exist_ok=True)

        # Create __init__.py
        with open(agent_dir / "__init__.py", "w") as f:
            f.write(f"""from .agent import {agent_name.capitalize()}Agent
"""
            )

        # Create agent.py with scaffold
        with open(agent_dir / "agent.py", "w") as f:
            f.write(f"""class {agent_name.capitalize()}Agent:
    \"\"\"
    A Django-based LLM agent scaffold.
    \"\"\"

    def __init__(self, config=None):
        self.config = config or {{}}
        self.name = "{agent_name}"

    def run(self, prompt: str, context=None) -> str:
        \"\"\"
        Execute the agent's main logic on the given prompt.
        
        Args:
            prompt: The user prompt or query
            context: Optional additional context for the agent
            
        Returns:
            str: The agent's response
        \"\"\"
        # TODO: Implement your agent logic here (e.g. OpenAI, LangChain, etc.)
        return f"[{{self.name}}] processing: {{prompt}}"
"""
            )

        # Create prompt_templates directory with a basic template
        os.makedirs(agent_dir / "prompt_templates", exist_ok=True)
        with open(agent_dir / "prompt_templates" / "base.txt", "w") as f:
            f.write("""You are a helpful AI assistant.

Context: {context}

User prompt: {prompt}
"""
            )

        # Create tests directory with a test file
        os.makedirs(agent_dir / "tests", exist_ok=True)
        with open(agent_dir / "tests" / "__init__.py", "w") as f:
            f.write("")

        with open(agent_dir / "tests" / f"test_{agent_name}.py", "w") as f:
            f.write(f"""from django.test import TestCase
from ..agent import {agent_name.capitalize()}Agent

class {agent_name.capitalize()}AgentTests(TestCase):
    def setUp(self):
        self.agent = {agent_name.capitalize()}Agent()
        
    def test_agent_initialization(self):
        self.assertEqual(self.agent.name, "{agent_name}")
        
    def test_agent_run(self):
        response = self.agent.run("Hello")
        self.assertIsInstance(response, str)
        self.assertIn("{agent_name}", response)
"""
            )

        self.stdout.write(self.style.SUCCESS(f"Successfully created agent '{agent_name}' in '{agent_dir}'"))

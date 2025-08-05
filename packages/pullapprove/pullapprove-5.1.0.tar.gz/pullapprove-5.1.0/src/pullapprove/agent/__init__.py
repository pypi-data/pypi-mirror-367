import shlex
import subprocess
from enum import Enum
from functools import cached_property
from pathlib import Path


def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt from the prompts directory.
    """
    prompt_file = Path(__file__).parent / "prompts" / f"{prompt_name}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file {prompt_file} does not exist.")
    return prompt_file.read_text().strip()


class AgentType(Enum):
    EDIT = "edit"
    NEW = "new"
    FIX = "fix"
    MIGRATE_V3 = "migrate_v3"
    MIGRATE_CODEOWNERS = "migrate_codeowners"


class Agent:
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type

    @cached_property
    def prompt(self):
        prompt = load_prompt("base")

        prompt += "\n\n" + load_prompt(self.agent_type.value)

        return prompt

    def run_command(self, command: str):
        prompt = self.prompt
        prompt += "\n\n" + load_prompt("cli")

        command_args = shlex.split(command)
        command_args.append(prompt)

        result = subprocess.run(command_args)

        return result.returncode == 0

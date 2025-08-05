from typing import Optional
import re
import yaml
from pathlib import Path

from xlin import ls, load_text, xmap_async

from agentlin.core.types import *


class SubAgentConfig(BaseModel):
    """
    Configuration for a sub-agent.
    """

    id: str
    name: str
    description: str
    model: Optional[str] = None  # Optional model name
    developer_prompt: str
    code_for_agent: str
    code_for_interpreter: str
    allowed_tools: list[str] = ["*"]


class SubAgentLoader:
    """SubAgent 加载器"""
    async def load_subagents(self, dir_path: Union[str, list[str]]) -> list[SubAgentConfig]:
        paths = ls(dir_path)
        subagents = await xmap_async(paths, self.load_subagent)
        return [subagent for subagent in subagents if subagent]

    def load_subagent(self, path: str) -> Optional[SubAgentConfig]:
        """
        Load a sub-agent configuration from a markdown file.

        Expected format:
        ---
        name: agent-name
        description: Agent description
        model: model-name (optional)
        allowed_tools: ["tool1", "tool2"] (optional, defaults to ["*"])
        ---

        Agent prompt content here...

        ## Code for Agent (optional)
        ```python
        # Code specific for agent
        ```

        ## Code for Interpreter (optional)
        ```python
        # Code specific for interpreter
        ```
        """
        try:
            text = load_text(path)
            if not text:
                return None

            # Parse YAML front matter
            front_matter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
            match = re.match(front_matter_pattern, text, re.DOTALL)

            if not match:
                print(f"No valid front matter found in {path}")
                return None

            yaml_content, markdown_content = match.groups()

            # Parse YAML
            try:
                metadata = yaml.safe_load(yaml_content)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML in {path}: {e}")
                return None

            # Extract required fields
            name = metadata.get('name')
            description = metadata.get('description')
            model = metadata.get('model')  # Optional model name

            if not name or not description:
                print(f"Missing required fields (name, description) in {path}")
                return None

            # Generate ID from file path or use name
            file_path = Path(path)
            agent_id = file_path.stem

            # Extract developer prompt (everything before code sections)
            developer_prompt = self._extract_developer_prompt(markdown_content)

            # Extract code sections
            code_for_agent = self._extract_code_section(markdown_content, "Code for Agent")
            code_for_interpreter = self._extract_code_section(markdown_content, "Code for Interpreter")

            return SubAgentConfig(
                id=agent_id,
                name=name,
                description=description,
                model=model,
                developer_prompt=developer_prompt,
                code_for_agent=code_for_agent or "",
                code_for_interpreter=code_for_interpreter or "",
                allowed_tools=metadata.get('allowed_tools', ["*"])
            )

        except Exception as e:
            print(f"Error loading subagent from {path}: {e}")
            return None

    def _extract_developer_prompt(self, markdown_content: str) -> str:
        """Extract the main content before any code sections."""
        # Split by code section headers
        code_section_pattern = r'\n## Code for (Agent|Interpreter)'
        parts = re.split(code_section_pattern, markdown_content)

        if parts:
            # Return the first part (before any code sections)
            return parts[0].strip()

        return markdown_content.strip()

    def _extract_code_section(self, markdown_content: str, section_name: str) -> Optional[str]:
        """Extract code from a specific section."""
        # Pattern to match: ## Section Name followed by code block
        pattern = rf'## {re.escape(section_name)}\s*\n```(?:python)?\s*\n(.*?)\n```'
        match = re.search(pattern, markdown_content, re.DOTALL | re.IGNORECASE)

        if match:
            return match.group(1).strip()

        return None


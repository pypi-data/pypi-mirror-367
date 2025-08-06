"""
Directory-based agent that loads tools from files in a specified directory.
"""

import os
import tempfile
from typing import Any, Dict, List, Optional, Callable
import weave
from zagency.core.agent import Agent
from zagency.core.lm import LM
from zagency.core.environment import Environment
from zagency.core.base import tool, ToolRegistry


class ToolDirAgent(Agent):
    """
    An agent that loads tools from Python files in a specified directory.
    
    Each .py file in the directory can contain multiple functions with 'self' parameter.
    These functions are dynamically loaded and bound as agent methods.
    """
    
    def __init__(self, lm: LM, environment: Environment, tools_dir: Optional[str] = None):
        # Set up tools directory before calling super().__init__
        if tools_dir is None:
            # Create temporary directory for agent lifetime
            self._temp_dir = tempfile.mkdtemp(prefix="agent_tools_")
            self.tools_dir = self._temp_dir
            self._is_temp_dir = True
        else:
            self.tools_dir = tools_dir
            self._temp_dir = None
            self._is_temp_dir = False
            
        os.makedirs(self.tools_dir, exist_ok=True)
        
        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        
        # Initialize base agent
        super().__init__(lm, environment)
    
    def _discover_tools(self) -> Dict[str, Callable]:
        """
        Override base method to discover tools using ToolRegistry.
        """
        # Discover tools from instance methods (like 'exit', etc.)
        self.tool_registry.discover_from_instance(self)
        
        # Load tools from directory
        self.tool_registry.load_from_directory(self.tools_dir, self)
        
        return self.tool_registry.tools
    

    
    @weave.op()
    def _confirm_decorator(self, tool_code: str) -> str:
        """
        Ensure the tool code has @tool decorator, add it if missing.
        """
        if "@tool" not in tool_code:
            lines = tool_code.strip().split('\n')
            # Find the def line and add decorator before it
            for i, line in enumerate(lines):
                if line.strip().startswith('def '):
                    lines.insert(i, '@tool')
                    break
            tool_code = '\n'.join(lines)
        return tool_code
    
    @weave.op()
    def _write_tool(self, tool_name: str, tool_code: str) -> str:
        """
        Write the tool code to a file in the tools directory.
        Returns the file path of the created tool.
        """
        # Create complete file content
        full_tool_code = f"""from zagency.core.base import tool

{tool_code}
"""
        
        # Write to file
        tool_file = os.path.join(self.tools_dir, f"{tool_name}.py")
        with open(tool_file, 'w') as f:
            f.write(full_tool_code)
        
        return tool_file
    
    @weave.op()
    def _load_tool(self, tool_file: str, tool_name: str) -> str:
        """
        Validate and load the tool file, handling errors and cleanup.
        Returns success/error message.
        """
        # Validate the file using ToolRegistry static methods
        is_importable, import_error = ToolRegistry.validate_importable(tool_file)
        if not is_importable:
            os.remove(tool_file)  # Clean up failed file
            return f"Error: Tool file not importable - {import_error}"
        
        is_decorated, decorator_error = ToolRegistry.validate_tool_decorators(tool_file)
        if not is_decorated:
            os.remove(tool_file)  # Clean up failed file
            return f"Error: Tool validation failed - {decorator_error}"
        
        # Reload tools using registry
        self.tool_registry.reload_from_directory(self.tools_dir, self)
        self.tools = self.tool_registry.tools
        
        return f"Tool '{tool_name}' created successfully and is now callable as self.{tool_name}()"

    @tool
    def create_tool(self, tool_name: str, tool_code: str) -> str:
        """
        Create a new tool by writing it to a file in the tools directory.
        Tool code should be a complete function definition with 'self' parameter.
        """
        # Step 1: Confirm decorator is present
        decorated_code = self._confirm_decorator(tool_code)
        
        # Step 2: Write tool to file
        tool_file = self._write_tool(tool_name, decorated_code)
        
        # Step 3: Load and validate the tool
        result = self._load_tool(tool_file, tool_name)
        
        return result
    
    @tool
    def list_tool_files(self) -> str:
        """
        List all tool files in the tools directory.
        """
        if not os.path.exists(self.tools_dir):
            return "Tools directory does not exist"
        
        files = [f for f in os.listdir(self.tools_dir) if f.endswith('.py') and not f.startswith('__')]
        if not files:
            return "No tool files found"
        
        return f"Tool files: {', '.join(files)}"
    
    @tool
    def reload_tools(self) -> str:
        """
        Reload all tools from the directory.
        """
        self.tool_registry.reload_from_directory(self.tools_dir, self)
        self.tools = self.tool_registry.tools
        tool_names = [name for name in self.tools.keys() if not name in ['exit', 'list_tool_files', 'reload_tools', 'create_tool']]
        return f"Reloaded tools: {', '.join(tool_names) if tool_names else 'None'}"
    
    def get_tools_directory(self) -> str:
        """
        Get the path to the tools directory.
        """
        return self.tools_dir
    
    def __del__(self):
        """
        Clean up temporary directory if one was created.
        """
        if self._is_temp_dir and self._temp_dir and os.path.exists(self._temp_dir):
            import shutil
            try:
                shutil.rmtree(self._temp_dir)
            except:
                pass  # Best effort cleanup
    
    # Abstract methods from base Agent class
    def ingest_state(self, environment: Environment) -> Dict[str, Any]:
        """
        Ingest the state of the environment.
        """
        return {"tools_dir": self.tools_dir, "num_tools": len(self.tools)}
    
    def synthesize_lm_input(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Synthesize the input for the language model.
        """
        env_state = kwargs.get('env_state', {})
        return [
            {
                "role": "system", 
                "content": f"You are an agent with {len(self.tools)} tools available. Tools directory: {self.tools_dir}"
            }
        ]

    def _generate_tool_definitions(self) -> List[Dict[str, Any]]:
        """Generate OpenAI tool definitions using ToolRegistry."""
        return self.tool_registry.get_openai_tools()

    @weave.op()
    def step(self) -> Dict[str, Any]:
        """
        Step the agent with a simple example.
        """
        # Simple step function for testing
        lm_response = self.lm.invoke(
            messages=[{"role": "user", "content": "Create a tool that calls self.environment.test_fabric() and returns the result NO ASYNC"}],
            tools=self._generate_tool_definitions()
        )
        lm_response = self.handle_lm_response(lm_response)
        response = lm_response['LM_response']
        result = {}
        if response.tool_calls:
            tool_results = self._execute_tool_calls(response.tool_calls)
            result['tool_calls'] = self.tool_call_message(tool_results)
        if response.content:
            result['content'] = response.content
        return result
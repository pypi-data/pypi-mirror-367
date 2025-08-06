"""
Self-improving agent that can dynamically create, update, and remove its own tools.
"""

import os
import importlib.util
import sys
import ast
from typing import Any, Dict, Callable, List, Tuple
import weave
from zagency.core.agent import Agent
from zagency.core.lm import LM
from zagency.core.environment import Environment
from zagency.core.base import tool


class ImprovingAgent(Agent):
    """
    An agent that can create, update, and remove its own tools dynamically.
    Tools are stored as separate files in a tools directory and loaded as bound methods.
    Each version creates a new complete agent file with all tools integrated.
    """
    
    def __init__(self, lm: LM, environment: Environment):
        super().__init__(lm, environment)
        self.tools_dir = "./agent_tools"
        self.version = 1
        self.version_str = "v1"
        self._dynamic_tools = {}  # Track dynamically added tools
        os.makedirs(self.tools_dir, exist_ok=True)
        
        # Load existing tools from directory
        self._load_tools_from_directory()
    
    def _load_tools_from_directory(self):
        """
        Load all existing tools from the tools directory.
        """
        if not os.path.exists(self.tools_dir):
            return
            
        for filename in os.listdir(self.tools_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                tool_name = filename[:-3]  # Remove .py extension
                tool_path = os.path.join(self.tools_dir, filename)
                
                try:
                    self._load_and_bind_tool(tool_name, tool_path)
                except Exception as e:
                    print(f"Failed to load tool {tool_name}: {e}")
                    
        # Refresh tools discovery after loading
        self.tools = self._discover_tools()
    
    def _load_and_bind_tool(self, tool_name: str, tool_path: str):
        """
        Load a tool from a file and bind it to the agent instance.
        """
        spec = importlib.util.spec_from_file_location(tool_name, tool_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find the tool function (should have same name as file)
        if hasattr(module, tool_name):
            tool_func = getattr(module, tool_name)
            
            # Bind to agent instance
            bound_tool = tool_func.__get__(self, self.__class__)
            setattr(self, tool_name, bound_tool)
            
            # Read the original code for tracking
            with open(tool_path, 'r') as f:
                file_content = f.read()
            
            # Track in dynamic tools
            self._dynamic_tools[tool_name] = {
                'function': bound_tool,
                'code': file_content,
                'path': tool_path
            }
        else:
            raise ValueError(f"Function {tool_name} not found in {tool_path}")
    
    def _check_tool_compilation(self, tool_code: str) -> Tuple[bool, str]:
        """
        Check if tool code compiles and has valid structure.
        Returns (is_valid, error_message).
        """
        try:
            # Try to parse the code
            parsed = ast.parse(tool_code)
            
            # Check if there's at least one function definition
            has_function = any(isinstance(node, ast.FunctionDef) for node in ast.walk(parsed))
            if not has_function:
                return False, "No function definition found in tool code"
            
            # Try to compile
            compile(tool_code, '<string>', 'exec')
            return True, ""
            
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Compilation error: {e}"

    @tool
    def create_tool(self, tool_name: str, tool_code: str) -> str:
        """
        Create a new tool for the agent. Tool code should be a complete function definition.
        The @tool decorator will be automatically added if not present.
        """
        # Check compilation first
        is_valid, error_msg = self._check_tool_compilation(tool_code)
        if not is_valid:
            return f"Error: Invalid tool code for {tool_name}: {error_msg}"
        
        # Add @tool decorator if not present
        if "@tool" not in tool_code:
            lines = tool_code.strip().split('\n')
            # Find the def line and add decorator before it
            for i, line in enumerate(lines):
                if line.strip().startswith('def '):
                    lines.insert(i, '@tool')
                    break
            tool_code = '\n'.join(lines)
        
        # Write tool to file
        tool_path = os.path.join(self.tools_dir, f"{tool_name}.py")
        full_tool_code = f"""from zagency.core.base import tool

{tool_code}
"""
        
        with open(tool_path, 'w') as f:
            f.write(full_tool_code)
        
        # Load and bind the tool
        try:
            self._load_and_bind_tool(tool_name, tool_path)
        except Exception as e:
            return f"Error loading tool {tool_name}: {e}"
        
        # Refresh tools discovery
        self.tools = self._discover_tools()
        
        # Generate versioned agent file
        self.increment_agent_version()
        
        return f"Tool '{tool_name}' created successfully and is now callable as self.{tool_name}()"
    
    @tool 
    def remove_tool(self, tool_name: str) -> str:
        """
        Remove a tool from the agent. The tool file is preserved but tool is no longer accessible.
        """
        if tool_name not in self._dynamic_tools:
            return f"Error: Tool '{tool_name}' not found in dynamic tools"
        
        # Remove from agent
        if hasattr(self, tool_name):
            delattr(self, tool_name)
        
        # Remove from tracking (but keep file)
        del self._dynamic_tools[tool_name]
        
        # Refresh tools discovery
        self.tools = self._discover_tools()
        
        # Generate versioned agent file
        self.increment_agent_version()
        
        return f"Tool '{tool_name}' removed successfully"
    
    @tool
    def update_tool(self, tool_name: str, new_tool_code: str) -> str:
        """
        Update an existing tool with new code.
        """
        if tool_name not in self._dynamic_tools:
            return f"Error: Tool '{tool_name}' not found. Use create_tool to add new tools."
        
        # Check compilation first
        is_valid, error_msg = self._check_tool_compilation(new_tool_code)
        if not is_valid:
            return f"Error: Invalid tool code for {tool_name}: {error_msg}"
        
        # Remove old tool
        self.remove_tool(tool_name)
        
        # Create new tool with updated code
        return self.create_tool(tool_name, new_tool_code)
    
    def increment_agent_version(self):
        """
        Create a new versioned agent file with all current tools integrated as methods.
        This creates a complete, standalone agent class.
        """
        self.version += 1
        self.version_str = f"v{self.version}"
        version_file = f"improving_agent_{self.version_str}.py"
        
        # Read current agent source as base
        current_file = __file__
        with open(current_file, 'r') as f:
            source_code = f.read()
        
        # Extract tool code from files and format as class methods
        tools_methods = ""
        for tool_name, tool_info in self._dynamic_tools.items():
            tool_path = tool_info['path']
            with open(tool_path, 'r') as f:
                tool_file_content = f.read()
            
            # Extract just the function definition (skip imports)
            lines = tool_file_content.split('\n')
            tool_lines = []
            in_function = False
            
            for line in lines:
                if line.strip().startswith('def ') or line.strip().startswith('@tool'):
                    in_function = True
                if in_function:
                    # Add proper indentation for class method
                    if line.strip():
                        tool_lines.append('    ' + line if not line.startswith('    ') else line)
                    else:
                        tool_lines.append('')
            
            if tool_lines:
                tools_methods += '\n' + '\n'.join(tool_lines) + '\n'
        
        # Insert tools before the end of the class
        lines = source_code.split('\n')
        
        # Find the last method of the ImprovingAgent class
        insert_index = len(lines) - 1
        for i in range(len(lines)-1, -1, -1):
            line = lines[i].strip()
            if line and not line.startswith('#') and not line.startswith('    ') and i > 0:
                # Found end of class, insert before this line
                insert_index = i
                break
        
        # Insert the dynamic tools
        if tools_methods.strip():
            lines.insert(insert_index, f"\n    # Dynamic Tools (added in {self.version_str})")
            lines.insert(insert_index + 1, tools_methods)
        
        modified_source = '\n'.join(lines)
        
        # Write versioned file
        with open(version_file, 'w') as f:
            f.write(modified_source)
        
        return version_file
    
    def get_environment_fabric(self) -> Dict[str, Callable]:
        """
        Get available environment capabilities that can inform tool creation.
        """
        return self.environment.get_fabric()
    
    def ingest_state(self, environment: Environment) -> Dict[str, Any]:
        """
        Ingest the state of the environment.
        """
        pass
    def synthesize_lm_input(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Synthesize the input for the language model.
        """
        pass

    @weave.op()
    def step(self) -> Dict[str, Any]:
        """
        Step the agent.
        """
        # simple step function that we will manipulate later:
        lm_response = self.lm.invoke(messages=[{"role": "user", "content": "Create a tool that calls self.environment.test_fabric() and returns the result"}], tools=self._generate_tool_definitions())
        lm_response = self.handle_lm_response(lm_response)
        response = lm_response['LM_response']
        result = {}
        if response.tool_calls:
            tool_results = self._execute_tool_calls(response.tool_calls)
            result['tool_calls'] = self.tool_call_message(tool_results)
        if response.content:
            result['content'] = response.content
        return result
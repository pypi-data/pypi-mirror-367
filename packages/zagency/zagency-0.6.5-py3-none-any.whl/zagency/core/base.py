from typing import Callable, Dict, Any, List, Optional, Union
import weave
import inspect
from pydantic import BaseModel, Field


class ParameterInfo(BaseModel):
    """Information about a function parameter."""
    name: str
    type: str
    description: Optional[str] = None
    required: bool = True
    default: Optional[Any] = None
    
    def __repr__(self) -> str:
        parts = [f"{self.name}: {self.type}"]
        if self.description:
            parts.append(f"- {self.description}")
        if not self.required:
            parts.append(f"(optional, default: {self.default})")
        return " ".join(parts)


class ToolCallDefinition(BaseModel):
    """OpenAI-compliant tool calling definition."""
    type: str = "function"
    function: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def from_function(cls, func: Callable, name: Optional[str] = None) -> "ToolCallDefinition":
        """Create a tool call definition from a function."""
        sig = inspect.signature(func)
        
        # Extract parameters
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name in ['self', 'cls']:
                continue
                
            param_type = "string"  # Default type
            if param.annotation != inspect.Parameter.empty:
                if param.annotation in [int, float]:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation in [list, List]:
                    param_type = "array"
                elif param.annotation in [dict, Dict]:
                    param_type = "object"
            
            properties[param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}"
            }
            
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        # TODO: @zubin make this a first party citizen of `base` ...
        function_def = {
            "name": name or func.__name__,
            "description": func.__doc__ or f"Execute {func.__name__}",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
        
        return cls(function=function_def)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for LLM."""
        return {
            "type": self.type,
            "function": self.function
        }
    
    def to_oai_tc(self) -> Dict[str, Any]:
        """Convert to OpenAI tool call format"""
        return self.function # just the function is what we want


class Fabric(BaseModel):
    """
    Represents a fabric method with all necessary metadata for LLM understanding.
    """
    name: str
    description: str
    parameters: List[ParameterInfo] = Field(default_factory=list)
    return_type: str = "Any"
    
    @classmethod
    def from_method(cls, method: Callable, name: Optional[str] = None) -> "Fabric":
        """Create a Fabric instance from a method."""
        sig = inspect.signature(method)
        method_name = name or method.__name__
        
        # Extract parameters
        parameters = []
        for param_name, param in sig.parameters.items():
            if param_name in ['self', 'cls']:
                continue
                
            type_str = str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any"
            type_str = type_str.replace("<class '", "").replace("'>", "")
            
            param_info = ParameterInfo(
                name=param_name,
                type=type_str,
                required=param.default == inspect.Parameter.empty,
                default=param.default if param.default != inspect.Parameter.empty else None
            )
            parameters.append(param_info)
        
        # Get return type
        return_type = "Any"
        if sig.return_annotation != inspect.Signature.empty:
            return_type = str(sig.return_annotation)
            return_type = return_type.replace("<class '", "").replace("'>", "")
        
        return cls(
            name=method_name,
            description=method.__doc__ or f"Execute {method_name}",
            parameters=parameters,
            return_type=return_type,
        )
    
    def __str__(self) -> str:
        """LLM-friendly representation."""
        lines = [
            f"🔧 {self.name}",
            f"Description: {self.description.strip()}",
        ]
        
        if self.parameters:
            lines.append("Parameters:")
            for param in self.parameters:
                lines.append(f"  • {param}")
        else:
            lines.append("Parameters: None")
            
        lines.append(f"Returns: {self.return_type}")
        
        return "\n".join(lines)
    
class ToolRegistry(BaseModel):
    """
    Registry for managing tools that can be called by agents.
    Handles discovery, loading, and OpenAI format conversion.
    """
    tools: Dict[str, Callable] = Field(default_factory=dict)
    tool_definitions: Dict[str, ToolCallDefinition] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_tool(self, name: str, func: Callable) -> None:
        """Add a single tool to the registry."""
        self.tools[name] = func
        self.tool_definitions[name] = ToolCallDefinition.from_function(func, name)
    
    def discover_from_instance(self, instance: Any) -> None:
        """
        Discover tools from an instance by looking for methods with @tool decorator.
        """
        for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
            if hasattr(method, "_is_tool") and not name.startswith('_'):
                self.add_tool(name, method)
    
    def load_from_directory(self, tools_dir: str, agent_instance: Any) -> None:
        """
        Load tools from Python files in a directory.
        Functions with 'self' parameter are bound to the agent_instance.
        """
        import os
        import importlib.util
        
        if not os.path.exists(tools_dir):
            return
            
        for filename in os.listdir(tools_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                file_path = os.path.join(tools_dir, filename)
                
                try:
                    file_tools = self._extract_tools_from_file(file_path, agent_instance)
                    for name, tool in file_tools.items():
                        self.add_tool(name, tool)
                except Exception as e:
                    print(f"Failed to load tools from {filename}: {e}")
    
    def _extract_tools_from_file(self, file_path: str, agent_instance: Any) -> Dict[str, Callable]:
        """Extract all tool functions from a single file."""
        import os
        import importlib.util
        
        tools = {}
        
        # Load the module
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find all functions with 'self' parameter
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if self._is_tool_function(obj):
                # Bind function to agent instance
                bound_tool = obj.__get__(agent_instance, agent_instance.__class__)
                setattr(agent_instance, name, bound_tool)
                tools[name] = bound_tool
                
        return tools
    
    def _is_tool_function(self, func: Callable) -> bool:
        """Check if a function should be treated as a tool."""
        try:
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            return len(params) > 0 and params[0] == 'self'
        except (ValueError, TypeError):
            return False
    
    def reload_from_directory(self, tools_dir: str, agent_instance: Any) -> None:
        """Reload all tools from directory, clearing existing directory-based tools first."""
        # Keep only tools that were added directly (not from files)
        original_tools = {}
        for name, method in inspect.getmembers(agent_instance, predicate=inspect.ismethod):
            if hasattr(method, "_is_tool") and not name.startswith('_'):
                original_tools[name] = method
        
        # Clear and rebuild
        self.tools.clear()
        self.tool_definitions.clear()
        
        # Re-add original tools
        for name, tool in original_tools.items():
            self.add_tool(name, tool)
        
        # Load from directory
        self.load_from_directory(tools_dir, agent_instance)
    
    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Get tools in OpenAI API format."""
        return [definition.to_oai_tc() for definition in self.tool_definitions.values()]
    
    def __repr__(self) -> str:
        """Pretty representation of the registry."""
        tool_list = list(self.tools.keys())
        return f"ToolRegistry(tools={tool_list})"
    
    @staticmethod
    def validate_importable(file_path: str) -> tuple[bool, str]:
        """Validate that a file can be imported without errors."""
        import os
        import importlib.util
        
        try:
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return True, ""
        except Exception as e:
            return False, f"Import error: {e}"
    
    @staticmethod
    def validate_tool_decorators(file_path: str) -> tuple[bool, str]:
        """Validate that all functions with 'self' parameter are decorated with @tool."""
        import ast
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has 'self' parameter
                    if node.args.args and node.args.args[0].arg == 'self':
                        # Check if it has @tool decorator
                        has_tool_decorator = False
                        for decorator in node.decorator_list:
                            if (isinstance(decorator, ast.Name) and decorator.id == 'tool') or \
                               (isinstance(decorator, ast.Attribute) and decorator.attr == 'tool'):
                                has_tool_decorator = True
                                break
                        
                        if not has_tool_decorator:
                            return False, f"Function '{node.name}' with 'self' parameter missing @tool decorator"
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {e}"

################################################################################
# OUR REALLY NICE DECORATORS! EVERYBODY CLAP FOR THEM!
################################################################################

def tool(func: Callable) -> Callable:
    """
    Decorator to mark a method as a tool that can be called by an LM.
    """
    func._is_tool = True
    return func


def fabric(func: Callable) -> Callable:
    """
    Decorator to mark a method as fabric that can be discovered by agents.
    Fabric methods represent capabilities/actions that an environment provides.
    """
    func._is_fabric = True
    return func

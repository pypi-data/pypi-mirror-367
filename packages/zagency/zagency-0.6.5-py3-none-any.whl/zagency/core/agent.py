from abc import ABC, abstractmethod
import inspect
import json
from typing import Any, Dict, List, Callable, Optional
from pydantic import create_model
from zagency.core.lm import LM
from zagency.core.environment import Environment
from zagency.core.base import tool
import weave

class Agent(ABC):
    """
    Base class for all agents. An Agent has an environment (its state),
    an LM (its brain), and a set of tools (its methods).
    
    The agent follows a step-based execution model:
    1. Ingest state from environment
    2. Call LM with current state and history
    3. Execute tools against the environment
    """

    def __init__(self, lm: LM, environment: Environment):
        self.environment = environment
        self.environment.register_agent(self)
        self.lm = lm
        self.tools = self._discover_tools()
        self.is_finished = False
        self._internal_state = {}  # Agent's private state
        self.history = []  # Conversation history
        self._trajectory = [] # trajectory of the agent. Can be ANYTHING

    @weave.op()
    def run(self, max_steps: int = 100, stop_condition: Optional[Callable] = None):
        """
        Runs the agent for a given number of steps or until the stop condition is met.
        """
        if stop_condition is None:
            stop_condition = self.stop_condition
        for _ in range(max_steps):
            if stop_condition():
                break
            self.step()
    
    @abstractmethod
    def step(self) -> Dict[str, Any]:
        """
        Execute one step of the agent's logic.
        This is where the agent:
        1. Reads state from the environment
        2. Decides what to do
        3. Updates its internal state
        4. Returns the result of the step
        """
        pass
    
    @abstractmethod
    def ingest_state(self, **kwargs) -> Dict[str, Any]:
        """
        Read and process state from the environment.
        Subclasses MUST override to customize state ingestion.
        """
        raise NotImplementedError("Subclasses must override ingest_state")
    
    @abstractmethod
    def synthesize_lm_input(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Synthesize the agent's history to a list of LM messages.
        Subclasses MUST override to customize history to LM message conversion.
        """
        raise NotImplementedError("Subclasses must override synthesize_lm_input")

    @weave.op()
    def invoke(self) -> Dict[str, Any]:
        """
        The main entry point for the agent following the pattern:
        1. Ingest state from environment
        2. Call LM with state context
        3. Execute tools against environment

        TODO: @zubin handle multiple parallel tool calls -- I think they don't get appended to the history properly?
        """
        # Step 1: Ingest state from environment and synthesize LM input
        env_state = self.ingest_state(self.environment)
        lm_messages = self.synthesize_lm_input(env_state=env_state)
        
        # Step 2: Call LM with tools
        tool_defs = self._generate_tool_definitions()
        lm_result = self.lm.invoke(lm_messages, tool_defs)
        
        lm_response = self.handle_lm_response(lm_result)
        response_message = lm_response["LM_response"]
        
        # Step 3: Execute tools against environment
        if response_message.tool_calls:
            tc_results = self._execute_tool_calls(response_message.tool_calls)
            result = self.tool_call_message(tc_results) # TODO: this is a hack to get the tool calls into the history
        else:
            result = {'role':'assistant', 'content': str(response_message)}
        self.history.append(result)  # Assistant response
        
        return result

    @weave.op()
    @tool
    def exit(self):
        """
        Stops the agent's execution loop. Call this when the task is complete.
        """
        self.is_finished = True
        return "Agent execution has been stopped."
    
    # BELOW IS ALL THE HELPER CODE

    @staticmethod
    def handle_lm_response(lm_result) -> Dict[str, Any]:
        """
        Handles the LM response and returns a dictionary with the response and token usage.
        CAN be overridden if a non LiteLLM method is used.
        """
        # Handle response
        if isinstance(lm_result, dict) and "response" in lm_result:
            response = lm_result["response"]
            usage = lm_result.get("usage", None)
        else:
            response = lm_result
            usage = None
        response_message = response.choices[0].message

        result = {"LM_response": response_message}
        if usage is not None:
            result["token_usage"] = usage

        return result # {LM_response: response_message, token_usage: usage} or {LM_response: response_message}
    
    @staticmethod
    def tool_call_message(tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts a tool call into a message.
        """
        return {
            "role" : "assistant",
            'content' : f"Tool call ran with result: {tool_call}"
        }

    
    def _discover_tools(self) -> Dict[str, Callable]:
        """Finds all methods decorated with @tool."""
        tools = {}
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, "_is_tool"):
                tools[name] = method
        return tools

    def _generate_tool_definitions(self) -> List[Dict[str, Any]]:
        """Generates OpenAI-compatible tool definitions from the agent's methods."""
        definitions = []
        for name, func in self.tools.items():
            sig = inspect.signature(func)
            doc = inspect.getdoc(func)

            fields = {
                param.name: (param.annotation, ...)
                for param in sig.parameters.values()
                if param.name != "self"
            }
            params_model = create_model(f"{name}Params", **fields)
            schema = params_model.model_json_schema()

            definitions.append(
                {
                    "name": name,
                    "description": doc,
                    "parameters": {
                        "type": "object",
                        "properties": schema.get("properties", {}),
                        "required": schema.get("required", []),
                    },
                }
            )
        return definitions
    
    @weave.op()
    def _execute_tool_calls(self, tool_calls) -> Dict[str, Any]:
        """
        For each tool call executes the tool call and returns the result as a dictionary with the tool name as the key.
        """
        results = {}
        for tool_call in tool_calls:
            results.update(self._execute_tool_call(tool_call))
        return results
    
    def _execute_tool_call(self, tool_call) -> Dict[str, Any]:
        """Executes a tool call and returns the result as a dictionary with the tool name as the key."""
        func_name = tool_call.function.name
        if func_name in self.tools:
            kwargs = json.loads(tool_call.function.arguments)
            func = self.tools[func_name]
            
            # Filter kwargs to only include parameters that the function expects
            sig = inspect.signature(func)
            filtered_kwargs = {
                key: value 
                for key, value in kwargs.items() 
                if key in sig.parameters and key != "self"
            }
            
            return {func_name: func(**filtered_kwargs)}
        else:
            return f"Error: Tool '{func_name}' not found."
    
    def stop_condition(self, *args, **kwargs) -> bool:
        """
        Returns True if the agent should stop executing.
        """
        return self.is_finished



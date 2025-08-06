from abc import ABC, abstractmethod
import os
from typing import Any, Dict, List

import litellm
from openai import OpenAI
import weave

class LM(ABC):
    """
    Abstract Base class for all LMs.
    """

    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def invoke(self, **kwargs) -> Any:
        """
        Invokes the LM.
        """
        pass

class LiteLLM(LM):
    """
    A concrete implementation of an LM that uses litellm.
    """

    def invoke(
        self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]
    ) -> dict:
        """
        Invokes the LM with function calling and returns both the response and token usage.
        """
        response = litellm.completion(
            model=self.model,
            messages=messages,
            tools=[{"type": "function", "function": t} for t in tools],
        )
        # Extract token usage if available
        usage = getattr(response, 'usage', None)
        if usage is None and hasattr(response, '__getitem__'):
            usage = response.get('usage', None)
        return {"response": response, "usage": usage}
    
class WeaveOAILM(LM):
    """
    Uses the `trace.wandb.ai` api to inference *any* model including CW models lol.
    DOES NOT use the `weave.chat.completions.create` api as that does not support function calling.
    """

    def __init__(self, model: str, project: str):
        # we trust that you know the model is call-able. No hand-holding here.
        self.model = model
        self.oai_client = OpenAI(api_key=os.getenv("WANDB_API_KEY"), base_url="https://trace.wandb.ai/inference/v1", project=project)
        
    @weave.op()
    def invoke(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> dict:
        """
        Invokes the LM with function calling and returns both the response and token usage.
        """
        tools_converted = [{"type": "function", "function": t} for t in tools] if tools else None
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools_converted 
        response = self.oai_client.chat.completions.create(**kwargs)
        # Extract token usage if available
        usage = getattr(response, 'usage', None)
        if usage is None and hasattr(response, '__getitem__'):
            usage = response.get('usage', None)

        return {"response": response, "usage": usage}

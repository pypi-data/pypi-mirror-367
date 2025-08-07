"""
LLM client creation utility
"""
import instructor
from openai import OpenAI
from instructor import Mode
from .model_config import get_model_config
from typing import List, Dict
from pydantic import BaseModel, Field
from dataclasses import dataclass, field, asdict

def get_llm_client(model_name: str):
    """Create an LLM client for the specified model using its configuration.
    
    Args:
        model_name: Name of the model as defined in models.json
        
    Returns:
        tuple: (client, actual_model_name) where client is the configured instructor client
               and actual_model_name is the model name to use in API calls
        
    Raises:
        ValueError: If model not found in configuration or client creation fails
    """
    # Get model configuration
    model_cfg = get_model_config().get_model(model_name)
    if not model_cfg:
        raise ValueError(f"Model '{model_name}' not found in configuration. Please add it to models.json")
    
    # Create client for this model
    try:
        client = instructor.from_openai(
            OpenAI(
                api_key=model_cfg['api_key'],
                base_url=model_cfg['endpoint']
            ),
            mode=Mode.JSON
        )
        actual_model_name = model_cfg['model']
        return client, actual_model_name
    except Exception as e:
        raise ValueError(f"Failed to initialize client for model '{model_name}': {e}")

@dataclass
class CustomMiniSweModelConfig:
    """Configuration for CustomMiniSweModel"""
    model_name: str
    api_key: str = ""
    api_base: str = ""
    model_kwargs: Dict = field(default_factory=dict)

class CustomMiniSweModel:
    """Custom model for mini-swe-agent using direct OpenAI API"""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.model_kwargs = kwargs
        self.n_calls = 0
        self.cost = 0.0
        
        # Get client using our existing utility
        self.client, self.actual_model = get_llm_client(model_name)
        
        # Create config object for mini-swe compatibility
        model_cfg = get_model_config().get_model(model_name)
        self.config = CustomMiniSweModelConfig(
            model_name=self.actual_model,
            api_key=model_cfg['api_key'] if model_cfg else "",
            api_base=model_cfg['endpoint'] if model_cfg else "",
            model_kwargs=kwargs
        )
    
    def query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, str]:
        """Query the model and return response in mini-swe expected format"""
        # Merge kwargs
        final_kwargs = {**self.model_kwargs, **kwargs}
        
        # For mini-swe, we need raw text response, not structured output
        # Create a plain OpenAI client instead of instructor
        from openai import OpenAI
        model_cfg = get_model_config().get_model(self.model_name)
        plain_client = OpenAI(
            api_key=model_cfg['api_key'],
            base_url=model_cfg['endpoint']
        )
        
        # Make the API call
        response = plain_client.chat.completions.create(
            model=self.actual_model,
            messages=messages,
            **final_kwargs
        )
        
        self.n_calls += 1
        
        # Return in the format mini-swe expects
        content = response.choices[0].message.content or ""
        return {"content": content}
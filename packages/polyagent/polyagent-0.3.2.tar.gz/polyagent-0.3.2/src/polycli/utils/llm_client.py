"""
LLM client creation utility
"""
import instructor
from openai import OpenAI
from instructor import Mode
from .model_config import get_model_config

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
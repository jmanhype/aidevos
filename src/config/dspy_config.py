#!/usr/bin/env python3
"""
Configuration module for DSPy integration in AIDevOS.

This module provides configuration management for DSPy models and API keys.
"""

import os
import logging
from typing import Dict, Optional, Any, List
import dspy
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger("aidevos.dspy_config")
logger.setLevel(logging.INFO)

# Load environment variables from .env file if it exists
load_dotenv()


class DSPyConfig:
    """
    Configuration manager for DSPy in AIDevOS.
    
    This class handles loading and managing configurations for language models
    used with DSPy, including API keys and model settings.
    """
    
    def __init__(self):
        """Initialize the DSPy configuration manager."""
        self.config: Dict[str, Any] = {
            "api_keys": {},
            "default_model": "gpt-4",
            "models": {
                "gpt-4": {"provider": "openai", "max_tokens": 4096},
                "gpt-3.5-turbo": {"provider": "openai", "max_tokens": 4096},
                "claude-3": {"provider": "anthropic", "max_tokens": 100000}
            },
            "optimization": {
                "enabled": False,
                "metric": "accuracy",
                "max_rounds": 3
            }
        }
        
        # Load API keys from environment variables
        self._load_api_keys()
        
        # Initialize DSPy with default model
        self._initialize_dspy()
        
        logger.info("DSPy configuration initialized")
        
    def _load_api_keys(self) -> None:
        """Load API keys from environment variables."""
        # OpenAI API key
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            self.config["api_keys"]["openai"] = openai_key
            logger.info("OpenAI API key loaded from environment")
        else:
            logger.warning("OpenAI API key not found in environment")
            
        # Anthropic API key
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.config["api_keys"]["anthropic"] = anthropic_key
            logger.info("Anthropic API key loaded from environment")
        else:
            logger.warning("Anthropic API key not found in environment")
    
    def _initialize_dspy(self) -> None:
        """Initialize DSPy with the default language model."""
        default_model = self.config["default_model"]
        model_config = self.config["models"].get(default_model, {})
        provider = model_config.get("provider", "openai")
        
        # Set up the language model based on the provider
        try:
            if provider == "openai":
                api_key = self.config["api_keys"].get("openai")
                if api_key:
                    os.environ["OPENAI_API_KEY"] = api_key
                    # Use a generic LLM interface that will work with OpenAI
                    lm = dspy.LM(model=default_model)
                    dspy.settings.configure(lm=lm)
                    logger.info(f"DSPy initialized with OpenAI model: {default_model}")
                else:
                    logger.error("Cannot initialize OpenAI model: API key not found")
                    
            elif provider == "anthropic":
                api_key = self.config["api_keys"].get("anthropic")
                if api_key:
                    os.environ["ANTHROPIC_API_KEY"] = api_key
                    # Use a generic LLM interface for Anthropic
                    lm = dspy.LM(model=default_model, provider="anthropic")
                    dspy.settings.configure(lm=lm)
                    logger.info(f"DSPy initialized with Anthropic model: {default_model}")
                else:
                    logger.error("Cannot initialize Anthropic model: API key not found")
            
            else:
                logger.error(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Error initializing DSPy: {e}", exc_info=True)
    
    def optimize_modules(self, modules: List[dspy.Module], dataset: Any) -> None:
        """
        Optimize the provided DSPy modules using the specified dataset.
        
        Args:
            modules: List of DSPy modules to optimize.
            dataset: Dataset to use for optimization.
        """
        if not self.config["optimization"]["enabled"]:
            logger.info("Optimization is disabled")
            return
            
        logger.info("Starting DSPy module optimization")
        metric = self.config["optimization"]["metric"]
        max_rounds = self.config["optimization"]["max_rounds"]
        
        try:
            for i, module in enumerate(modules):
                logger.info(f"Optimizing module {i+1}/{len(modules)}")
                
                # Create an optimizer for this module
                optimizer = dspy.Optimize(
                    module=module,
                    metric=metric,
                    max_rounds=max_rounds
                )
                
                # Optimize the module
                optimizer.run(dataset)
                logger.info(f"Module {i+1} optimization completed")
                
        except Exception as e:
            logger.error(f"Error during optimization: {e}", exc_info=True)
    
    def set_default_model(self, model_name: str) -> bool:
        """
        Set the default language model for DSPy.
        
        Args:
            model_name: Name of the model to use as default.
            
        Returns:
            True if successful, False otherwise.
        """
        if model_name not in self.config["models"]:
            logger.error(f"Unknown model: {model_name}")
            return False
            
        self.config["default_model"] = model_name
        self._initialize_dspy()
        return True
    
    def add_model(self, name: str, provider: str, max_tokens: int) -> bool:
        """
        Add a new model to the configuration.
        
        Args:
            name: Name of the model.
            provider: Provider of the model (openai, anthropic, etc.).
            max_tokens: Maximum tokens the model can handle.
            
        Returns:
            True if successful, False otherwise.
        """
        if name in self.config["models"]:
            logger.warning(f"Model {name} already exists, updating configuration")
            
        self.config["models"][name] = {
            "provider": provider,
            "max_tokens": max_tokens
        }
        
        logger.info(f"Added model {name} ({provider}) to configuration")
        return True
    
    def enable_optimization(self, enabled: bool = True, metric: str = "accuracy", max_rounds: int = 3) -> None:
        """
        Enable or disable DSPy module optimization.
        
        Args:
            enabled: Whether optimization should be enabled.
            metric: Metric to use for optimization.
            max_rounds: Maximum number of optimization rounds.
        """
        self.config["optimization"] = {
            "enabled": enabled,
            "metric": metric,
            "max_rounds": max_rounds
        }
        
        if enabled:
            logger.info(f"Optimization enabled with metric '{metric}' and {max_rounds} max rounds")
        else:
            logger.info("Optimization disabled")


# Create a singleton instance
dspy_config = DSPyConfig()

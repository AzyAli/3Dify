"""Configuration management for 3dify.
This module handles configuration loading, validation, and application.
"""

import os
import json
from typing import Dict, Optional, Any, Union
from pathlib import Path

DEFAULT_CONFIG = {
    "general": {
        "verbose": True,
        "temp_dir": None, #This will end up using system temp dir if remained None!
    },
    "loader": {
        "cache_enabled": True,
        "cache_dir": ".3dify_cache",
    },
    "processor":{
        "num_workers": 4,
        "batch_size": 1,
    },
    "model":{
        "bolt3d": {
            "use_gpu": True,
            "device": "cuda:0",
        },
        "trellis": {
            "use_gpu": True,
            "device": "cuda:0",
        },
    },
    "export":{
        "optimize_mesh": True,
        "texture_resolution": 2048,
    },
    "visualization":{
        "jupyter":{
            # "enable": True,
            "width": 800,
            "height": 600,
        },
    },

}

class Config:
    """Configuration manager for the pipeline."""   
    def __init__(self, config_dict: Optional[Dict] = None, config_path: Optional[Union[str, Path]] = None):
        """Initialize the configuration with default values and optional overrides.
        Args:
            config_dict (dict, optional): Configuration dictionary to override defaults
            config_path (str or Path, optional): Path to a JSON configuration file 
        """
        self._config = DEFAULT_CONFIG.copy()
        if config_path:
            self._load_from_file(config_path)
        if config_dict:
            self._update_recursive(self._config, config_dict)
    
    def _load_from_file(self, config_path: Union[str, Path]):
        """Load configuration from a JSON file.
        Args:
            config_path (str or Path): Path to the JSON configuration file
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        with open(config_path, 'r') as f:
            try:
                file_config = json.load(f)
                self._update_recursive(self._config, file_config)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON format in configuration file: {config_path}")
    
    def _update_recursive(self, target: Dict, source: Dict):
        """Recursively update the target dictionary with values from the source dictionary.
        Args:
            target (dict): Target dictionary to be updated
            source (dict): Source dictionary with new values
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._update_recursive(target[key], value)
            else:
                target[key] = value

    def get(self, *keys, default=None):
        """Get a configuration value by keys.
        Args:
            *keys: Keys to access the nested configuration
            default: Default value if the key does not exist
        Returns:
            The configuration value or default if not found
        """
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, value, *keys):
        """Set a configuration value by keys.
        Args:
            value: Value to set
            *keys: Keys to access the nested configuration
        Returns:
        self: For method chaining
        """
        if not keys:
            raise ValueError("At least one key must be provided to set a value.")
        target = self._config
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value
        return self

    def save(self, config_path: Union[str, Path]):
        """Save the current configuration to a JSON file.
        Args:
            config_path (str or Path): Path to save the JSON configuration file
        Returns:
            self: For method chaining
        """
        config_path = Path(config_path)
        os.makedirs(config_path.parent, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(self._config, f, indent=4)
        return self

    def __getitem__(self, key: str) -> Any:
        """Get a configuration value by key.
        Args:
            key (str): Key to retrieve the value
        Returns:
            The configuration value
        Raises:
            KeyError: If the key does not exist
        """
        if key in self._config:
            return self._config[key]
        else:
            raise KeyError(f"Configuration key '{key}' not found.")

    def __setitem__(self, key: str, value: Any):
        """Set a configuration value by key.
        Args:
            key (str): Key to set the value
            value: Value to set
        """
        self._config[key] = value

    def __repr__(self) -> str:
        """String representation of the configuration.
        Returns:
            str: String representation of the configuration
        """
        return f"Config({self._config})"
    
    def __str__(self) -> str:
        """Returns:
            a formatted string of the configuration.
        """
        return json.dumps(self._config, indent=2)    
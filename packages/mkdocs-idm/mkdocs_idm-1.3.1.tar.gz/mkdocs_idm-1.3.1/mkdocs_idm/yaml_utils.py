"""
YAML utilities for handling Python object references in MkDocs configuration.

This module provides safe YAML parsing that can handle Python object references
like `!!python/name:material.extensions.emoji.twemoji` while maintaining security.
"""

import importlib
from typing import Any, Dict, List, Optional, Union

# Try to use ruamel.yaml first, fall back to PyYAML
try:
    from ruamel.yaml import YAML
    from ruamel.yaml.constructor import Constructor
    RUAMEL_AVAILABLE = True
except ImportError:
    RUAMEL_AVAILABLE = False

try:
    import yaml
    PYYAML_AVAILABLE = True
except ImportError:
    PYYAML_AVAILABLE = False


class SafePythonConstructor:
    """A safe constructor for Python object references in YAML."""
    
    # List of trusted modules that can be imported
    TRUSTED_MODULES = [
        'material.extensions.emoji',
        'pymdownx.emoji',
        'material.extensions',
        'pymdownx',
    ]
    
    @classmethod
    def construct_python_name(cls, loader, node):
        """Safely construct Python object references for trusted modules."""
        value = loader.construct_scalar(node)
        module_name, attr_name = value.rsplit('.', 1)
        
        # Check if the module is trusted
        if not any(module_name.startswith(trusted) for trusted in cls.TRUSTED_MODULES):
            raise ValueError(f"Untrusted module: {module_name}")
        
        try:
            module = importlib.import_module(module_name)
            return getattr(module, attr_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Failed to import {value}: {e}")


def get_yaml_parser(backend: str = "auto") -> Any:
    """
    Get a YAML parser with Python object reference support.
    
    Args:
        backend: The YAML parser to use ("auto", "ruamel", or "pyyaml")
    
    Returns:
        A configured YAML parser instance
    
    Raises:
        ImportError: If no suitable YAML parser is available
    """
    if backend == "auto":
        if RUAMEL_AVAILABLE:
            return _get_ruamel_parser()
        elif PYYAML_AVAILABLE:
            return _get_pyyaml_parser()
        else:
            raise ImportError("No YAML parser available. Install PyYAML or ruamel.yaml")
    
    elif backend == "ruamel":
        if not RUAMEL_AVAILABLE:
            raise ImportError("ruamel.yaml not available. Install with: pip install ruamel.yaml")
        return _get_ruamel_parser()
    
    elif backend == "pyyaml":
        if not PYYAML_AVAILABLE:
            raise ImportError("PyYAML not available. Install with: pip install PyYAML")
        return _get_pyyaml_parser()
    
    else:
        raise ValueError(f"Unknown backend: {backend}")


def _get_ruamel_parser() -> YAML:
    """Get a configured ruamel.yaml parser."""
    yaml_parser = YAML(typ='safe')
    
    # Add constructor for Python object references
    def construct_python_name(loader, node):
        return SafePythonConstructor.construct_python_name(loader, node)
    
    yaml_parser.constructor.add_constructor('tag:yaml.org,2002:python/name', construct_python_name)
    
    return yaml_parser


def _get_pyyaml_parser() -> Any:
    """Get a configured PyYAML parser."""
    # Add constructor for Python object references
    def construct_python_name(loader, node):
        return SafePythonConstructor.construct_python_name(loader, node)
    
    yaml.add_constructor('tag:yaml.org,2002:python/name', construct_python_name, yaml.SafeLoader)
    
    return yaml


def load_yaml_with_python_refs(content: str, backend: str = "auto") -> Union[Dict, List]:
    """
    Load YAML content that may contain Python object references.
    
    Args:
        content: YAML content as string
        backend: YAML parser backend to use
    
    Returns:
        Parsed YAML data
    
    Raises:
        ValueError: If Python object references are unsafe
        ImportError: If no suitable YAML parser is available
    """
    parser = get_yaml_parser(backend)
    
    if RUAMEL_AVAILABLE and isinstance(parser, YAML):
        return parser.load(content)
    else:
        return yaml.safe_load(content)


def load_yaml_file_with_python_refs(file_path: str, backend: str = "auto") -> Union[Dict, List]:
    """
    Load a YAML file that may contain Python object references.
    
    Args:
        file_path: Path to the YAML file
        backend: YAML parser backend to use
    
    Returns:
        Parsed YAML data
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If Python object references are unsafe
        ImportError: If no suitable YAML parser is available
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return load_yaml_with_python_refs(content, backend) 
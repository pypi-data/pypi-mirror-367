"""
Configuration settings for Code2Flow.

This module provides configuration options for customizing the behavior
of Code2Flow visualization and tracing.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Config:
    """Configuration settings for Code2Flow."""
    
    # Tracing settings
    capture_locals: bool = True
    capture_globals: bool = False
    max_depth: int = 10
    ignore_modules: List[str] = field(default_factory=lambda: ['code2flow', 'sys', 'traceback'])
    
    # Visualization settings
    default_layout: str = "hierarchical"
    figure_size: tuple = (12, 8)
    show_variables: bool = True
    show_returns: bool = True
    max_variable_display: int = 3
    
    # Export settings
    default_export_format: str = "mermaid"
    export_metadata: bool = True
    
    # Color scheme
    colors: Dict[str, str] = field(default_factory=lambda: {
        'start': '#90EE90',
        'end': '#FFB6C1', 
        'process': '#ffffff',
        'decision': '#FFE4B5',
        'call': '#87CEEB',
        'return': '#ffffff',
        'loop': '#ffffff',
        'exception': '#FFA07A'
    })
    
    @classmethod
    def default(cls) -> 'Config':
        """Get default configuration."""
        return cls()
        
    @classmethod  
    def minimal(cls) -> 'Config':
        """Get minimal configuration for basic tracing."""
        return cls(
            capture_locals=False,
            capture_globals=False,
            max_depth=5,
            show_variables=False
        )
        
    @classmethod
    def detailed(cls) -> 'Config':
        """Get detailed configuration for comprehensive tracing."""
        return cls(
            capture_locals=True,
            capture_globals=True,
            max_depth=20,
            show_variables=True,
            show_returns=True
        )

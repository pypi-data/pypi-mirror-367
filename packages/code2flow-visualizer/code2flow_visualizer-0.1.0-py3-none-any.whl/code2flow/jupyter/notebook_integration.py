"""
Jupyter notebook integration for Code2Flow.

This module provides integration with Jupyter notebooks for interactive
code visualization.
"""

from typing import Optional
from ..core.flow import CodeFlow


class JupyterVisualizer:
    """Jupyter notebook integration for Code2Flow."""
    
    def __init__(self, flow: Optional[CodeFlow] = None):
        self.flow = flow or CodeFlow()
        
    def display(self):
        """Display visualization in Jupyter notebook."""
        # TODO: Implement Jupyter-specific display
        print("Jupyter integration coming soon!")
        print("For now, use the regular FlowVisualizer.display() method")
        
    def create_widget(self):
        """Create interactive widget for Jupyter."""
        # TODO: Implement interactive widget
        print("Interactive widget coming soon!")

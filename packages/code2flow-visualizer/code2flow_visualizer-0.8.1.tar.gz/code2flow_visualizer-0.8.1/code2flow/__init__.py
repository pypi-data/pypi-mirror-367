"""
Code2Flow: Real-Time Code Execution Visualizer for Python

A powerful debugging and visualization library that generates interactive 
flowcharts of Python code execution.
"""

__version__ = "0.1.0"
__author__ = "Aryan Mishra"
__email__ = "your.email@example.com"

# Core components
from .core.tracer import CodeTracer
from .core.flow import CodeFlow
from .visualizer.flow_visualizer import FlowVisualizer
from .decorators.visualize import visualize

# Export formats
from .exporters.mermaid_exporter import MermaidExporter
from .exporters.graphviz_exporter import GraphvizExporter
from .exporters.image_exporter import ImageExporter

# Jupyter integration
from .jupyter.notebook_integration import JupyterVisualizer

# Configuration
from .config.settings import Config

__all__ = [
    # Core API
    "CodeTracer",
    "CodeFlow", 
    "FlowVisualizer",
    "visualize",
    
    # Exporters
    "MermaidExporter",
    "GraphvizExporter", 
    "ImageExporter",
    
    # Jupyter
    "JupyterVisualizer",
    
    # Config
    "Config",
    
    # Version info
    "__version__",
    "__author__",
    "__email__",
]

# Convenience imports for common use cases
def trace(func, *args, **kwargs):
    """Quick trace function execution and return flow object."""
    flow = CodeFlow()
    flow.trace_function(func, *args, **kwargs)
    return flow

def quick_visualize(func, *args, **kwargs):
    """Quick visualization of function execution."""
    flow = CodeFlow()
    result = flow.trace_function(func, *args, **kwargs)
    visualizer = FlowVisualizer(flow)
    visualizer.display()
    return result

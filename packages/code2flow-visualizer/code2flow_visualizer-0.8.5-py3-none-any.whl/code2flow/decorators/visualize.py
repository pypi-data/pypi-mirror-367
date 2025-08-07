"""
Decorator for easy function visualization in Code2Flow.

This module provides the @visualize decorator that can be applied to functions
to automatically trace and visualize their execution flow.
"""

import functools
from typing import Any, Callable, Dict, Optional, TypeVar, Union
import inspect

from ..core.flow import CodeFlow
from ..visualizer.flow_visualizer import FlowVisualizer

F = TypeVar('F', bound=Callable[..., Any])


class VisualizeConfig:
    """Configuration for the @visualize decorator."""
    
    def __init__(
        self,
        show_variables: bool = True,
        show_returns: bool = True,
        max_depth: int = 10,
        export_format: Optional[str] = None,
        export_path: Optional[str] = None,
        auto_display: bool = True,
        capture_globals: bool = False,
        ignore_modules: Optional[list] = None
    ):
        self.show_variables = show_variables
        self.show_returns = show_returns
        self.max_depth = max_depth
        self.export_format = export_format
        self.export_path = export_path
        self.auto_display = auto_display
        self.capture_globals = capture_globals
        self.ignore_modules = ignore_modules or []


def visualize(
    func: Optional[F] = None,
    *,
    show_variables: bool = True,
    show_returns: bool = True,
    max_depth: int = 10,
    export_format: Optional[str] = None,
    export_path: Optional[str] = None,
    auto_display: bool = True,
    capture_globals: bool = False,
    ignore_modules: Optional[list] = None,
    config: Optional[VisualizeConfig] = None
) -> Union[F, Callable[[F], F]]:
    """
    Decorator to automatically visualize function execution flow.
    
    Can be used with or without parameters:
    
    @visualize
    def my_function():
        pass
        
    @visualize(show_variables=False, export_format="mermaid")
    def my_function():
        pass
    
    Args:
        func: Function to decorate (when used without parameters)
        show_variables: Whether to show variable values in visualization
        show_returns: Whether to show return values
        max_depth: Maximum recursion depth to trace
        export_format: Export format ("mermaid", "graphviz", "png", "svg")
        export_path: Path to save exported visualization
        auto_display: Whether to automatically display visualization
        capture_globals: Whether to capture global variables
        ignore_modules: List of module names to ignore during tracing
        config: Optional VisualizeConfig object with all settings
    
    Returns:
        Decorated function or decorator function
    """
    
    # Use config if provided, otherwise create from parameters
    if config:
        cfg = config
    else:
        cfg = VisualizeConfig(
            show_variables=show_variables,
            show_returns=show_returns,
            max_depth=max_depth,
            export_format=export_format,
            export_path=export_path,
            auto_display=auto_display,
            capture_globals=capture_globals,
            ignore_modules=ignore_modules
        )
    
    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # Create flow tracer
            flow = CodeFlow()
            flow.tracer.capture_globals = cfg.capture_globals
            flow.tracer.max_depth = cfg.max_depth
            flow.tracer.ignore_modules.extend(cfg.ignore_modules)
            
            # Trace function execution
            result = flow.trace_function(f, *args, **kwargs)
            
            # Store flow for later access
            wrapper._last_flow = flow
            wrapper._last_result = result
            
            # Auto-display if requested
            if cfg.auto_display:
                try:
                    visualizer = FlowVisualizer(flow)
                    visualizer.display()
                except Exception as e:
                    print(f"Could not display visualization: {e}")
            
            # Auto-export if requested
            if cfg.export_format and cfg.export_path:
                try:
                    _export_flow(flow, cfg.export_format, cfg.export_path)
                except Exception as e:
                    print(f"Could not export visualization: {e}")
            
            return result
            
        # Add methods to access visualization
        wrapper.get_flow = lambda: getattr(wrapper, '_last_flow', None)
        wrapper.get_visualization = lambda: _create_visualizer(wrapper.get_flow())
        wrapper.export = lambda fmt, path: _export_flow(wrapper.get_flow(), fmt, path)
        wrapper.show = lambda: _show_flow(wrapper.get_flow())
        
        # Store configuration
        wrapper._visualize_config = cfg
        wrapper._original_function = f
        
        return wrapper
    
    # Handle both @visualize and @visualize() syntax
    if func is None:
        return decorator
    else:
        return decorator(func)


def _create_visualizer(flow: Optional[CodeFlow]) -> Optional[FlowVisualizer]:
    """Create a visualizer from a flow object."""
    if flow is None:
        return None
    return FlowVisualizer(flow)


def _export_flow(flow: Optional[CodeFlow], format: str, path: str) -> None:
    """Export flow in the specified format."""
    if flow is None:
        raise ValueError("No flow data available")
        
    format = format.lower()
    
    if format == "mermaid":
        flow.export_mermaid(path)
    elif format == "graphviz" or format == "dot":
        flow.export_graphviz(path)
    elif format in ["png", "svg", "pdf", "jpg", "jpeg"]:
        flow.export_image(path, format)
    else:
        raise ValueError(f"Unsupported export format: {format}")


def _show_flow(flow: Optional[CodeFlow]) -> None:
    """Display the flow visualization."""
    if flow is None:
        print("No flow data available")
        return
        
    try:
        visualizer = FlowVisualizer(flow)
        visualizer.display()
    except Exception as e:
        print(f"Could not display visualization: {e}")


# Convenience functions for interactive use
def get_last_visualization() -> Optional[FlowVisualizer]:
    """Get the visualization from the last decorated function call."""
    # This would need to be implemented with global state tracking
    # For now, users should use the wrapper methods
    print("Use function_name.get_visualization() to get the visualization")
    return None


def export_last_visualization(format: str, path: str) -> None:
    """Export the last visualization."""
    # This would need to be implemented with global state tracking  
    # For now, users should use the wrapper methods
    print("Use function_name.export(format, path) to export the visualization")


# Example usage demonstrations
if __name__ == "__main__":
    # Example 1: Basic usage
    @visualize
    def fibonacci(n):
        """Calculate fibonacci number recursively."""
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    # Example 2: With configuration
    @visualize(
        show_variables=True,
        export_format="mermaid",
        export_path="fibonacci_flow.md",
        max_depth=5
    )
    def fibonacci_export(n):
        """Calculate fibonacci with export."""
        if n <= 1:
            return n
        return fibonacci_export(n-1) + fibonacci_export(n-2)
    
    # Example 3: Manual control
    @visualize(auto_display=False)
    def manual_control_function(x, y):
        """Function with manual visualization control."""
        result = x + y
        if result > 10:
            result = result * 2
        return result
    
    # Usage examples:
    print("Running examples...")
    
    # Basic usage - auto-displays
    result1 = fibonacci(4)
    print(f"Fibonacci(4) = {result1}")
    
    # Access the flow data
    flow = fibonacci.get_flow()
    if flow:
        print(f"Flow statistics: {flow.get_flow_statistics()}")
    
    # Manual control
    result2 = manual_control_function(5, 8)
    print(f"Manual function result: {result2}")
    
    # Show visualization manually
    manual_control_function.show()
    
    # Export manually
    try:
        manual_control_function.export("png", "manual_flow.png")
        print("Exported to manual_flow.png")
    except Exception as e:
        print(f"Export failed: {e}")

"""
Core execution tracer for Code2Flow.

This module provides the CodeTracer class that monitors Python code execution
and captures variable states, function calls, and control flow.
"""

import sys
import inspect
import ast
import types
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import traceback


@dataclass
class ExecutionStep:
    """Represents a single step in code execution."""
    step_id: int
    filename: str
    line_number: int
    function_name: str
    code_context: str
    event_type: str  # 'call', 'line', 'return', 'exception'
    local_vars: Dict[str, Any] = field(default_factory=dict)
    global_vars: Dict[str, Any] = field(default_factory=dict)
    stack_depth: int = 0
    timestamp: float = 0.0
    return_value: Any = None
    exception_info: Optional[Tuple] = None


@dataclass 
class FunctionCall:
    """Represents a function call in the execution flow."""
    function_name: str
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    start_step: int
    end_step: Optional[int] = None
    return_value: Any = None
    exception: Optional[Exception] = None


class CodeTracer:
    """
    Traces Python code execution and captures execution flow.
    
    This class uses sys.settrace to monitor code execution and build
    a comprehensive execution trace including variable states and control flow.
    """
    
    def __init__(self, capture_locals: bool = True, capture_globals: bool = False,
                 max_depth: int = 10, ignore_modules: Optional[List[str]] = None):
        """
        Initialize the CodeTracer.
        
        Args:
            capture_locals: Whether to capture local variables
            capture_globals: Whether to capture global variables  
            max_depth: Maximum stack depth to trace
            ignore_modules: List of module names to ignore during tracing
        """
        self.capture_locals = capture_locals
        self.capture_globals = capture_globals
        self.max_depth = max_depth
        self.ignore_modules = ignore_modules or ['code2flow', 'sys', 'traceback']
        
        # Execution state
        self.steps: List[ExecutionStep] = []
        self.function_calls: List[FunctionCall] = []
        self.current_step_id = 0
        self.call_stack: List[FunctionCall] = []
        self.is_tracing = False
        
        # Original trace function (to restore later)
        self._original_trace = None
        
    def start_trace(self) -> None:
        """Start tracing code execution."""
        if self.is_tracing:
            return
            
        self._original_trace = sys.gettrace()
        sys.settrace(self._trace_handler)
        self.is_tracing = True
        self.current_step_id = 0
        self.steps.clear()
        self.function_calls.clear()
        self.call_stack.clear()
        
    def stop_trace(self) -> None:
        """Stop tracing code execution."""
        if not self.is_tracing:
            return
            
        sys.settrace(self._original_trace)
        self.is_tracing = False
        
    def _trace_handler(self, frame: types.FrameType, event: str, arg: Any) -> Optional[Callable]:
        """
        Handle trace events from sys.settrace.
        
        Args:
            frame: Current execution frame
            event: Type of event ('call', 'line', 'return', 'exception')  
            arg: Event-specific argument
            
        Returns:
            Trace function to continue tracing
        """
        try:
            # Check if we should ignore this frame
            if self._should_ignore_frame(frame):
                return self._trace_handler
                
            # Check max depth
            if len(self.call_stack) >= self.max_depth:
                return None
                
            # Create execution step
            step = self._create_execution_step(frame, event, arg)
            self.steps.append(step)
            
            # Handle different event types
            if event == 'call':
                self._handle_call_event(frame, step)
            elif event == 'return':
                self._handle_return_event(frame, step, arg)
            elif event == 'exception':
                self._handle_exception_event(frame, step, arg)
                
            return self._trace_handler
            
        except Exception as e:
            # Don't let tracing errors break the program
            print(f"Code2Flow tracing error: {e}")
            return None
            
    def _should_ignore_frame(self, frame: types.FrameType) -> bool:
        """Check if frame should be ignored during tracing."""
        filename = frame.f_code.co_filename
        function_name = frame.f_code.co_name
        
        # Always ignore built-in functions
        if '<built-in>' in filename:
            return True
            
        # Always ignore the tracer's own methods
        if function_name.startswith('_trace') or function_name in ['start_trace', 'stop_trace']:
            return True
            
        # Ignore modules in ignore list, but be more specific
        for module in self.ignore_modules:
            if module in filename and 'site-packages' in filename:
                return True
                
        return False
        
    def _create_execution_step(self, frame: types.FrameType, event: str, arg: Any) -> ExecutionStep:
        """Create an ExecutionStep from frame information."""
        import time
        
        # Get code context
        try:
            lines, start_line = inspect.getsourcelines(frame.f_code)
            current_line_idx = frame.f_lineno - start_line
            if 0 <= current_line_idx < len(lines):
                code_context = lines[current_line_idx].strip()
            else:
                code_context = ""
        except:
            code_context = ""
            
        # Capture variables
        local_vars = {}
        global_vars = {}
        
        if self.capture_locals:
            local_vars = self._safe_capture_vars(frame.f_locals)
            
        if self.capture_globals:
            global_vars = self._safe_capture_vars(frame.f_globals)
            
        step = ExecutionStep(
            step_id=self.current_step_id,
            filename=frame.f_code.co_filename,
            line_number=frame.f_lineno,
            function_name=frame.f_code.co_name,
            code_context=code_context,
            event_type=event,
            local_vars=local_vars,
            global_vars=global_vars,
            stack_depth=len(self.call_stack),
            timestamp=time.time(),
            return_value=arg if event == 'return' else None,
            exception_info=arg if event == 'exception' else None
        )
        
        self.current_step_id += 1
        return step
        
    def _safe_capture_vars(self, var_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Safely capture variables, handling non-serializable objects."""
        safe_vars = {}
        
        for name, value in var_dict.items():
            try:
                # Skip private/internal variables
                if name.startswith('__') and name.endswith('__'):
                    continue
                    
                # Try to get a safe representation
                safe_vars[name] = self._get_safe_repr(value)
                
            except Exception:
                safe_vars[name] = "<unable to capture>"
                
        return safe_vars
        
    def _get_safe_repr(self, value: Any) -> Any:
        """Get a safe string representation of a value."""
        try:
            # For basic types, return as-is
            if isinstance(value, (int, float, str, bool, type(None))):
                return value
                
            # For collections, limit size and recursion
            if isinstance(value, (list, tuple)):
                if len(value) > 10:
                    return f"{type(value).__name__}({len(value)} items)"
                return [self._get_safe_repr(item) for item in value[:5]]
                
            if isinstance(value, dict):
                if len(value) > 10:
                    return f"dict({len(value)} items)"
                return {k: self._get_safe_repr(v) for k, v in list(value.items())[:5]}
                
            # For objects, show type and basic info
            return f"<{type(value).__name__} object>"
            
        except:
            return "<unable to represent>"
            
    def _handle_call_event(self, frame: types.FrameType, step: ExecutionStep) -> None:
        """Handle function call events."""
        try:
            # Extract function arguments
            code = frame.f_code
            arg_names = code.co_varnames[:code.co_argcount]
            args = tuple(frame.f_locals.get(name) for name in arg_names)
            
            # Create function call record
            func_call = FunctionCall(
                function_name=step.function_name,
                args=args,
                kwargs={},  # TODO: Extract kwargs
                start_step=step.step_id
            )
            
            self.call_stack.append(func_call)
            self.function_calls.append(func_call)
            
        except Exception as e:
            # Don't break tracing for call handling errors
            pass
            
    def _handle_return_event(self, frame: types.FrameType, step: ExecutionStep, return_value: Any) -> None:
        """Handle function return events."""
        if self.call_stack:
            func_call = self.call_stack.pop()
            func_call.end_step = step.step_id
            func_call.return_value = return_value
            
    def _handle_exception_event(self, frame: types.FrameType, step: ExecutionStep, exc_info: Tuple) -> None:
        """Handle exception events."""
        if self.call_stack:
            func_call = self.call_stack[-1]
            func_call.exception = exc_info[1]
            
    def trace_function(self, func: Callable, *args, **kwargs) -> Any:
        """
        Trace execution of a specific function.
        
        Args:
            func: Function to trace
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function return value
        """
        self.start_trace()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            self.stop_trace()
            
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of the execution trace."""
        return {
            'total_steps': len(self.steps),
            'function_calls': len(self.function_calls),
            'max_stack_depth': max((step.stack_depth for step in self.steps), default=0),
            'unique_functions': len(set(step.function_name for step in self.steps)),
            'execution_time': self.steps[-1].timestamp - self.steps[0].timestamp if self.steps else 0
        }
        
    def __enter__(self):
        """Context manager entry."""
        self.start_trace()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_trace()

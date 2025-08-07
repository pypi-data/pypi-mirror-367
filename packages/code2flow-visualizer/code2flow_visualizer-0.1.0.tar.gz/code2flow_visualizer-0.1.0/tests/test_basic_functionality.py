"""
Test suite for Code2Flow basic functionality.
Tests 1-20: Core tracing and basic operations.
"""

import pytest
import sys
import os
from unittest.mock import patch

from code2flow import CodeFlow, CodeTracer, visualize, trace
from code2flow.core.flow import NodeType, FlowNode, FlowEdge
from code2flow.core.tracer import ExecutionStep, FunctionCall


class TestBasicFunctionality:
    """Tests 1-20: Core functionality and basic operations."""
    
    def test_01_codeflow_initialization(self):
        """Test 1: CodeFlow instance initialization."""
        flow = CodeFlow()
        assert flow is not None
        assert isinstance(flow, CodeFlow)
        assert len(flow.nodes) == 0
        assert len(flow.edges) == 0
        assert len(flow.execution_steps) == 0
    
    def test_02_codetracer_initialization(self):
        """Test 2: CodeTracer instance initialization."""
        tracer = CodeTracer()
        assert tracer is not None
        assert isinstance(tracer, CodeTracer)
        assert tracer.capture_locals == True
        assert tracer.capture_globals == False
        assert tracer.max_depth == 10
        assert tracer.is_tracing == False
    
    def test_03_simple_function_tracing(self, code_flow, sample_functions):
        """Test 3: Basic function tracing functionality."""
        simple_add = sample_functions['simple_add']
        result = code_flow.trace_function(simple_add, 5, 3)
        
        assert result == 8
        assert len(code_flow.execution_steps) > 0
        assert len(code_flow.nodes) > 0
        assert len(code_flow.edges) > 0
    
    def test_04_execution_steps_capture(self, code_flow, sample_functions):
        """Test 4: Execution steps are properly captured."""
        simple_add = sample_functions['simple_add']
        code_flow.trace_function(simple_add, 10, 20)
        
        steps = code_flow.execution_steps
        assert len(steps) > 0
        
        # Check that we have different event types
        event_types = set(step.event_type for step in steps)
        assert 'call' in event_types
        assert 'line' in event_types or 'return' in event_types
    
    def test_05_variable_capture(self, code_flow):
        """Test 5: Local variables are captured correctly."""
        def test_vars(x, y):
            z = x + y
            w = z * 2
            return w
        
        code_flow.trace_function(test_vars, 3, 4)
        
        # Check that variables were captured
        variable_found = False
        for step in code_flow.execution_steps:
            if 'z' in step.local_vars:
                assert step.local_vars['z'] == 7
                variable_found = True
                break
        
        assert variable_found, "Variable 'z' should be captured"
    
    def test_06_recursive_function_tracing(self, code_flow, sample_functions):
        """Test 6: Recursive functions are traced correctly."""
        factorial = sample_functions['simple_factorial']
        result = code_flow.trace_function(factorial, 4)
        
        assert result == 24
        assert len(code_flow.execution_steps) > 4  # Should have multiple recursive calls
        
        # Check for multiple function calls
        call_events = [step for step in code_flow.execution_steps if step.event_type == 'call']
        assert len(call_events) >= 4  # Should have at least 4 calls for factorial(4)
    
    def test_07_conditional_logic_tracing(self, code_flow, sample_functions):
        """Test 7: Conditional logic creates decision nodes."""
        conditional = sample_functions['conditional_function']
        
        # Test different branches
        code_flow.trace_function(conditional, 15)  # Should trigger first branch
        
        # Check for decision nodes
        decision_nodes = code_flow.get_nodes_by_type(NodeType.DECISION)
        assert len(decision_nodes) > 0, "Should have decision nodes for conditional logic"
    
    def test_08_loop_tracing(self, code_flow, sample_functions):
        """Test 8: Loop constructs are traced properly."""
        loop_func = sample_functions['loop_function']
        result = code_flow.trace_function(loop_func, 5)
        
        assert result == 10  # 0+1+2+3+4
        assert len(code_flow.execution_steps) > 5
        
        # Should have process nodes for loop body
        process_nodes = code_flow.get_nodes_by_type(NodeType.PROCESS)
        assert len(process_nodes) > 0
    
    def test_09_flow_statistics(self, code_flow, sample_functions):
        """Test 9: Flow statistics are calculated correctly."""
        factorial = sample_functions['simple_factorial']
        code_flow.trace_function(factorial, 3)
        
        stats = code_flow.get_flow_statistics()
        
        assert 'total_nodes' in stats
        assert 'total_edges' in stats
        assert 'node_types' in stats
        assert stats['total_nodes'] > 0
        assert stats['total_edges'] > 0
    
    def test_10_variable_changes_tracking(self, code_flow):
        """Test 10: Variable changes are tracked correctly."""
        def counter_function(n):
            counter = 0
            for i in range(n):
                counter += 1
            return counter
        
        code_flow.trace_function(counter_function, 3)
        changes = code_flow.get_variable_changes('counter')
        
        assert len(changes) > 0, "Should track changes to 'counter' variable"
        
        # Check that counter increases
        values = [change[1] for change in changes]
        assert 0 in values  # Initial value
        assert max(values) >= 3  # Final value
    
    def test_11_node_types_classification(self, code_flow, sample_functions):
        """Test 11: Different node types are classified correctly."""
        conditional = sample_functions['conditional_function']
        code_flow.trace_function(conditional, 8)
        
        # Check for start and end nodes
        start_nodes = code_flow.get_nodes_by_type(NodeType.START)
        end_nodes = code_flow.get_nodes_by_type(NodeType.END)
        call_nodes = code_flow.get_nodes_by_type(NodeType.CALL)
        
        assert len(start_nodes) == 1, "Should have exactly one START node"
        assert len(end_nodes) == 1, "Should have exactly one END node"
        assert len(call_nodes) >= 1, "Should have at least one CALL node"
    
    def test_12_trace_helper_function(self, sample_functions):
        """Test 12: trace() helper function works correctly."""
        simple_add = sample_functions['simple_add']
        flow = trace(simple_add, 7, 8)
        
        assert isinstance(flow, CodeFlow)
        assert len(flow.execution_steps) > 0
        assert len(flow.nodes) > 0
    
    def test_13_visualize_decorator_basic(self, sample_functions):
        """Test 13: @visualize decorator basic functionality."""
        @visualize(auto_display=False)
        def decorated_add(a, b):
            return a + b
        
        result = decorated_add(5, 10)
        assert result == 15
        
        # Check that flow was captured
        flow = decorated_add.get_flow()
        assert flow is not None
        assert len(flow.execution_steps) > 0
    
    def test_14_execution_path_analysis(self, code_flow, sample_functions):
        """Test 14: Execution path can be analyzed."""
        simple_add = sample_functions['simple_add']
        code_flow.trace_function(simple_add, 1, 2)
        
        path = code_flow.get_execution_path()
        assert isinstance(path, list)
        assert len(path) > 0
        
        # Path should start with START node and end with END node
        start_nodes = code_flow.get_nodes_by_type(NodeType.START)
        end_nodes = code_flow.get_nodes_by_type(NodeType.END)
        
        if start_nodes and end_nodes:
            assert path[0] == start_nodes[0].node_id
            assert path[-1] == end_nodes[0].node_id
    
    def test_15_nested_function_calls(self, code_flow):
        """Test 15: Nested function calls are handled correctly."""
        def inner_func(x):
            return x * 2
        
        def outer_func(y):
            return inner_func(y) + 5
        
        result = code_flow.trace_function(outer_func, 3)
        assert result == 11  # (3 * 2) + 5
        
        # Should have multiple function calls
        call_events = [step for step in code_flow.execution_steps if step.event_type == 'call']
        assert len(call_events) >= 2  # outer_func and inner_func
    
    def test_16_empty_function_tracing(self, code_flow):
        """Test 16: Empty functions are traced correctly."""
        def empty_function():
            pass
        
        result = code_flow.trace_function(empty_function)
        assert result is None
        assert len(code_flow.execution_steps) > 0  # Should still capture call/return
    
    def test_17_function_with_return_value(self, code_flow):
        """Test 17: Return values are captured correctly."""
        def return_constant():
            return 42
        
        result = code_flow.trace_function(return_constant)
        assert result == 42
        
        # Check for return events
        return_events = [step for step in code_flow.execution_steps if step.event_type == 'return']
        assert len(return_events) > 0
        
        # Check that return value is captured
        return_step = return_events[0]
        assert return_step.return_value == 42
    
    def test_18_multiple_parameters_function(self, code_flow):
        """Test 18: Functions with multiple parameters work correctly."""
        def multi_param_func(a, b, c, d=10, e=20):
            return a + b + c + d + e
        
        result = code_flow.trace_function(multi_param_func, 1, 2, 3, d=15)
        assert result == 41  # 1+2+3+15+20
        
        # Check that parameters were captured
        call_events = [step for step in code_flow.execution_steps if step.event_type == 'call']
        assert len(call_events) > 0
        
        call_step = call_events[0]
        assert 'a' in call_step.local_vars
        assert call_step.local_vars['a'] == 1
    
    def test_19_tracer_start_stop_methods(self, code_tracer):
        """Test 19: Tracer start/stop methods work correctly."""
        assert not code_tracer.is_tracing
        
        code_tracer.start_trace()
        assert code_tracer.is_tracing
        
        code_tracer.stop_trace()
        assert not code_tracer.is_tracing
    
    def test_20_execution_step_data_integrity(self, code_flow):
        """Test 20: ExecutionStep data integrity and completeness."""
        def test_function(x):
            y = x + 1
            return y
        
        code_flow.trace_function(test_function, 5)
        
        for step in code_flow.execution_steps:
            # Each step should have required fields
            assert hasattr(step, 'step_id')
            assert hasattr(step, 'filename')
            assert hasattr(step, 'line_number')
            assert hasattr(step, 'function_name')
            assert hasattr(step, 'event_type')
            assert hasattr(step, 'timestamp')
            
            # step_id should be non-negative
            assert step.step_id >= 0
            
            # event_type should be valid
            assert step.event_type in ['call', 'line', 'return', 'exception']
            
            # timestamp should be reasonable
            assert step.timestamp > 0

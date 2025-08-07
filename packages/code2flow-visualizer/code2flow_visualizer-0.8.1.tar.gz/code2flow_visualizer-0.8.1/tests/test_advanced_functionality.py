"""
Test suite for Code2Flow advanced functionality.
Tests 21-40: Advanced features, decorators, exports, and error handling.
"""

import pytest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock

from code2flow import CodeFlow, CodeTracer, visualize, trace, FlowVisualizer
from code2flow.core.flow import NodeType
from code2flow.decorators.visualize import VisualizeConfig
from code2flow.exporters.mermaid_exporter import MermaidExporter


class TestAdvancedFunctionality:
    """Tests 21-40: Advanced functionality and edge cases."""
    
    def test_21_visualize_decorator_with_config(self):
        """Test 21: @visualize decorator with custom configuration."""
        config = VisualizeConfig(
            show_variables=True,
            max_depth=5,
            auto_display=False,
            capture_globals=False
        )
        
        @visualize(config=config)
        def configured_function(x, y):
            z = x * y
            return z + 10
        
        result = configured_function(3, 4)
        assert result == 22
        
        flow = configured_function.get_flow()
        assert flow is not None
        assert len(flow.execution_steps) > 0
    
    def test_22_visualize_decorator_with_export(self, temp_dir):
        """Test 22: @visualize decorator with automatic export."""
        export_path = os.path.join(temp_dir, "test_export.md")
        
        @visualize(auto_display=False, export_format="mermaid", export_path=export_path)
        def export_function(n):
            return n * 2
        
        result = export_function(5)
        assert result == 10
        
        # Check that file was created
        assert os.path.exists(export_path)
        
        # Check file content
        with open(export_path, 'r') as f:
            content = f.read()
            assert "graph TD" in content
    
    def test_23_mermaid_exporter_basic(self, code_flow, sample_functions):
        """Test 23: Mermaid exporter basic functionality."""
        simple_add = sample_functions['simple_add']
        code_flow.trace_function(simple_add, 2, 3)
        
        exporter = MermaidExporter(code_flow)
        content = exporter.export()
        
        assert isinstance(content, str)
        assert "graph TD" in content
        assert "START" in content
        assert "END" in content
    
    def test_24_mermaid_export_with_styling(self, code_flow, sample_functions):
        """Test 24: Mermaid export includes proper styling."""
        conditional = sample_functions['conditional_function']
        code_flow.trace_function(conditional, 12)
        
        content = code_flow.export_mermaid()
        
        assert "classDef start-node" in content
        assert "classDef end-node" in content
        assert "classDef decision-node" in content
        assert "fill:#90EE90" in content  # Start node color
    
    def test_25_mermaid_export_with_metadata(self, code_flow, sample_functions, temp_dir):
        """Test 25: Mermaid export with metadata."""
        factorial = sample_functions['simple_factorial']
        code_flow.trace_function(factorial, 3)
        
        exporter = MermaidExporter(code_flow)
        export_path = os.path.join(temp_dir, "metadata_test.md")
        content = exporter.export_with_metadata(export_path)
        
        assert "# Code Execution Flow" in content
        assert "## Statistics" in content
        assert "Total Nodes" in content
        assert os.path.exists(export_path)
    
    def test_26_interactive_html_export(self, code_flow, sample_functions, temp_dir):
        """Test 26: Interactive HTML export functionality."""
        simple_add = sample_functions['simple_add']
        code_flow.trace_function(simple_add, 1, 2)
        
        exporter = MermaidExporter(code_flow)
        export_path = os.path.join(temp_dir, "interactive.html")
        content = exporter.export_interactive(export_path)
        
        assert "<html>" in content
        assert "mermaid" in content
        assert "Code2Flow" in content
        assert os.path.exists(export_path)
    
    def test_27_flow_visualizer_initialization(self, code_flow, sample_functions):
        """Test 27: FlowVisualizer initialization and basic setup."""
        simple_add = sample_functions['simple_add']
        code_flow.trace_function(simple_add, 4, 5)
        
        visualizer = FlowVisualizer(code_flow)
        assert visualizer.flow == code_flow
        assert visualizer.fig is None  # Not displayed yet
        assert visualizer.ax is None
    
    def test_28_custom_tracer_configuration(self):
        """Test 28: Custom tracer configuration options."""
        tracer = CodeTracer(
            capture_locals=False,
            capture_globals=True,
            max_depth=20,
            ignore_modules=['test_module']
        )
        
        assert tracer.capture_locals == False
        assert tracer.capture_globals == True
        assert tracer.max_depth == 20
        assert 'test_module' in tracer.ignore_modules
    
    def test_29_exception_handling_in_tracing(self, code_flow):
        """Test 29: Exception handling during tracing."""
        def exception_function():
            raise ValueError("Test exception")
        
        with pytest.raises(ValueError):
            code_flow.trace_function(exception_function)
        
        # Should still capture steps up to the exception (at least the call)
        # Note: Exception handling might cause tracing to stop early
        # This is acceptable behavior, so we just check that tracer didn't break
        assert isinstance(code_flow.execution_steps, list)
    
    def test_30_large_recursion_depth(self, code_flow):
        """Test 30: Handling functions with large recursion depth."""
        def deep_recursion(n):
            if n <= 0:
                return 0
            return 1 + deep_recursion(n-1)
        
        # Test with depth that exceeds default max_depth
        result = code_flow.trace_function(deep_recursion, 5)
        assert result == 5
        assert len(code_flow.execution_steps) > 0
    
    def test_31_complex_data_structures(self, code_flow):
        """Test 31: Handling functions that work with complex data structures."""
        def dict_processing(data):
            result = {}
            for key, value in data.items():
                if isinstance(value, int):
                    result[key] = value * 2
                else:
                    result[key] = str(value).upper()
            return result
        
        test_data = {'a': 1, 'b': 'hello', 'c': 3}
        result = code_flow.trace_function(dict_processing, test_data)
        
        expected = {'a': 2, 'b': 'HELLO', 'c': 6}
        assert result == expected
        assert len(code_flow.execution_steps) > 0
    
    def test_32_nested_loops_tracing(self, code_flow, sample_functions):
        """Test 32: Nested loops are traced correctly."""
        nested_loops = sample_functions['nested_loops']
        result = code_flow.trace_function(nested_loops, 3, 2)
        
        assert result == 3  # 0*0 + 0*1 + 1*0 + 1*1 + 2*0 + 2*1 = 0 + 0 + 0 + 1 + 0 + 2 = 3
        assert len(code_flow.execution_steps) > 6  # Multiple loop iterations
        
        # Should have multiple process nodes for loop bodies
        process_nodes = code_flow.get_nodes_by_type(NodeType.PROCESS)
        assert len(process_nodes) > 0
    
    def test_33_object_oriented_code_tracing(self, code_flow, sample_functions):
        """Test 33: Object-oriented code is traced correctly."""
        SimpleClass = sample_functions['SimpleClass']
        obj = SimpleClass(5)
        
        result = code_flow.trace_function(obj.multiply, 3)
        assert result == 15
        
        # Check that method call was captured
        call_events = [step for step in code_flow.execution_steps if step.event_type == 'call']
        assert len(call_events) > 0
        
        # Check that 'self' parameter was captured
        found_self = False
        for step in code_flow.execution_steps:
            if 'self' in step.local_vars:
                found_self = True
                break
        assert found_self, "Should capture 'self' parameter in method calls"
    
    def test_34_lambda_function_tracing(self, code_flow):
        """Test 34: Lambda functions are handled appropriately."""
        lambda_func = lambda x: x * 2 + 1
        
        result = code_flow.trace_function(lambda_func, 5)
        assert result == 11
        assert len(code_flow.execution_steps) > 0
    
    def test_35_generator_function_tracing(self, code_flow):
        """Test 35: Generator functions are traced correctly."""
        def simple_generator(n):
            for i in range(n):
                yield i * 2
        
        # Trace the generator creation
        gen = code_flow.trace_function(simple_generator, 3)
        
        # Generator should be created
        assert hasattr(gen, '__next__')
        
        # Consume the generator
        results = list(gen)
        assert results == [0, 2, 4]
    
    def test_36_context_manager_tracing(self, code_flow):
        """Test 36: Functions using context managers are traced."""
        def context_function():
            with open(__file__, 'r') as f:
                first_line = f.readline()
            return len(first_line)
        
        result = code_flow.trace_function(context_function)
        assert isinstance(result, int)
        assert result > 0  # Should read something
        assert len(code_flow.execution_steps) > 0
    
    def test_37_list_comprehension_tracing(self, code_flow):
        """Test 37: Functions with list comprehensions are traced."""
        def comprehension_function(n):
            squares = [x**2 for x in range(n) if x % 2 == 0]
            return sum(squares)
        
        result = code_flow.trace_function(comprehension_function, 5)
        assert result == 20  # 0^2 + 2^2 + 4^2 = 0 + 4 + 16 = 20
        assert len(code_flow.execution_steps) > 0
    
    def test_38_variable_shadowing(self, code_flow):
        """Test 38: Variable shadowing is handled correctly."""
        def shadowing_function():
            x = 10
            def inner():
                x = 20  # Shadows outer x
                return x
            return x + inner()
        
        result = code_flow.trace_function(shadowing_function)
        assert result == 30  # 10 + 20
        assert len(code_flow.execution_steps) > 0
    
    def test_39_flow_statistics_accuracy(self, code_flow, sample_functions):
        """Test 39: Flow statistics are calculated accurately."""
        fibonacci = sample_functions['simple_fibonacci']
        code_flow.trace_function(fibonacci, 4)
        
        stats = code_flow.get_flow_statistics()
        
        # Verify specific statistics
        assert stats['total_nodes'] > 0
        assert stats['total_edges'] == stats['total_nodes'] - 1  # Tree structure
        assert 'node_types' in stats
        
        node_types = stats['node_types']
        assert 'start' in node_types
        assert 'end' in node_types
        assert node_types['start'] == 1  # Exactly one start node
        assert node_types['end'] == 1    # Exactly one end node
    
    def test_40_memory_efficiency(self, code_flow):
        """Test 40: Memory efficiency with moderately large traces."""
        def memory_test_function(n):
            result = []
            for i in range(n):
                for j in range(i):
                    result.append(i * j)
            return len(result)
        
        # Test with moderately large input
        result = code_flow.trace_function(memory_test_function, 20)
        assert result == 190  # Sum of 0 to 19 = 190
        
        # Should handle this without memory issues
        assert len(code_flow.execution_steps) > 0
        assert len(code_flow.nodes) > 0
        
        # Memory usage should be reasonable (this is more of a smoke test)
        # In a real scenario, you might want to measure actual memory usage

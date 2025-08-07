"""
Test suite for Code2Flow performance and integration testing.
Tests 61-80: Performance scenarios, stress testing, and integration cases.
"""

import pytest
import sys
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor

from code2flow import CodeFlow, CodeTracer, visualize, trace
from code2flow.core.flow import NodeType
from code2flow.exporters.mermaid_exporter import MermaidExporter


class TestPerformanceAndIntegration:
    """Tests 61-80: Performance and integration scenarios."""
    
    def test_61_performance_moderate_recursion(self, code_flow):
        """Test 61: Performance with moderate recursion depth."""
        def fibonacci_recursive(n):
            if n <= 1:
                return n
            return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)
        
        start_time = time.time()
        result = code_flow.trace_function(fibonacci_recursive, 8)
        end_time = time.time()
        
        assert result == 21  # 8th Fibonacci number
        assert len(code_flow.execution_steps) > 20
        
        # Should complete in reasonable time (less than 5 seconds)
        execution_time = end_time - start_time
        assert execution_time < 5.0, f"Execution took too long: {execution_time}s"
    
    def test_62_performance_large_array_processing(self, code_flow):
        """Test 62: Performance with large array processing."""
        def process_large_array(arr):
            result = []
            for i, item in enumerate(arr):
                if i % 2 == 0:
                    result.append(item * 2)
                else:
                    result.append(item + 1)
            return result
        
        large_array = list(range(100))  # 100 elements
        
        start_time = time.time()
        result = code_flow.trace_function(process_large_array, large_array)
        end_time = time.time()
        
        assert len(result) == 100
        assert result[0] == 0  # 0 * 2
        assert result[1] == 2  # 1 + 1
        
        # Should handle large arrays efficiently
        execution_time = end_time - start_time
        assert execution_time < 3.0, f"Large array processing took too long: {execution_time}s"
    
    def test_63_performance_nested_loop_complexity(self, code_flow):
        """Test 63: Performance with nested loops (O(n²) complexity)."""
        def nested_loop_algorithm(n):
            result = 0
            for i in range(n):
                for j in range(n):
                    result += i * j
            return result
        
        start_time = time.time()
        result = code_flow.trace_function(nested_loop_algorithm, 15)
        end_time = time.time()
        
        expected = sum(i * j for i in range(15) for j in range(15))
        assert result == expected
        
        # Should handle O(n²) complexity reasonably
        execution_time = end_time - start_time
        assert execution_time < 3.0, f"Nested loops took too long: {execution_time}s"
    
    def test_64_memory_usage_with_large_traces(self, code_flow):
        """Test 64: Memory usage with functions generating large traces."""
        def memory_intensive_function(n):
            data = []
            for i in range(n):
                data.append(i ** 2)
                if i % 10 == 0:
                    data = [x for x in data if x % 2 == 0]  # Filter even numbers
            return len(data)
        
        result = code_flow.trace_function(memory_intensive_function, 50)
        
        assert isinstance(result, int)
        assert result > 0
        
        # Should generate substantial trace without memory issues
        assert len(code_flow.execution_steps) > 50
        assert len(code_flow.nodes) > 10
    
    def test_65_concurrent_tracing_simulation(self):
        """Test 65: Simulate concurrent tracing scenarios."""
        def worker_function(worker_id):
            result = 0
            for i in range(10):
                result += worker_id * i
            return result
        
        # Create multiple CodeFlow instances (simulating concurrent usage)
        flows = []
        results = []
        
        for worker_id in range(5):
            flow = CodeFlow()
            result = flow.trace_function(worker_function, worker_id)
            flows.append(flow)
            results.append(result)
        
        # Each worker should produce different results
        assert len(set(results)) == 5  # All results should be unique
        
        # Each flow should have captured steps
        for flow in flows:
            assert len(flow.execution_steps) > 5
    
    def test_66_export_performance_large_flow(self, code_flow):
        """Test 66: Export performance with large flow graphs."""
        def complex_algorithm(n):
            result = []
            for i in range(n):
                if i % 3 == 0:
                    result.append(i * 2)
                elif i % 3 == 1:
                    result.append(i + 5)
                else:
                    result.append(i ** 2)
            return sum(result)
        
        # Generate a complex flow
        code_flow.trace_function(complex_algorithm, 30)
        
        # Test export performance
        start_time = time.time()
        mermaid_content = code_flow.export_mermaid()
        export_time = time.time() - start_time
        
        assert "graph TD" in mermaid_content
        assert len(mermaid_content) > 100  # Should be substantial
        
        # Export should complete quickly
        assert export_time < 2.0, f"Export took too long: {export_time}s"
    
    def test_67_integration_with_built_in_functions(self, code_flow):
        """Test 67: Integration with Python built-in functions."""
        def function_using_builtins(data):
            # Use various built-in functions
            result = []
            result.append(len(data))
            result.append(max(data) if data else 0)
            result.append(min(data) if data else 0)
            result.append(sum(data))
            
            # Use built-in data structure methods
            sorted_data = sorted(data)
            result.extend(sorted_data[:3])  # First 3 elements
            
            return result
        
        test_data = [5, 2, 8, 1, 9, 3, 7]
        result = code_flow.trace_function(function_using_builtins, test_data)
        
        expected = [7, 9, 1, 35, 1, 2, 3]  # len, max, min, sum, first 3 of sorted
        assert result == expected
        
        # Should handle built-ins without issues
        assert len(code_flow.execution_steps) > 5
    
    def test_68_integration_with_standard_library(self, code_flow):
        """Test 68: Integration with standard library modules."""
        import math
        import random
        
        def function_using_stdlib(n):
            # Use math module
            result = math.sqrt(n)
            result = math.ceil(result)
            
            # Use random module (with seed for reproducibility)
            random.seed(42)
            random_nums = [random.randint(1, 10) for _ in range(3)]
            
            return result + sum(random_nums)
        
        result = code_flow.trace_function(function_using_stdlib, 25)
        
        # math.sqrt(25) = 5.0, math.ceil(5.0) = 5
        # With seed 42, should get reproducible random numbers
        assert isinstance(result, int)
        assert result > 5  # At least the math result plus some random numbers
        
        # Should trace the function without issues
        assert len(code_flow.execution_steps) > 3
    
    def test_69_integration_decorator_with_complex_function(self):
        """Test 69: Integration of @visualize decorator with complex functions."""
        @visualize(auto_display=False)
        def complex_decorated_function(matrix):
            # Matrix operations
            rows, cols = len(matrix), len(matrix[0])
            result = []
            
            for i in range(rows):
                row_sum = sum(matrix[i])
                if row_sum > 10:
                    result.append(row_sum * 2)
                else:
                    result.append(row_sum)
            
            return result
        
        test_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        result = complex_decorated_function(test_matrix)
        
        expected = [6, 30, 48]  # [6, 15*2, 24*2]
        assert result == expected
        
        # Check that decorator captured the execution
        flow = complex_decorated_function.get_flow()
        assert flow is not None
        assert len(flow.execution_steps) > 10
    
    def test_70_error_recovery_after_exception(self, code_flow):
        """Test 70: Error recovery and tracing after exceptions."""
        def function_with_exception(x):
            if x < 0:
                raise ValueError("Negative value not allowed")
            return x * 2
        
        # First, trace a normal execution
        result1 = code_flow.trace_function(function_with_exception, 5)
        assert result1 == 10
        steps1 = len(code_flow.execution_steps)
        
        # Then, trace an execution that raises an exception
        code_flow2 = CodeFlow()
        with pytest.raises(ValueError):
            code_flow2.trace_function(function_with_exception, -3)
        
        # Then, trace another normal execution
        code_flow3 = CodeFlow()
        result2 = code_flow3.trace_function(function_with_exception, 7)
        assert result2 == 14
        steps3 = len(code_flow3.execution_steps)
        
        # All traces should work independently
        assert steps1 > 0
        assert steps3 > 0
    
    def test_71_variable_tracking_with_complex_data_types(self, code_flow):
        """Test 71: Variable tracking with complex data types."""
        def function_with_complex_data():
            # Various complex data types
            my_dict = {'a': 1, 'b': [1, 2, 3]}
            my_list = [1, {'nested': True}, [4, 5]]
            my_tuple = (1, 2, {'key': 'value'})
            my_set = {1, 2, 3, 4}
            
            # Modify the data
            my_dict['c'] = my_list
            my_list.append(my_tuple)
            
            return len(str(my_dict)) + len(str(my_list))
        
        result = code_flow.trace_function(function_with_complex_data)
        
        assert isinstance(result, int)
        assert result > 10  # Should be substantial
        
        # Should track variable changes safely
        dict_changes = code_flow.get_variable_changes('my_dict')
        list_changes = code_flow.get_variable_changes('my_list')
        
        assert len(dict_changes) > 0
        assert len(list_changes) > 0
    
    def test_72_flow_analysis_with_multiple_branches(self, code_flow):
        """Test 72: Flow analysis with multiple execution branches."""
        def multi_branch_function(x, y):
            if x > 10:
                if y > 5:
                    return x * y
                else:
                    return x + y
            elif x > 5:
                if y > 10:
                    return x - y
                else:
                    return x / (y + 1)
            else:
                return x ** y
        
        # Test different branches
        test_cases = [(15, 8), (15, 3), (8, 12), (8, 2), (3, 4)]
        results = []
        
        for x, y in test_cases:
            flow = CodeFlow()
            result = flow.trace_function(multi_branch_function, x, y)
            results.append(result)
            
            # Each execution should have decision nodes
            decision_nodes = flow.get_nodes_by_type(NodeType.DECISION)
            assert len(decision_nodes) > 1  # Multiple decision points
        
        # All results should be different (testing different branches)
        assert len(set(results)) == len(test_cases)
    
    def test_73_performance_with_string_operations(self, code_flow):
        """Test 73: Performance with intensive string operations."""
        def string_intensive_function(text, operations):
            result = text
            for op in operations:
                if op == 'upper':
                    result = result.upper()
                elif op == 'lower':
                    result = result.lower()
                elif op == 'reverse':
                    result = result[::-1]
                elif op == 'repeat':
                    result = result * 2
                elif op == 'strip':
                    result = result.strip()
            
            return len(result)
        
        text = "Hello World! " * 10
        operations = ['upper', 'reverse', 'lower', 'strip', 'repeat'] * 4
        
        start_time = time.time()
        result = code_flow.trace_function(string_intensive_function, text, operations)
        end_time = time.time()
        
        assert isinstance(result, int)
        assert result > 0
        
        # Should handle string operations efficiently
        execution_time = end_time - start_time
        assert execution_time < 2.0, f"String operations took too long: {execution_time}s"
    
    def test_74_integration_with_class_inheritance(self, code_flow):
        """Test 74: Integration with class inheritance."""
        class BaseProcessor:
            def __init__(self, data):
                self.data = data
            
            def process(self):
                return self._transform(self.data)
            
            def _transform(self, data):
                return data
        
        class NumberProcessor(BaseProcessor):
            def _transform(self, data):
                return [x * 2 for x in data if isinstance(x, (int, float))]
        
        class StringProcessor(BaseProcessor):
            def _transform(self, data):
                return [str(x).upper() for x in data]
        
        # Test with NumberProcessor
        num_processor = NumberProcessor([1, 2, 3, 'hello', 4.5])
        result1 = code_flow.trace_function(num_processor.process)
        
        expected1 = [2, 4, 6, 9.0]
        assert result1 == expected1
        
        # Test with StringProcessor
        flow2 = CodeFlow()
        str_processor = StringProcessor([1, 2, 'hello', 3.14])
        result2 = flow2.trace_function(str_processor.process)
        
        expected2 = ['1', '2', 'HELLO', '3.14']
        assert result2 == expected2
        
        # Both should have captured method calls
        assert len(code_flow.execution_steps) > 5
        assert len(flow2.execution_steps) > 5
    
    def test_75_stress_test_rapid_function_calls(self):
        """Test 75: Stress test with rapid function calls."""
        def simple_calculation(a, b):
            return a + b * 2
        
        # Perform many rapid traces
        flows = []
        results = []
        
        start_time = time.time()
        for i in range(20):
            flow = CodeFlow()
            result = flow.trace_function(simple_calculation, i, i + 1)
            flows.append(flow)
            results.append(result)
        
        end_time = time.time()
        
        # All should complete successfully
        assert len(flows) == 20
        assert len(results) == 20
        
        # Results should be correct
        for i, result in enumerate(results):
            expected = i + (i + 1) * 2
            assert result == expected
        
        # Should complete in reasonable time
        total_time = end_time - start_time
        assert total_time < 5.0, f"Rapid calls took too long: {total_time}s"
    
    def test_76_integration_with_external_imports(self, code_flow):
        """Test 76: Integration with external imports and modules."""
        def function_with_imports():
            import os
            import sys
            from collections import defaultdict
            
            # Use imported modules
            current_dir = os.getcwd()
            python_version = sys.version_info.major
            
            # Use imported classes
            counter = defaultdict(int)
            for char in "hello":
                counter[char] += 1
            
            return len(current_dir) + python_version + len(counter)
        
        result = code_flow.trace_function(function_with_imports)
        
        assert isinstance(result, int)
        assert result > 5  # Should be substantial
        
        # Should handle imports without breaking
        assert len(code_flow.execution_steps) > 5
    
    def test_77_flow_statistics_comprehensive_analysis(self, code_flow):
        """Test 77: Comprehensive flow statistics analysis."""
        def comprehensive_function(data):
            # Multiple types of operations
            result = []
            
            # Loops
            for item in data:
                # Conditionals
                if item % 2 == 0:
                    result.append(item ** 2)
                else:
                    result.append(item * 3)
            
            # Function calls
            total = sum(result)
            average = total / len(result) if result else 0
            
            # More conditionals
            if average > 50:
                return "high"
            elif average > 20:
                return "medium"
            else:
                return "low"
        
        test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = code_flow.trace_function(comprehensive_function, test_data)
        
        assert result in ["high", "medium", "low"]
        
        # Analyze comprehensive statistics
        stats = code_flow.get_flow_statistics()
        
        assert stats['total_nodes'] > 15
        assert stats['total_edges'] > 10
        assert 'decision' in stats['node_types']
        assert 'process' in stats['node_types']
        assert stats['node_types']['decision'] > 5  # Multiple decisions
    
    def test_78_export_format_consistency(self, code_flow, temp_dir):
        """Test 78: Consistency across different export formats."""
        def export_test_function(n):
            result = 0
            for i in range(n):
                if i % 2 == 0:
                    result += i
                else:
                    result -= i
            return result
        
        code_flow.trace_function(export_test_function, 10)
        
        # Export in different formats
        mermaid_content = code_flow.export_mermaid()
        
        # Test Mermaid format
        assert "graph TD" in mermaid_content
        assert "START" in mermaid_content
        assert "END" in mermaid_content
        
        # Export with metadata
        exporter = MermaidExporter(code_flow)
        metadata_path = os.path.join(temp_dir, "metadata_export.md")
        metadata_content = exporter.export_with_metadata(metadata_path)
        
        assert "# Code Execution Flow" in metadata_content
        assert "## Statistics" in metadata_content
        assert os.path.exists(metadata_path)
        
        # Export interactive HTML
        html_path = os.path.join(temp_dir, "interactive_export.html")
        html_content = exporter.export_interactive(html_path)
        
        assert "<html>" in html_content
        assert "mermaid" in html_content
        assert os.path.exists(html_path)
    
    def test_79_integration_with_context_managers(self, code_flow):
        """Test 79: Integration with context managers and resource handling."""
        def function_with_context_managers(filename):
            result = []
            
            # File context manager
            try:
                with open(filename, 'w') as f:
                    f.write("test data\n")
                    f.write("more test data\n")
                
                with open(filename, 'r') as f:
                    lines = f.readlines()
                    result.extend([len(line.strip()) for line in lines])
                
            finally:
                # Cleanup
                if os.path.exists(filename):
                    os.remove(filename)
            
            return result
        
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(delete=False).name
        
        result = code_flow.trace_function(function_with_context_managers, temp_file)
        
        expected = [9, 14]  # Lengths of "test data" and "more test data"
        assert result == expected
        
        # Should handle context managers properly
        assert len(code_flow.execution_steps) > 10
    
    def test_80_comprehensive_integration_scenario(self, code_flow):
        """Test 80: Comprehensive integration scenario combining multiple features."""
        class DataProcessor:
            def __init__(self, name):
                self.name = name
                self.processed_count = 0
            
            def process_dataset(self, data):
                """Comprehensive data processing with multiple patterns."""
                results = []
                
                for item in data:
                    # Type checking and processing
                    if isinstance(item, str):
                        processed = self._process_string(item)
                    elif isinstance(item, (int, float)):
                        processed = self._process_number(item)
                    elif isinstance(item, list):
                        processed = self._process_list(item)
                    else:
                        processed = str(item)
                    
                    results.append(processed)
                    self.processed_count += 1
                
                # Post-processing
                if len(results) > 5:
                    results = self._filter_results(results)
                
                return {
                    'processor': self.name,
                    'count': self.processed_count,
                    'results': results,
                    'summary': self._generate_summary(results)
                }
            
            def _process_string(self, s):
                return s.upper() if len(s) < 5 else s.lower()
            
            def _process_number(self, n):
                return n ** 2 if n > 0 else abs(n)
            
            def _process_list(self, lst):
                return sum(x for x in lst if isinstance(x, (int, float)))
            
            def _filter_results(self, results):
                # Keep every other result
                return [results[i] for i in range(0, len(results), 2)]
            
            def _generate_summary(self, results):
                return f"Processed {len(results)} items"
        
        # Complex test data
        test_data = [
            "hello",
            "hi",
            42,
            -3.14,
            [1, 2, 3, 'mixed'],
            "world",
            100,
            [4, 5, 6],
            "test string that is longer than five characters"
        ]
        
        processor = DataProcessor("TestProcessor")
        result = code_flow.trace_function(processor.process_dataset, test_data)
        
        # Verify comprehensive processing
        assert result['processor'] == "TestProcessor"
        assert result['count'] == len(test_data)
        assert 'results' in result
        assert 'summary' in result
        assert "Processed" in result['summary']
        
        # Should have captured extensive execution flow
        assert len(code_flow.execution_steps) > 30
        assert len(code_flow.nodes) > 25
        
        # Should have various node types
        stats = code_flow.get_flow_statistics()
        assert stats['node_types']['call'] > 5  # Multiple method calls
        assert stats['node_types']['decision'] > 3  # Multiple conditionals
        assert stats['node_types']['process'] > 10  # Multiple processing steps

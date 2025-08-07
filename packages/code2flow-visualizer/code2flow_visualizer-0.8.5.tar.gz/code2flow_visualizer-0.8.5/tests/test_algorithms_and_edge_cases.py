"""
Test suite for Code2Flow algorithm-specific testing and edge cases.
Tests 41-60: Various algorithms and edge case scenarios.
"""

import pytest
import sys
import os
from unittest.mock import patch
import threading
import time

from code2flow import CodeFlow, CodeTracer, visualize, trace
from code2flow.core.flow import NodeType


class TestAlgorithmsAndEdgeCases:
    """Tests 41-60: Algorithm-specific testing and edge cases."""
    
    def test_41_bubble_sort_algorithm(self, code_flow):
        """Test 41: Bubble sort algorithm tracing."""
        def bubble_sort(arr):
            n = len(arr)
            for i in range(n):
                for j in range(0, n-i-1):
                    if arr[j] > arr[j+1]:
                        arr[j], arr[j+1] = arr[j+1], arr[j]
            return arr
        
        test_array = [64, 34, 25, 12, 22, 11, 90]
        result = code_flow.trace_function(bubble_sort, test_array.copy())
        
        expected = [11, 12, 22, 25, 34, 64, 90]
        assert result == expected
        assert len(code_flow.execution_steps) > 10  # Multiple iterations
        
        # Should have decision nodes for comparisons
        decision_nodes = code_flow.get_nodes_by_type(NodeType.DECISION)
        assert len(decision_nodes) > 0
    
    def test_42_binary_search_algorithm(self, code_flow):
        """Test 42: Binary search algorithm implementation."""
        def binary_search(arr, target):
            left, right = 0, len(arr) - 1
            
            while left <= right:
                mid = (left + right) // 2
                if arr[mid] == target:
                    return mid
                elif arr[mid] < target:
                    left = mid + 1
                else:
                    right = mid - 1
            return -1
        
        sorted_array = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        result = code_flow.trace_function(binary_search, sorted_array, 13)
        
        assert result == 6  # Index of 13
        assert len(code_flow.execution_steps) > 5
        
        # Check variable changes for 'mid'
        mid_changes = code_flow.get_variable_changes('mid')
        assert len(mid_changes) > 0
    
    def test_43_quicksort_algorithm(self, code_flow):
        """Test 43: Quicksort recursive algorithm."""
        def quicksort(arr):
            if len(arr) <= 1:
                return arr
            
            pivot = arr[len(arr) // 2]
            left = [x for x in arr if x < pivot]
            middle = [x for x in arr if x == pivot]
            right = [x for x in arr if x > pivot]
            
            return quicksort(left) + middle + quicksort(right)
        
        test_array = [3, 6, 8, 10, 1, 2, 1]
        result = code_flow.trace_function(quicksort, test_array)
        
        expected = [1, 1, 2, 3, 6, 8, 10]
        assert result == expected
        
        # Should have multiple recursive calls
        call_events = [step for step in code_flow.execution_steps if step.event_type == 'call']
        assert len(call_events) > 3  # Multiple recursive calls
    
    def test_44_merge_sort_algorithm(self, code_flow):
        """Test 44: Merge sort divide-and-conquer algorithm."""
        def merge_sort(arr):
            if len(arr) <= 1:
                return arr
            
            mid = len(arr) // 2
            left = merge_sort(arr[:mid])
            right = merge_sort(arr[mid:])
            
            return merge(left, right)
        
        def merge(left, right):
            result = []
            i, j = 0, 0
            
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
            
            result.extend(left[i:])
            result.extend(right[j:])
            return result
        
        test_array = [38, 27, 43, 3, 9, 82, 10]
        result = code_flow.trace_function(merge_sort, test_array)
        
        expected = [3, 9, 10, 27, 38, 43, 82]
        assert result == expected
        assert len(code_flow.execution_steps) > 15  # Complex algorithm
    
    def test_45_fibonacci_dynamic_programming(self, code_flow):
        """Test 45: Fibonacci with dynamic programming approach."""
        def fibonacci_dp(n):
            if n <= 1:
                return n
            
            dp = [0] * (n + 1)
            dp[1] = 1
            
            for i in range(2, n + 1):
                dp[i] = dp[i-1] + dp[i-2]
            
            return dp[n]
        
        result = code_flow.trace_function(fibonacci_dp, 8)
        assert result == 21  # 8th Fibonacci number
        
        # Check that dp array changes are tracked
        dp_changes = code_flow.get_variable_changes('dp')
        assert len(dp_changes) > 5  # Should change multiple times
    
    def test_46_depth_first_search(self, code_flow):
        """Test 46: Depth-first search on a simple graph."""
        def dfs(graph, start, visited=None):
            if visited is None:
                visited = set()
            
            visited.add(start)
            result = [start]
            
            for neighbor in graph.get(start, []):
                if neighbor not in visited:
                    result.extend(dfs(graph, neighbor, visited))
            
            return result
        
        graph = {
            'A': ['B', 'C'],
            'B': ['D', 'E'],
            'C': ['F'],
            'D': [],
            'E': ['F'],
            'F': []
        }
        
        result = code_flow.trace_function(dfs, graph, 'A')
        assert 'A' in result
        assert len(result) > 1  # Should visit multiple nodes
        
        # Should have recursive calls
        call_events = [step for step in code_flow.execution_steps if step.event_type == 'call']
        assert len(call_events) > 2
    
    def test_47_breadth_first_search(self, code_flow):
        """Test 47: Breadth-first search implementation."""
        def bfs(graph, start):
            visited = set()
            queue = [start]
            result = []
            
            while queue:
                node = queue.pop(0)
                if node not in visited:
                    visited.add(node)
                    result.append(node)
                    queue.extend(neighbor for neighbor in graph.get(node, []) if neighbor not in visited)
            
            return result
        
        graph = {
            'A': ['B', 'C'],
            'B': ['D', 'E'],
            'C': ['F'],
            'D': [],
            'E': ['F'],
            'F': []
        }
        
        result = code_flow.trace_function(bfs, graph, 'A')
        assert 'A' in result
        assert len(result) > 1
        
        # Should have loop iterations
        assert len(code_flow.execution_steps) > 10
    
    def test_48_tower_of_hanoi(self, code_flow):
        """Test 48: Tower of Hanoi recursive solution."""
        def hanoi(n, source, destination, auxiliary):
            if n == 1:
                return [(source, destination)]
            
            moves = []
            moves.extend(hanoi(n-1, source, auxiliary, destination))
            moves.append((source, destination))
            moves.extend(hanoi(n-1, auxiliary, destination, source))
            
            return moves
        
        result = code_flow.trace_function(hanoi, 3, 'A', 'C', 'B')
        assert len(result) == 7  # 2^3 - 1 moves
        assert ('A', 'C') in result
        
        # Should have multiple recursive calls
        call_events = [step for step in code_flow.execution_steps if step.event_type == 'call']
        assert len(call_events) > 5
    
    def test_49_greatest_common_divisor(self, code_flow):
        """Test 49: Euclidean algorithm for GCD."""
        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a
        
        result = code_flow.trace_function(gcd, 48, 18)
        assert result == 6
        
        # Check variable changes
        a_changes = code_flow.get_variable_changes('a')
        b_changes = code_flow.get_variable_changes('b')
        assert len(a_changes) > 1
        assert len(b_changes) > 1
    
    def test_50_prime_number_checker(self, code_flow):
        """Test 50: Prime number checking algorithm."""
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    return False
            return True
        
        # Test with a prime number
        result = code_flow.trace_function(is_prime, 17)
        assert result == True
        
        # Test with a non-prime number
        code_flow2 = CodeFlow()
        result2 = code_flow2.trace_function(is_prime, 15)
        assert result2 == False
        
        assert len(code_flow.execution_steps) > 3
    
    def test_51_matrix_multiplication(self, code_flow):
        """Test 51: Matrix multiplication algorithm."""
        def matrix_multiply(A, B):
            rows_A, cols_A = len(A), len(A[0])
            rows_B, cols_B = len(B), len(B[0])
            
            if cols_A != rows_B:
                return None
            
            result = [[0 for _ in range(cols_B)] for _ in range(rows_A)]
            
            for i in range(rows_A):
                for j in range(cols_B):
                    for k in range(cols_A):
                        result[i][j] += A[i][k] * B[k][j]
            
            return result
        
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        
        result = code_flow.trace_function(matrix_multiply, A, B)
        expected = [[19, 22], [43, 50]]
        assert result == expected
        
        # Should have nested loops
        assert len(code_flow.execution_steps) > 15
    
    def test_52_palindrome_checker(self, code_flow):
        """Test 52: Palindrome checking with different approaches."""
        def is_palindrome_iterative(s):
            s = s.lower().replace(' ', '')
            left, right = 0, len(s) - 1
            
            while left < right:
                if s[left] != s[right]:
                    return False
                left += 1
                right -= 1
            
            return True
        
        result = code_flow.trace_function(is_palindrome_iterative, "A man a plan a canal Panama")
        assert result == True
        
        # Check variable tracking
        left_changes = code_flow.get_variable_changes('left')
        right_changes = code_flow.get_variable_changes('right')
        assert len(left_changes) > 1
        assert len(right_changes) > 1
    
    def test_53_factorial_iterative_vs_recursive(self, code_flow):
        """Test 53: Compare iterative vs recursive factorial."""
        def factorial_iterative(n):
            result = 1
            for i in range(1, n + 1):
                result *= i
            return result
        
        def factorial_recursive(n):
            if n <= 1:
                return 1
            return n * factorial_recursive(n - 1)
        
        # Test iterative version
        result1 = code_flow.trace_function(factorial_iterative, 5)
        steps1 = len(code_flow.execution_steps)
        
        # Test recursive version
        code_flow2 = CodeFlow()
        result2 = code_flow2.trace_function(factorial_recursive, 5)
        steps2 = len(code_flow2.execution_steps)
        
        assert result1 == result2 == 120
        # Recursive version should have more steps due to multiple calls
        assert steps2 > steps1
    
    def test_54_string_algorithms(self, code_flow):
        """Test 54: String manipulation algorithms."""
        def longest_common_subsequence(text1, text2):
            m, n = len(text1), len(text2)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if text1[i-1] == text2[j-1]:
                        dp[i][j] = dp[i-1][j-1] + 1
                    else:
                        dp[i][j] = max(dp[i-1][j], dp[i][j-1])
            
            return dp[m][n]
        
        result = code_flow.trace_function(longest_common_subsequence, "abcde", "ace")
        assert result == 3  # "ace" is the LCS
        
        # Should have nested loops and 2D array operations
        assert len(code_flow.execution_steps) > 20
    
    def test_55_edge_case_empty_inputs(self, code_flow):
        """Test 55: Edge cases with empty inputs."""
        def process_list(items):
            if not items:
                return []
            
            result = []
            for item in items:
                result.append(item * 2)
            return result
        
        # Test with empty list
        result = code_flow.trace_function(process_list, [])
        assert result == []
        
        # Should still capture execution steps
        assert len(code_flow.execution_steps) > 0
        
        # Test with None input - should handle gracefully or raise error inside function
        code_flow2 = CodeFlow()
        try:
            result2 = code_flow2.trace_function(process_list, None)
            # If no error, should return empty list or None
            assert result2 == [] or result2 is None
        except TypeError:
            # This is also acceptable behavior
            pass
        
        # Should have captured some execution steps even with None
        assert isinstance(code_flow2.execution_steps, list)
    
    def test_56_edge_case_single_element(self, code_flow):
        """Test 56: Edge cases with single element inputs."""
        def find_max(arr):
            if not arr:
                return None
            
            max_val = arr[0]
            for item in arr[1:]:
                if item > max_val:
                    max_val = item
            return max_val
        
        # Test with single element
        result = code_flow.trace_function(find_max, [42])
        assert result == 42
        
        # Should handle single element gracefully
        assert len(code_flow.execution_steps) > 0
    
    def test_57_edge_case_very_large_numbers(self, code_flow):
        """Test 57: Edge cases with very large numbers."""
        def power_function(base, exponent):
            result = 1
            for _ in range(exponent):
                result *= base
            return result
        
        result = code_flow.trace_function(power_function, 2, 10)
        assert result == 1024
        
        # Should handle large calculations
        assert len(code_flow.execution_steps) > 10
    
    def test_58_edge_case_negative_numbers(self, code_flow):
        """Test 58: Edge cases with negative numbers."""
        def absolute_value_sum(numbers):
            total = 0
            for num in numbers:
                if num < 0:
                    total += -num
                else:
                    total += num
            return total
        
        test_numbers = [-5, 3, -2, 8, -1]
        result = code_flow.trace_function(absolute_value_sum, test_numbers)
        assert result == 19  # 5 + 3 + 2 + 8 + 1
        
        # Should have decision nodes for negative checks
        decision_nodes = code_flow.get_nodes_by_type(NodeType.DECISION)
        assert len(decision_nodes) > 0
    
    def test_59_edge_case_floating_point_precision(self, code_flow):
        """Test 59: Edge cases with floating point precision."""
        def calculate_average(numbers):
            if not numbers:
                return 0.0
            
            total = sum(numbers)
            return total / len(numbers)
        
        test_numbers = [1.1, 2.2, 3.3, 4.4, 5.5]
        result = code_flow.trace_function(calculate_average, test_numbers)
        
        # Check that result is approximately correct (floating point precision)
        assert abs(result - 3.3) < 0.0001
        
        # Should capture floating point operations
        assert len(code_flow.execution_steps) > 0
    
    def test_60_edge_case_unicode_strings(self, code_flow):
        """Test 60: Edge cases with Unicode strings."""
        def count_characters(text):
            char_count = {}
            for char in text:
                if char in char_count:
                    char_count[char] += 1
                else:
                    char_count[char] = 1
            return char_count
        
        # Test with Unicode characters
        unicode_text = "Hello 🌍 World! 🚀"
        result = code_flow.trace_function(count_characters, unicode_text)
        
        assert '🌍' in result
        assert '🚀' in result
        assert result['l'] == 3  # Three 'l' characters
        
        # Should handle Unicode properly
        assert len(code_flow.execution_steps) > 5

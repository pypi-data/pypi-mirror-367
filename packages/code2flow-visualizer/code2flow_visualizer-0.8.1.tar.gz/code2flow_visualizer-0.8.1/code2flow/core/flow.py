"""
Core flow analysis and representation for Code2Flow.

This module provides the CodeFlow class that analyzes execution traces
and builds flowchart representations of code execution.
"""

import ast
import inspect
from typing import Any, Dict, List, Optional, Tuple, Set, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx

from .tracer import CodeTracer, ExecutionStep, FunctionCall


class NodeType(Enum):
    """Types of nodes in the execution flow."""
    START = "start"
    END = "end"
    PROCESS = "process"  # Regular code execution
    DECISION = "decision"  # Conditional branches
    CALL = "call"  # Function calls
    RETURN = "return"  # Function returns
    LOOP = "loop"  # Loop constructs
    EXCEPTION = "exception"  # Exception handling


@dataclass
class FlowNode:
    """Represents a node in the execution flowchart."""
    node_id: str
    node_type: NodeType
    label: str
    code_line: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)
    step_id: Optional[int] = None
    function_name: str = ""
    line_number: int = 0
    
    # Visual properties
    color: str = "#ffffff"
    shape: str = "box"
    
    def __post_init__(self):
        """Set default visual properties based on node type."""
        if self.node_type == NodeType.START:
            self.color = "#90EE90"  # Light green
            self.shape = "ellipse"
        elif self.node_type == NodeType.END:
            self.color = "#FFB6C1"  # Light pink
            self.shape = "ellipse"
        elif self.node_type == NodeType.DECISION:
            self.color = "#FFE4B5"  # Moccasin
            self.shape = "diamond"
        elif self.node_type == NodeType.CALL:
            self.color = "#87CEEB"  # Sky blue
            self.shape = "box"
        elif self.node_type == NodeType.EXCEPTION:
            self.color = "#FFA07A"  # Light salmon
            self.shape = "box"


@dataclass
class FlowEdge:
    """Represents an edge in the execution flowchart."""
    source: str
    target: str
    label: str = ""
    condition: Optional[str] = None
    edge_type: str = "normal"  # normal, true, false, exception
    
    # Visual properties
    color: str = "#000000"
    style: str = "solid"
    
    def __post_init__(self):
        """Set default visual properties based on edge type."""
        if self.edge_type == "true":
            self.color = "#008000"  # Green
            self.label = "True"
        elif self.edge_type == "false":
            self.color = "#FF0000"  # Red
            self.label = "False"
        elif self.edge_type == "exception":
            self.color = "#FF4500"  # Orange red
            self.style = "dashed"


class CodeFlow:
    """
    Analyzes execution traces and builds flowchart representations.
    
    This class takes execution traces from CodeTracer and builds
    a structured flowchart representation that can be visualized.
    """
    
    def __init__(self, tracer: Optional[CodeTracer] = None):
        """
        Initialize CodeFlow.
        
        Args:
            tracer: Optional CodeTracer instance to use
        """
        self.tracer = tracer or CodeTracer()
        self.nodes: Dict[str, FlowNode] = {}
        self.edges: List[FlowEdge] = []
        self.graph = nx.DiGraph()
        
        # Analysis state
        self.execution_steps: List[ExecutionStep] = []
        self.function_calls: List[FunctionCall] = []
        self.current_node_id = 0
        
    def trace_function(self, func: Callable, *args, **kwargs) -> Any:
        """
        Trace a function and build its flow representation.
        
        Args:
            func: Function to trace
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function return value
        """
        # Execute with tracing
        result = self.tracer.trace_function(func, *args, **kwargs)
        
        # Build flow from trace
        self.execution_steps = self.tracer.steps
        self.function_calls = self.tracer.function_calls
        self._build_flow()
        
        return result
        
    def trace_code(self, code: str, globals_dict: Optional[Dict] = None, 
                   locals_dict: Optional[Dict] = None) -> Any:
        """
        Trace arbitrary code and build its flow representation.
        
        Args:
            code: Python code string to trace
            globals_dict: Global variables dictionary
            locals_dict: Local variables dictionary
            
        Returns:
            Code execution result
        """
        globals_dict = globals_dict or {}
        locals_dict = locals_dict or {}
        
        self.tracer.start_trace()
        
        try:
            result = exec(code, globals_dict, locals_dict)
        finally:
            self.tracer.stop_trace()
            
        # Build flow from trace
        self.execution_steps = self.tracer.steps
        self.function_calls = self.tracer.function_calls
        self._build_flow()
        
        return result
        
    def _build_flow(self) -> None:
        """Build flowchart from execution steps."""
        if not self.execution_steps:
            return
            
        self.nodes.clear()
        self.edges.clear()
        self.graph.clear()
        self.current_node_id = 0
        
        # Create start node
        start_node = self._create_node(NodeType.START, "START")
        prev_node_id = start_node.node_id
        
        # Process execution steps
        for i, step in enumerate(self.execution_steps):
            node = self._create_node_from_step(step)
            
            if node:
                # Add edge from previous node
                self._add_edge(prev_node_id, node.node_id)
                prev_node_id = node.node_id
                
        # Create end node
        end_node = self._create_node(NodeType.END, "END")
        if prev_node_id != end_node.node_id:
            self._add_edge(prev_node_id, end_node.node_id)
            
        # Build NetworkX graph
        self._build_networkx_graph()
        
    def _create_node_from_step(self, step: ExecutionStep) -> Optional[FlowNode]:
        """Create a flow node from an execution step."""
        # Determine node type based on step
        if step.event_type == "call":
            node_type = NodeType.CALL
            label = f"Call {step.function_name}()"
        elif step.event_type == "return":
            node_type = NodeType.RETURN
            return_val = step.return_value
            label = f"Return {return_val}" if return_val is not None else "Return"
        elif step.event_type == "exception":
            node_type = NodeType.EXCEPTION
            label = f"Exception: {step.exception_info}"
        else:
            # Regular line execution
            if self._is_decision_step(step):
                node_type = NodeType.DECISION
                label = step.code_context
            elif self._is_loop_step(step):
                node_type = NodeType.LOOP
                label = step.code_context
            else:
                node_type = NodeType.PROCESS
                label = step.code_context or f"Line {step.line_number}"
                
        # Create node
        node = self._create_node(
            node_type=node_type,
            label=label,
            code_line=step.code_context,
            variables=step.local_vars,
            step_id=step.step_id,
            function_name=step.function_name,
            line_number=step.line_number
        )
        
        return node
        
    def _is_decision_step(self, step: ExecutionStep) -> bool:
        """Check if step represents a decision/conditional."""
        code = step.code_context.strip().lower()
        return any(keyword in code for keyword in ['if ', 'elif ', 'while '])
        
    def _is_loop_step(self, step: ExecutionStep) -> bool:
        """Check if step represents a loop construct."""
        code = step.code_context.strip().lower()
        return any(keyword in code for keyword in ['for ', 'while '])
        
    def _create_node(self, node_type: NodeType, label: str, **kwargs) -> FlowNode:
        """Create a new flow node."""
        node_id = f"node_{self.current_node_id}"
        self.current_node_id += 1
        
        node = FlowNode(
            node_id=node_id,
            node_type=node_type,
            label=label,
            **kwargs
        )
        
        self.nodes[node_id] = node
        return node
        
    def _add_edge(self, source: str, target: str, label: str = "", 
                  edge_type: str = "normal", condition: Optional[str] = None) -> FlowEdge:
        """Add an edge between two nodes."""
        edge = FlowEdge(
            source=source,
            target=target,
            label=label,
            edge_type=edge_type,
            condition=condition
        )
        
        self.edges.append(edge)
        return edge
        
    def _build_networkx_graph(self) -> None:
        """Build NetworkX graph from nodes and edges."""
        # Add nodes
        for node in self.nodes.values():
            self.graph.add_node(
                node.node_id,
                label=node.label,
                node_type=node.node_type.value,
                color=node.color,
                shape=node.shape,
                variables=node.variables
            )
            
        # Add edges
        for edge in self.edges:
            self.graph.add_edge(
                edge.source,
                edge.target,
                label=edge.label,
                color=edge.color,
                style=edge.style,
                edge_type=edge.edge_type
            )
            
    def get_nodes_by_type(self, node_type: NodeType) -> List[FlowNode]:
        """Get all nodes of a specific type."""
        return [node for node in self.nodes.values() if node.node_type == node_type]
        
    def get_function_subgraph(self, function_name: str) -> nx.DiGraph:
        """Get subgraph for a specific function."""
        function_nodes = [
            node.node_id for node in self.nodes.values() 
            if node.function_name == function_name
        ]
        return self.graph.subgraph(function_nodes)
        
    def get_execution_path(self) -> List[str]:
        """Get the main execution path through the flow."""
        if not self.nodes:
            return []
            
        # Find start and end nodes
        start_nodes = [n.node_id for n in self.nodes.values() if n.node_type == NodeType.START]
        end_nodes = [n.node_id for n in self.nodes.values() if n.node_type == NodeType.END]
        
        if not start_nodes or not end_nodes:
            return list(self.nodes.keys())
            
        try:
            return nx.shortest_path(self.graph, start_nodes[0], end_nodes[0])
        except nx.NetworkXNoPath:
            return list(self.nodes.keys())
            
    def get_variable_changes(self, variable_name: str) -> List[Tuple[str, Any]]:
        """Get all changes to a specific variable throughout execution."""
        changes = []
        
        for node in self.nodes.values():
            if variable_name in node.variables:
                changes.append((node.node_id, node.variables[variable_name]))
                
        return changes
        
    def get_flow_statistics(self) -> Dict[str, Any]:
        """Get statistics about the execution flow."""
        node_types = {}
        for node in self.nodes.values():
            node_type = node.node_type.value
            node_types[node_type] = node_types.get(node_type, 0) + 1
            
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'node_types': node_types,
            'functions': len(set(node.function_name for node in self.nodes.values() if node.function_name)),
            'max_depth': max((len(path) for path in nx.all_simple_paths(
                self.graph, 
                next(iter(self.get_nodes_by_type(NodeType.START))).node_id if self.get_nodes_by_type(NodeType.START) else list(self.nodes.keys())[0],
                next(iter(self.get_nodes_by_type(NodeType.END))).node_id if self.get_nodes_by_type(NodeType.END) else list(self.nodes.keys())[-1]
            )), default=0) if self.nodes else 0
        }
        
    def export_mermaid(self, filename: Optional[str] = None) -> str:
        """Export flow as Mermaid diagram."""
        from ..exporters.mermaid_exporter import MermaidExporter
        exporter = MermaidExporter(self)
        return exporter.export(filename)
        
    def export_graphviz(self, filename: Optional[str] = None) -> str:
        """Export flow as Graphviz diagram."""
        from ..exporters.graphviz_exporter import GraphvizExporter
        exporter = GraphvizExporter(self)
        return exporter.export(filename)
        
    def export_image(self, filename: str, format: str = "png") -> None:
        """Export flow as image."""
        from ..exporters.image_exporter import ImageExporter
        exporter = ImageExporter(self)
        exporter.export(filename, format)

"""
Flow visualizer for Code2Flow.

This module provides the FlowVisualizer class that creates visual representations
of code execution flow using matplotlib and other visualization libraries.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import networkx as nx
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from ..core.flow import CodeFlow, FlowNode, FlowEdge, NodeType


class FlowVisualizer:
    """
    Creates visual representations of code execution flow.
    
    This class takes a CodeFlow object and generates various types of
    visualizations including static plots and interactive displays.
    """
    
    def __init__(self, flow: CodeFlow):
        """
        Initialize FlowVisualizer.
        
        Args:
            flow: CodeFlow object containing the execution trace
        """
        self.flow = flow
        self.fig = None
        self.ax = None
        self.node_positions = {}
        self.node_patches = {}
        
    def display(self, figsize: Tuple[int, int] = (12, 8), layout: str = "hierarchical") -> None:
        """
        Display the flow visualization.
        
        Args:
            figsize: Figure size (width, height)
            layout: Layout algorithm ("hierarchical", "circular", "spring")
        """
        if not self.flow.nodes:
            print("No flow data to visualize")
            return
            
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(1, 1, figsize=figsize)
        
        # Calculate node positions
        self._calculate_positions(layout)
        
        # Draw nodes and edges
        self._draw_nodes()
        self._draw_edges()
        
        # Configure plot
        self.ax.set_title("Code Execution Flow", fontsize=16, fontweight='bold')
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # Add legend
        self._add_legend()
        
        plt.tight_layout()
        plt.show()
        
    def _calculate_positions(self, layout: str) -> None:
        """Calculate node positions based on layout algorithm."""
        G = self.flow.graph
        
        if layout == "hierarchical":
            self.node_positions = self._hierarchical_layout(G)
        elif layout == "circular":
            self.node_positions = nx.circular_layout(G)
        elif layout == "spring":
            self.node_positions = nx.spring_layout(G, k=2, iterations=50)
        else:
            self.node_positions = nx.spring_layout(G)
            
        # Scale positions to reasonable plot coordinates
        scale = 10
        for node_id in self.node_positions:
            x, y = self.node_positions[node_id]
            self.node_positions[node_id] = (x * scale, y * scale)
            
    def _hierarchical_layout(self, G: nx.DiGraph) -> Dict[str, Tuple[float, float]]:
        """Create a hierarchical layout for the flow graph."""
        if not G.nodes():
            return {}
            
        # Find start nodes (nodes with no predecessors)
        start_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]
        if not start_nodes:
            # If no clear start, use first node
            start_nodes = [list(G.nodes())[0]]
            
        # Assign levels using BFS
        levels = {}
        queue = [(node, 0) for node in start_nodes]
        visited = set()
        
        while queue:
            node, level = queue.pop(0)
            if node in visited:
                continue
                
            visited.add(node)
            levels[node] = level
            
            # Add successors to next level
            for successor in G.successors(node):
                if successor not in visited:
                    queue.append((successor, level + 1))
                    
        # Arrange nodes by level
        level_nodes = {}
        for node, level in levels.items():
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(node)
            
        # Calculate positions
        positions = {}
        max_level = max(level_nodes.keys()) if level_nodes else 0
        
        for level, nodes in level_nodes.items():
            y = 1.0 - (level / max_level) if max_level > 0 else 0.5
            
            # Spread nodes horizontally
            if len(nodes) == 1:
                x = 0.5
                positions[nodes[0]] = (x, y)
            else:
                for i, node in enumerate(nodes):
                    x = i / (len(nodes) - 1)
                    positions[node] = (x, y)
                    
        return positions
        
    def _draw_nodes(self) -> None:
        """Draw flow nodes on the plot."""
        for node in self.flow.nodes.values():
            if node.node_id not in self.node_positions:
                continue
                
            x, y = self.node_positions[node.node_id]
            
            # Determine node visual properties
            width, height = self._get_node_size(node)
            color = node.color
            shape = node.shape
            
            # Create node patch
            if shape == "ellipse":
                patch = patches.Ellipse((x, y), width, height, 
                                      facecolor=color, edgecolor='black', linewidth=1)
            elif shape == "diamond":
                # Create diamond shape
                diamond_points = np.array([
                    [x, y + height/2],  # top
                    [x + width/2, y],   # right
                    [x, y - height/2],  # bottom
                    [x - width/2, y]    # left
                ])
                patch = patches.Polygon(diamond_points, facecolor=color, 
                                      edgecolor='black', linewidth=1)
            else:  # box
                patch = FancyBboxPatch((x - width/2, y - height/2), width, height,
                                     boxstyle="round,pad=0.1", 
                                     facecolor=color, edgecolor='black', linewidth=1)
            
            self.ax.add_patch(patch)
            self.node_patches[node.node_id] = patch
            
            # Add node label
            label = self._format_node_label(node)
            self.ax.text(x, y, label, ha='center', va='center', 
                        fontsize=8, fontweight='bold', wrap=True)
                        
    def _draw_edges(self) -> None:
        """Draw flow edges on the plot."""
        for edge in self.flow.edges:
            if (edge.source not in self.node_positions or 
                edge.target not in self.node_positions):
                continue
                
            x1, y1 = self.node_positions[edge.source]
            x2, y2 = self.node_positions[edge.target]
            
            # Draw arrow
            self.ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle='->', color=edge.color,
                                         linestyle=edge.style, lw=1.5))
            
            # Add edge label if present
            if edge.label:
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                self.ax.text(mid_x, mid_y, edge.label, fontsize=6,
                           bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
                           
    def _get_node_size(self, node: FlowNode) -> Tuple[float, float]:
        """Get appropriate size for a node based on its content."""
        base_width, base_height = 2.0, 1.0
        
        # Adjust size based on label length
        label_factor = min(len(node.label) / 20, 2.0)
        width = base_width * (1 + label_factor * 0.3)
        height = base_height * (1 + label_factor * 0.2)
        
        return width, height
        
    def _format_node_label(self, node: FlowNode) -> str:
        """Format node label for display."""
        label = node.label
        
        # Truncate long labels
        if len(label) > 30:
            label = label[:27] + "..."
            
        # Add variable info for process nodes
        if node.node_type == NodeType.PROCESS and node.variables:
            # Show up to 2 most important variables
            var_strs = []
            for var_name, var_value in list(node.variables.items())[:2]:
                if not var_name.startswith('_'):
                    var_strs.append(f"{var_name}={var_value}")
                    
            if var_strs:
                label += "\n" + ", ".join(var_strs)
                
        return label
        
    def _add_legend(self) -> None:
        """Add legend explaining node types and colors."""
        legend_elements = []
        
        # Create legend patches for each node type present
        node_types_present = set(node.node_type for node in self.flow.nodes.values())
        
        type_info = {
            NodeType.START: ("Start", "#90EE90"),
            NodeType.END: ("End", "#FFB6C1"),
            NodeType.PROCESS: ("Process", "#ffffff"),
            NodeType.DECISION: ("Decision", "#FFE4B5"),
            NodeType.CALL: ("Function Call", "#87CEEB"),
            NodeType.RETURN: ("Return", "#ffffff"),
            NodeType.LOOP: ("Loop", "#ffffff"),
            NodeType.EXCEPTION: ("Exception", "#FFA07A")
        }
        
        for node_type in node_types_present:
            if node_type in type_info:
                name, color = type_info[node_type]
                legend_elements.append(patches.Rectangle((0, 0), 1, 1, 
                                                       facecolor=color, edgecolor='black',
                                                       label=name))
        
        if legend_elements:
            self.ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
            
    def save_image(self, filename: str, dpi: int = 300, format: str = 'png') -> None:
        """
        Save the visualization as an image.
        
        Args:
            filename: Output filename
            dpi: Image resolution
            format: Image format ('png', 'svg', 'pdf', etc.)
        """
        if self.fig is None:
            self.display()
            
        self.fig.savefig(filename, dpi=dpi, format=format, bbox_inches='tight')
        
    def get_interactive_widget(self):
        """
        Get an interactive widget for Jupyter notebooks.
        
        Returns:
            Interactive widget or None if not available
        """
        try:
            import ipywidgets as widgets
            from IPython.display import display
            
            # Create widget with controls
            play_button = widgets.Button(description="Play Animation")
            step_slider = widgets.IntSlider(min=0, max=len(self.flow.execution_steps)-1, 
                                          description="Step:")
            
            def on_play_clicked(b):
                # Implement step-by-step animation
                for i in range(len(self.flow.execution_steps)):
                    step_slider.value = i
                    
            play_button.on_click(on_play_clicked)
            
            def on_step_change(change):
                if change['type'] == 'change' and change['name'] == 'value':
                    self._highlight_step(change['new'])
                    
            step_slider.observe(on_step_change)
            
            return widgets.VBox([
                widgets.HBox([play_button, step_slider]),
                widgets.Output()
            ])
            
        except ImportError:
            print("Interactive widgets require ipywidgets")
            return None
            
    def _highlight_step(self, step_index: int) -> None:
        """Highlight a specific execution step in the visualization."""
        if step_index >= len(self.flow.execution_steps):
            return
            
        step = self.flow.execution_steps[step_index]
        
        # Find corresponding node
        target_node = None
        for node in self.flow.nodes.values():
            if node.step_id == step.step_id:
                target_node = node
                break
                
        if target_node and target_node.node_id in self.node_patches:
            # Reset all nodes to default color
            for node in self.flow.nodes.values():
                if node.node_id in self.node_patches:
                    patch = self.node_patches[node.node_id]
                    patch.set_facecolor(node.color)
                    
            # Highlight current node
            patch = self.node_patches[target_node.node_id]
            patch.set_facecolor('#FFFF00')  # Yellow highlight
            
            if self.fig:
                self.fig.canvas.draw()
                
    def visualize_function(self, func, *args, **kwargs):
        """
        Visualize a function execution directly.
        
        Args:
            func: Function to visualize
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function return value
        """
        result = self.flow.trace_function(func, *args, **kwargs)
        self.display()
        return result

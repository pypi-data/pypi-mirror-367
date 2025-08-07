"""
Mermaid diagram exporter for Code2Flow.

This module provides the MermaidExporter class that converts CodeFlow objects
into Mermaid.js diagram format for easy sharing and documentation.
"""

from typing import Dict, List, Optional, Set
import re
from ..core.flow import CodeFlow, FlowNode, FlowEdge, NodeType


class MermaidExporter:
    """
    Exports CodeFlow objects as Mermaid.js diagrams.
    
    Mermaid.js is a popular diagramming library that uses markdown-like syntax
    to generate flowcharts, sequence diagrams, and other visualizations.
    """
    
    def __init__(self, flow: CodeFlow):
        """
        Initialize MermaidExporter.
        
        Args:
            flow: CodeFlow object to export
        """
        self.flow = flow
        
    def export(self, filename: Optional[str] = None) -> str:
        """
        Export the flow as a Mermaid diagram.
        
        Args:
            filename: Optional filename to save the diagram to
            
        Returns:
            Mermaid diagram as a string
        """
        if not self.flow.nodes:
            return "graph TD\n    A[No flow data available]"
            
        diagram = self._generate_mermaid_diagram()
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(diagram)
                
        return diagram
        
    def _generate_mermaid_diagram(self) -> str:
        """Generate the complete Mermaid diagram."""
        lines = []
        
        # Header
        lines.append("```mermaid")
        lines.append("graph TD")
        
        # Add node definitions
        lines.extend(self._generate_node_definitions())
        
        # Add blank line
        lines.append("")
        
        # Add edge definitions
        lines.extend(self._generate_edge_definitions())
        
        # Add styling
        lines.extend(self._generate_styling())
        
        # Footer
        lines.append("```")
        
        return "\n".join(lines)
        
    def _generate_node_definitions(self) -> List[str]:
        """Generate Mermaid node definitions."""
        lines = []
        
        for node in self.flow.nodes.values():
            mermaid_id = self._sanitize_id(node.node_id)
            label = self._format_node_label(node)
            shape = self._get_mermaid_shape(node)
            
            line = f"    {mermaid_id}{shape[0]}{label}{shape[1]}"
            lines.append(line)
            
        return lines
        
    def _generate_edge_definitions(self) -> List[str]:
        """Generate Mermaid edge definitions."""
        lines = []
        
        for edge in self.flow.edges:
            source_id = self._sanitize_id(edge.source)
            target_id = self._sanitize_id(edge.target)
            
            # Determine edge style and label
            if edge.edge_type == "true":
                edge_style = " -->|Yes| "
            elif edge.edge_type == "false":
                edge_style = " -->|No| "
            elif edge.label:
                edge_style = f" -->|{edge.label}| "
            else:
                edge_style = " --> "
                
            line = f"    {source_id}{edge_style}{target_id}"
            lines.append(line)
            
        return lines
        
    def _generate_styling(self) -> List[str]:
        """Generate Mermaid styling definitions."""
        lines = []
        lines.append("")
        lines.append("    %% Styling")
        
        # Define color classes
        color_classes = {
            NodeType.START: "start-node",
            NodeType.END: "end-node", 
            NodeType.DECISION: "decision-node",
            NodeType.CALL: "call-node",
            NodeType.EXCEPTION: "exception-node"
        }
        
        # Group nodes by type for styling
        node_groups = {}
        for node in self.flow.nodes.values():
            node_type = node.node_type
            if node_type not in node_groups:
                node_groups[node_type] = []
            node_groups[node_type].append(self._sanitize_id(node.node_id))
            
        # Apply styles to each group
        for node_type, node_ids in node_groups.items():
            if node_type in color_classes:
                class_name = color_classes[node_type]
                for node_id in node_ids:
                    lines.append(f"    class {node_id} {class_name}")
                    
        # Define CSS classes
        lines.extend([
            "",
            "    classDef start-node fill:#90EE90,stroke:#333,stroke-width:2px",
            "    classDef end-node fill:#FFB6C1,stroke:#333,stroke-width:2px", 
            "    classDef decision-node fill:#FFE4B5,stroke:#333,stroke-width:2px",
            "    classDef call-node fill:#87CEEB,stroke:#333,stroke-width:2px",
            "    classDef exception-node fill:#FFA07A,stroke:#333,stroke-width:2px"
        ])
        
        return lines
        
    def _sanitize_id(self, node_id: str) -> str:
        """Sanitize node ID for Mermaid compatibility."""
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', node_id)
        
        # Ensure it starts with a letter
        if not sanitized[0].isalpha():
            sanitized = 'node_' + sanitized
            
        return sanitized
        
    def _format_node_label(self, node: FlowNode) -> str:
        """Format node label for Mermaid display."""
        label = node.label
        
        # Escape special characters
        label = label.replace('"', '\\"')
        label = label.replace('[', '\\[')
        label = label.replace(']', '\\]')
        label = label.replace('{', '\\{')
        label = label.replace('}', '\\}')
        label = label.replace('|', '\\|')
        
        # Truncate if too long
        if len(label) > 50:
            label = label[:47] + "..."
            
        # Add variable information for process nodes
        if node.node_type == NodeType.PROCESS and node.variables:
            var_info = []
            for var_name, var_value in list(node.variables.items())[:2]:
                if not var_name.startswith('_'):
                    var_info.append(f"{var_name}={var_value}")
                    
            if var_info:
                var_str = "<br/>".join(var_info)
                label += f"<br/><small>{var_str}</small>"
                
        return label
        
    def _get_mermaid_shape(self, node: FlowNode) -> tuple:
        """Get appropriate Mermaid shape for node type."""
        shape_map = {
            NodeType.START: ("([", "])"),      # Stadium shape
            NodeType.END: ("([", "])"),        # Stadium shape
            NodeType.DECISION: ("{", "}"),     # Diamond shape
            NodeType.PROCESS: ("[", "]"),      # Rectangle shape
            NodeType.CALL: ("[", "]"),         # Rectangle shape
            NodeType.RETURN: ("[", "]"),       # Rectangle shape
            NodeType.LOOP: ("[", "]"),         # Rectangle shape
            NodeType.EXCEPTION: ("[", "]")     # Rectangle shape
        }
        
        return shape_map.get(node.node_type, ("[", "]"))
        
    def export_with_metadata(self, filename: Optional[str] = None) -> str:
        """
        Export diagram with additional metadata and documentation.
        
        Args:
            filename: Optional filename to save to
            
        Returns:
            Mermaid diagram with metadata
        """
        lines = []
        
        # Add title and description
        lines.extend([
            "# Code Execution Flow",
            "",
            "This diagram shows the execution flow of your Python code.",
            "",
            "## Statistics",
            ""
        ])
        
        # Add statistics
        stats = self.flow.get_flow_statistics()
        for key, value in stats.items():
            lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
            
        lines.append("")
        
        # Add the diagram
        diagram = self._generate_mermaid_diagram()
        lines.append(diagram)
        
        # Add variable tracking information
        if self.flow.execution_steps:
            lines.extend([
                "",
                "## Variable Changes",
                "",
                "Key variables and their changes throughout execution:",
                ""
            ])
            
            # Find variables that change
            all_variables = set()
            for step in self.flow.execution_steps:
                all_variables.update(step.local_vars.keys())
                
            for var_name in sorted(all_variables):
                if not var_name.startswith('_'):
                    changes = self.flow.get_variable_changes(var_name)
                    if changes:
                        lines.append(f"### {var_name}")
                        for node_id, value in changes[:5]:  # Limit to first 5 changes
                            lines.append(f"- {node_id}: `{value}`")
                        lines.append("")
                        
        content = "\n".join(lines)
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
                
        return content
        
    def export_interactive(self, filename: Optional[str] = None) -> str:
        """
        Export as interactive HTML with embedded Mermaid.
        
        Args:
            filename: Optional filename to save to
            
        Returns:
            HTML content with interactive diagram
        """
        mermaid_diagram = self._generate_mermaid_diagram()
        
        # Remove the markdown code blocks for HTML embedding
        diagram_content = mermaid_diagram.replace("```mermaid\n", "").replace("```", "")
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Code2Flow - Execution Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .mermaid {{
            text-align: center;
            margin: 20px 0;
        }}
        .info {{
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-box {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2196f3;
        }}
        .stat-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 Code Execution Flow Visualization</h1>
        
        <div class="info">
            <h3>About This Diagram</h3>
            <p>This interactive flowchart shows how your Python code executed step by step. 
            Each node represents a different part of your code execution, and arrows show the flow of control.</p>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value">{len(self.flow.nodes)}</div>
                <div class="stat-label">Total Nodes</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(self.flow.edges)}</div>
                <div class="stat-label">Connections</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(set(node.function_name for node in self.flow.nodes.values() if node.function_name))}</div>
                <div class="stat-label">Functions</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(self.flow.execution_steps)}</div>
                <div class="stat-label">Execution Steps</div>
            </div>
        </div>
        
        <div class="mermaid">
{diagram_content}
        </div>
        
        <div class="info">
            <h3>Legend</h3>
            <ul>
                <li><strong>Green nodes</strong>: Start/End points</li>
                <li><strong>Blue nodes</strong>: Function calls</li>
                <li><strong>Yellow nodes</strong>: Decision points (if/while)</li>
                <li><strong>Red nodes</strong>: Exceptions</li>
                <li><strong>White nodes</strong>: Regular code execution</li>
            </ul>
        </div>
    </div>

    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true
            }}
        }});
    </script>
</body>
</html>
        """
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_template)
                
        return html_template

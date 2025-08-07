# Code2Flow 🔄

**Real-Time Code Execution Visualizer for Python**

Code2Flow is a powerful debugging and visualization library that generates interactive flowcharts of Python code execution. Watch your variables change step-by-step and understand complex logic flow like never before.

## ✨ Features

- 🔍 **Step-by-step execution visualization** - See how variables change during code execution
- 📊 **Interactive flowcharts** - Navigate through execution paths visually  
- 📝 **Jupyter Notebook integration** - Works seamlessly in your favorite environment
- 🎨 **Multiple export formats** - Export to Mermaid.js, Graphviz, PNG, SVG
- 🚀 **Real-time debugging** - Like Python Tutor but more powerful and flexible
- 🔧 **Customizable visualization** - Configure colors, layout, and display options

## 🚀 Quick Start

```bash
pip install code2flow
```

### Basic Usage

```python
from code2flow import visualize

@visualize
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# This will generate an interactive flowchart
result = fibonacci(5)
```

### Jupyter Notebook

```python
from code2flow import FlowVisualizer

visualizer = FlowVisualizer()
visualizer.track_function(your_function)
visualizer.display()  # Shows interactive widget
```

### Export Options

```python
from code2flow import CodeFlow

flow = CodeFlow()
flow.trace(your_code)
flow.export_mermaid("flowchart.md")
flow.export_graphviz("flowchart.dot")
flow.export_image("flowchart.png")
```

## 🛠️ Installation

### Basic Installation
```bash
pip install code2flow
```

### Development Installation
```bash
pip install code2flow[dev]
```

### With Mermaid Support
```bash
pip install code2flow[mermaid]
```

## 📖 Documentation

- [Getting Started Guide](docs/getting_started.md)
- [API Reference](docs/api_reference.md)
- [Examples](examples/)
- [Contributing](CONTRIBUTING.md)

## 🎯 Why Code2Flow?

Traditional debugging tools show you *where* your code fails, but Code2Flow shows you *how* your code behaves. Perfect for:

- Understanding complex algorithms
- Teaching programming concepts  
- Debugging recursive functions
- Visualizing data flow in applications
- Code reviews and documentation

## 📊 Example Output

```
┌─────────────────┐
│ fibonacci(5)    │
│ n = 5          │
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│ n > 1 ?        │
│ True           │
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│ fibonacci(4) +  │
│ fibonacci(3)    │
└─────────────────┘
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- 🐛 [Report bugs](https://github.com/yourusername/code2flow/issues)
- 💡 [Request features](https://github.com/yourusername/code2flow/issues)
- 💬 [Join discussions](https://github.com/yourusername/code2flow/discussions)

---

Made with ❤️ for the Python community

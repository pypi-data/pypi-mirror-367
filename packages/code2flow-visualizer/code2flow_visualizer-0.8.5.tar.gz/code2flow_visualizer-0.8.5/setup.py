from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="code2flow-visualizer",
    version="0.8.5",  # ✅ Updated version
    author="Aryan Mishra",
    author_email="aryanmishra.dev@gmail.com",
    description="Real-Time Code Execution Visualizer for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aryan0854/code2flow-visualizer",
    project_urls={
        "Repository": "https://github.com/Aryan0854/code2flow-visualizer",
        "Bug Tracker": "https://github.com/Aryan0854/code2flow-visualizer/issues",
        "Documentation": "https://github.com/Aryan0854/code2flow-visualizer#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    install_requires=[
        "graphviz>=0.20.0",
        "jupyter>=1.0.0",
        "ipython>=8.0.0",
        "matplotlib>=3.5.0",
        "networkx>=2.8.0",
        "pydot>=1.4.0",
        "ast-decompiler>=0.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "jupyter-notebook>=6.4.0",
        ],
        "mermaid": [
            "mermaid-py>=0.1.0",
        ],
    },
    keywords="debugging visualization flowchart code-analysis",
)

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="enhanced-mcp-memory",
    version="2.0.4",
    description="MCP server with sequential thinking, project convention learning, and intelligent memory management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="cbunting99",
    author_email="cbunting99@users.noreply.github.com",
    url="https://github.com/cbunting99/enhanced-mcp-memory",
    py_modules=[
        "mcp_server_enhanced", 
        "memory_manager", 
        "database", 
        "sequential_thinking", 
        "project_conventions",
        "enhanced_automation_middleware"
    ],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "enhanced-mcp-memory=mcp_server_enhanced:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="mcp, memory, ai, task-management, knowledge-graph, semantic-search, sequential-thinking, project-conventions, token-optimization",
    project_urls={
        "Bug Reports": "https://github.com/cbunting99/enhanced-mcp-memory/issues",
        "Source": "https://github.com/cbunting99/enhanced-mcp-memory",
        "Documentation": "https://github.com/cbunting99/enhanced-mcp-memory#readme",
    },
)

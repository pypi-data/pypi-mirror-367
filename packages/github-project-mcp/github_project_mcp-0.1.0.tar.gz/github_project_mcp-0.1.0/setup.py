"""Setup configuration for GitHub Project MCP Server"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="github-project-mcp",
    version="0.1.0",
    author="Enrica Tan",
    author_email="tanenrica@gmail.com",
    description="A Model Context Protocol server for managing GitHub projects and issues via GraphQL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaqarx/github-project-mcp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "mcp>=0.9.0",
        "httpx>=0.27.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "gps=github_project_mcp.cli:cli",
            "github-project-server=github_project_mcp.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "github_project_mcp": ["*.json"],
    },
)
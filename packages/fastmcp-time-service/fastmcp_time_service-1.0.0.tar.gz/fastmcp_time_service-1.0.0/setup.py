#!/usr/bin/env python3
"""
MCP Time Server - 基于SSE传输的MCP时间服务器
"""

from setuptools import setup, find_packages

# 读取 README 文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取 requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fastmcp-time-service",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="基于SSE传输的MCP时间服务器，提供多时区时间查询功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcp-time-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mcp-time-server=mcp_time_server.time_server:main",
        ],
    },
    keywords="mcp, time, server, timezone, fastmcp",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/mcp-time-server/issues",
        "Source": "https://github.com/yourusername/mcp-time-server",
        "Documentation": "https://github.com/yourusername/mcp-time-server/blob/main/README.md",
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.json"],
    },
)
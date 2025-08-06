"""
ODIN Protocol Python SDK Setup
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
version = "1.0.0"

# Read long description from README
long_description = """
# ODIN Protocol Python SDK

The definitive Python SDK for the ODIN Protocol - the world's first standardized AI-to-AI communication protocol with self-healing capabilities.

## Features

🚀 **Revolutionary AI Communication**
- Standardized protocol for AI-to-AI messaging
- Self-healing capabilities with automatic error correction
- Real-time analytics and monitoring

🎯 **Advanced Rule Engine** 
- 100+ built-in operators and conditions
- Custom rule creation and management
- Policy enforcement and compliance checking

🔌 **Extensible Plugin System**
- Easy plugin development framework
- Marketplace integration for community plugins
- Enterprise-grade customization options

🏢 **Enterprise Ready**
- Production-tested reliability
- Comprehensive security features
- Scalable architecture

## Quick Start

```python
from odin_sdk import OdinClient, OdinMessage

# Initialize client
client = OdinClient(api_key="your-api-key")

# Create and send message
message = client.create_message()\\
    .set_ids("trace-1", "session-1", "agent-1", "agent-2")\\
    .set_role("assistant")\\
    .set_content("Hello from AI Agent!")\\
    .build()

# Send with automatic rule evaluation
response = client.send_message(message)
print(f"Action: {response.action_taken}")
```

## Plugin Development

```python
from odin_sdk.plugins import BasePlugin

class MyPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "my-plugin"
    
    async def process_message(self, message, context):
        # Custom processing logic
        return message
```

## Enterprise Features

- **Multi-tenancy support**
- **Advanced analytics dashboard** 
- **Custom rule development**
- **24/7 enterprise support**
- **SLA guarantees**
- **On-premise deployment options**

## Use Cases

- **AI Agent Orchestration**: Coordinate multiple AI agents
- **Quality Assurance**: Automatic message validation and healing
- **Compliance Monitoring**: Ensure AI communications meet regulations
- **Performance Optimization**: Real-time monitoring and optimization
- **Enterprise Integration**: Connect AI systems across organizations

## Pricing

- **Developer**: Free for up to 10K messages/month
- **Professional**: $199/month - 100K messages, advanced features
- **Enterprise**: Custom pricing - Unlimited messages, dedicated support

## Support

- 📚 [Documentation](https://docs.odin-protocol.com)
- 💬 [Community Discord](https://discord.gg/odin-protocol)
- 🎫 [Enterprise Support](https://odin-protocol.com/support)
- 🌟 [GitHub](https://github.com/odin-protocol/python-sdk)

Transform your AI systems with the ODIN Protocol today!
"""

setup(
    name="odin-protocol",
    version=version,
    author="ODIN Protocol Team",
    author_email="sdk@odin-protocol.com",
    description="Revolutionary AI Communication Protocol with Self-Healing Capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/odin-protocol/python-sdk",
    project_urls={
        "Homepage": "https://odin-protocol.com",
        "Documentation": "https://docs.odin-protocol.com",
        "Repository": "https://github.com/odin-protocol/python-sdk",
        "Bug Tracker": "https://github.com/odin-protocol/python-sdk/issues",
        "Enterprise": "https://odin-protocol.com/enterprise"
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Distributed Computing",
        "Topic :: Communications",
    ],
    python_requires=">=3.8",
    install_requires=[
        "protobuf>=4.0.0",
        "httpx>=0.24.0",
        "asyncio",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "flake8>=5.0.0",
        ],
        "enterprise": [
            "redis>=4.0.0",
            "pydantic>=2.0.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
        ],
        "analytics": [
            "pandas>=1.5.0",
            "numpy>=1.21.0",
            "matplotlib>=3.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "odin=odin_sdk.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "odin_sdk": ["*.proto", "*.yaml", "*.json"],
    },
    keywords=[
        "ai", "artificial-intelligence", "communication", "protocol", 
        "messaging", "agents", "rule-engine", "self-healing",
        "enterprise", "sdk", "api", "microservices"
    ],
    license="Commercial",
    zip_safe=False,
)

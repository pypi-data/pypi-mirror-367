# Groclake Agent Manager

A Python package for automated Docker deployment and agent management with container orchestration capabilities.

## Features

- **Automated Docker Environment Setup**: Installs and configures Docker CE on CentOS 9 systems
- **Agent Container Deployment**: Deploy Groclake agent containers with optimized configurations
- **Status Verification**: Verify agent container deployment and running status
- **Configuration Management**: Centralized configuration with sensible defaults for agent management
- **Industry Standard Naming**: Follows Python packaging best practices and naming conventions

## Installation

```bash
pip install groclake-agent-manager
```

## Usage

### Command Line Interface

```bash
# Perform full agent manager deployment (Docker setup + agent deployment)
groclake-agent-manager

# Or run the module directly
python -m groclake_agent_manager.agent_manager
```

### Python API

```python
from groclake_agent_manager import (
    deploy_groclake_agent_manager,
    deploy_groclake_agent,
    setup_docker_environment
)

# Perform complete agent manager deployment
deploy_groclake_agent_manager()

# Deploy agent container with custom settings
deploy_groclake_agent(
    container_name="my_agent",
    deployment_port=8080
)

# Setup Docker environment only
setup_docker_environment()
```

## Configuration

The package uses the following default configurations for agent management:

| Setting | Default Value | Description |
|---------|---------------|-------------|
| Agent Container Name | `server_agent_v16` | Default agent container name |
| Agent Deployment Port | `21026` | Default port for agent deployment |
| Docker Image Prefix | `tarunplotch` | Docker registry prefix for agent images |
| Auth Mount Path | `/etc/groclake/auth` | Authentication mount path for agents |
| Gunicorn Workers | `1` | Number of Gunicorn workers per agent |
| Worker Class | `eventlet` | Gunicorn worker class for agent processes |
| Worker Connections | `80` | Gunicorn worker connections for agent scaling |
| Bind Address | `0.0.0.0` | Network binding address for agent services |

## Architecture

The Groclake Agent Manager follows a modular architecture:

- **`agent_manager.py`**: Core agent management functionality
- **`setup_docker_environment()`**: Docker environment setup and configuration
- **`deploy_groclake_agent()`**: Individual agent container deployment
- **`deploy_groclake_agent_manager()`**: Complete agent manager deployment orchestration

## Requirements

- Python 3.7+
- CentOS 9 (for Docker installation)
- Sudo privileges (for Docker operations)
- Network access to Docker registry

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd groclake-agent-manager

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Run tests (when implemented)
python -m pytest
```

### Code Structure

```
groclake-agent-manager/
├── groclake_agent_manager/
│   ├── __init__.py          # Package initialization and exports
│   └── agent_manager.py     # Core agent management functionality
├── setup.py                 # Package installation configuration
├── pyproject.toml          # Modern Python packaging
└── README.md               # This file
```

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here] 

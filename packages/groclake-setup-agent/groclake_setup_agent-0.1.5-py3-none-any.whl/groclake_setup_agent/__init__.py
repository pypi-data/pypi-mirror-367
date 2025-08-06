"""
Groclake Agent Manager Package

A Python package for deploying Docker containers with automated Docker installation
and container management capabilities.

This package provides functionality to:
- Install Docker on CentOS 9 systems
- Deploy Docker containers with custom configurations
- Verify container deployment status
"""

__version__ = "0.1.5"
__author__ = "Plotch.ai"
__description__ = "Agent Deployment Manager deployment automation tool"

from .setup_agent import (
    setup_docker_environment,
    groclake_deployment_manager_deploy,
    groclake_setup_agent_deploy,
    main
)

__all__ = [
    "setup_docker_environment",
    "groclake_deployment_manager_deploy", 
    "groclake_setup_agent_deploy",
    "main"
]


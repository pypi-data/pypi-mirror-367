import subprocess
from typing import List, Optional
import subprocess
import socket
import json
import requests
from typing import List, Optional

# Constants
GROCLAKE_AGENT_CONTAINER_NAME = "deployment_agent"
GROCLAKE_AGENT_DEPLOYMENT_PORT = 21028
GROCLAKE_DOCKER_IMAGE_PREFIX = "tarunplotch"
GROCLAKE_AUTH_MOUNT_PATH = "/etc/groclake/auth"
GROCLAKE_GUNICORN_WORKERS = 1
GROCLAKE_GUNICORN_WORKER_CLASS = "eventlet"
GROCLAKE_GUNICORN_WORKER_CONNECTIONS = 80
GROCLAKE_GUNICORN_BIND_ADDRESS = "0.0.0.0"
CALLBACK_ENDPOINT = "http://35.244.33.240:21026/query"



def get_server_ip() -> str:
    try:
        result = subprocess.run("hostname -I", shell=True, capture_output=True, text=True)
        return result.stdout.strip().split()[0]
    except Exception as e:
        print(f"Failed to fetch server IP: {e}")
        return "unknown"

def post_deployment_callback(container_name: str, deployment_port: int, server_ip: str):
    payload = {
        "header": {
            "version": "1.0",
            "message": "Request",
            "apc_id": "636601a7-3b8a-4c67-b061-b8310ee05acb",
            "client_agent_uuid": "636601a7-3b8a-4c67-b061-b8310ee05acb",
            "server_agent_uuid": "c8ae2a89-4cb7-4971-986f-fb8943ab6f95",
            "message_id": "0fcbf0bf-0c2f-40fb-bd5a-16c798ce337d",
            "task_id": "0fcbf0bf-0c2f-40fb-bd5a-16c798ce337d"
        },
        "body": {
            "query_text": f"{container_name} deployed successfully",
            "intent": "",
            "entities": [
                {"monitor_id": "MON_1752037270_7d1e0f93"},
                {"deployment_port": deployment_port},
                {"server_ip": server_ip}
            ],
            "metadata": {
                "session_token": "groc_session_d1b6f8d193904a22bd723248d647de83",
                "customer_id": "user_af9f5991654a",
                "user_id": "user_af9f5991654a",
                "account_id": "acct_plotch_572121",
                "timestamp": 1752491979171
            }
        }
    }

    try:
        response = requests.post(CALLBACK_ENDPOINT, json=payload, timeout=8)
        print(f"POST request sent. Status: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"POST callback failed (non-breaking): {e}")
def setup_docker_environment() -> None:
    """Install Docker on CentOS system for Groclake Agent Manager.
    
    This function installs Docker CE and related components on a CentOS 9 system
    using the official Docker repository. This is a prerequisite for deploying
    Groclake agent containers.
    """
    print("Setting up Docker environment for Groclake Agent Manager...")
    docker_install_commands = [
        "sudo dnf -y remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine || true",
        "sudo dnf -y install dnf-plugins-core",
        "sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo",
        "sudo dnf -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
        "sudo systemctl enable docker",
        "sudo systemctl start docker"
    ]
    
    for command in docker_install_commands:
        subprocess.run(command, shell=True, check=True)

def groclake_deployment_manager_deploy(
    container_name: str = GROCLAKE_AGENT_CONTAINER_NAME,
    deployment_port: int = GROCLAKE_AGENT_DEPLOYMENT_PORT
) -> None:
    """Deploy a Groclake agent container with the specified configuration.
    
    Args:
        container_name: Name of the Groclake agent container to deploy
        deployment_port: Port number for the agent deployment
    """
    docker_image_name = f"{GROCLAKE_DOCKER_IMAGE_PREFIX}/{container_name}:latest"
    print(f"Pulling Groclake agent image: {docker_image_name}")
    subprocess.run(["sudo", "docker", "pull", docker_image_name], check=True)

    container_instance_name = f"{container_name}_container"
    print(f"Deploying Groclake agent container: {container_instance_name}")
    
    docker_run_command = [
        "sudo", "docker", "run", "-d",
        "--name", container_instance_name,
        "-p", f"{deployment_port}:{deployment_port}",
        "-v", f"{GROCLAKE_AUTH_MOUNT_PATH}:{GROCLAKE_AUTH_MOUNT_PATH}:ro",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "--user", "root",
        docker_image_name,
        "sh", "-c",
        f"gunicorn --workers {GROCLAKE_GUNICORN_WORKERS} "
        f"--worker-class {GROCLAKE_GUNICORN_WORKER_CLASS} "
        f"--worker-connections {GROCLAKE_GUNICORN_WORKER_CONNECTIONS} "
        f"-b {GROCLAKE_GUNICORN_BIND_ADDRESS}:{deployment_port} "
        f"groclake_deployment_manager:app"
    ]
    subprocess.run(docker_run_command, check=True)

    # Verify container is running
    container_status_command = [
        "sudo", "docker", "ps", 
        "--filter", f"name={container_instance_name}", 
        "--filter", "status=running", 
        "--format", "{{.Names}}"
    ]
    status_process = subprocess.run(
        container_status_command, 
        capture_output=True, 
        text=True, 
        check=True
    )
    running_containers = status_process.stdout.strip().splitlines()

    if container_instance_name in running_containers:
        print(f"Groclake agent container '{container_instance_name}' is running successfully.")
        server_ip = get_server_ip()
        post_deployment_callback(container_name, deployment_port, server_ip)
    else:
        raise RuntimeError(f"Groclake agent container '{container_instance_name}' failed to start.")

def groclake_setup_agent_deploy() -> None:
    """Perform a complete deployment of the Groclake Agent Manager.
    
    This function orchestrates the entire deployment process for the Groclake Agent Manager:
    1. Sets up Docker environment on CentOS 9
    2. Deploys the Groclake agent container with default settings
    """
    setup_docker_environment()
    groclake_deployment_manager_deploy()

def main() -> None:
    """Main entry point for the Groclake Agent Manager deployment script."""
    groclake_setup_agent_deploy()

if __name__ == "__main__":
    main()


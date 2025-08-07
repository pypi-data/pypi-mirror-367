# k3sprovision

k3sprovision is a Python package for automated provisioning and management of k3s clusters using Ansible and shell commands. It supports master/worker node setup, high availability with Kube-VIP, and integrates with Ansible inventory files.

## Features
- Provision k3s clusters with master and worker nodes
- Bootstrap master nodes and join additional masters/workers
- Install and configure Kube-VIP for high availability
- Retrieve and apply Kube-VIP manifests
- Gather host information from Ansible inventory
- Colorized logging and shell command execution

## Requirements
- Python 3.8+
- Ansible (Python package)
- PyYAML
- jq, curl, k3sup, kubectl, ssh (available in shell)

## Installation
Install via pip (after publishing to PyPI):
```bash
pip install k3sprovision
```

## Usage Example
```python
from k3sprovision import ClusterProvisioner

# Example config dictionary
config = {
    "cluster": "mycluster",
    "inventory": "inventory/inventory.yml",
    "k3s_version": "v1.28.5+k3s1",
    "kube_vip_version": "v0.6.4",
    "kubectl_config": "~/.kube/config",
    "ssh_key": "~/.ssh/id_rsa"
}

provisioner = ClusterProvisioner(config)
provisioner.run()  # Provisions the cluster end-to-end
```

## API Reference

### ClusterProvisioner
Handles provisioning and setup of k3s clusters.

#### `__init__(self, config: dict = None)`
Initializes with a config dict or environment variables.

#### `bootstrap_master(self)`
Bootstraps the first master node using k3sup.

#### `get_kube_vip_latest_version(self) -> str`
Fetches the latest Kube-VIP version from GitHub.

#### `download_kube_vip_file(self)`
Downloads the Kube-VIP manifest YAML for the specified version.

#### `install_kube_vip(self)`
Installs Kube-VIP for high availability networking.

#### `bootstrap_masters_join_cluster(self)`
Joins additional master nodes to the cluster.

#### `bootstrap_worker_join_cluster(self)`
Joins worker nodes to the cluster.

#### `run(self)`
Runs the full provisioning workflow: master bootstrap, Kube-VIP install, join masters/workers, install cloud provider.

### Cluster
Represents a k3s cluster and gathers host info from Ansible inventory.

#### `__init__(self, inventory_file: str, cluster: str)`
Loads inventory and variables for the specified cluster group.

#### `hosts`
Dictionary with keys `master`, `masters`, and `workers`, each containing host info.

### Helper
Utility functions for logging, shell command execution, and YAML parsing.

#### `run_shell(cmd: str, output_return: bool = False, output_print: bool = False) -> str`
Runs a shell command and returns or prints output.

#### `get_yaml(filename: str)`
Loads a YAML file and returns its contents.

#### Logging functions
`log_info`, `log_error`, `log_warning`, `log_debug`, `log_critical`, `log_shell` for colorized output.

## Directory Structure

```
k3sprovision/
    __init__.py
    cluster.py
    helper.py
    provisioner.py
```

## License
See LICENSE file for details.

## Author
Omniopenverse <omniopenverse@gmail.com>

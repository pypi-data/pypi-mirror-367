import os
import json
from .helper import Helper
from .cluster import Cluster


class ClusterProvisioner:
    """
    Handles the provisioning and setup of a k3s cluster, including master and worker nodes,
    and the installation of Kube-VIP for high availability.
    """
    def __init__(self, config: dict = None):
        """
        Initialize the ClusterProvisioner with configuration.
        Args:
            config (dict): Configuration dictionary for the cluster setup.

        Example:
            config = {
                "cluster": STRING,
                "inventory": STRING,
                "k3s_version": STRING or None,
                "kube_vip_version": STRING or None,
                "kubectl_config": STRING,
                "ssh_key": STRING
            }
        """
        if config is None:
            config = {
                "cluster": os.environ.get("CLUSTER"),
                "inventory": os.environ.get("INVENTORY"),
                "k3s_version": os.environ.get("K3S_VERSION"),
                "kube_vip_version": os.environ.get("KUBE_VIP_VERSION"),
                "kubectl_config": os.environ.get("KUBECTL_CONFIG"),
                "ssh_key": os.environ.get("SSH_KEY")
            }
        self.config = config
        self.helper = Helper()
        self.cluster = Cluster(
            inventory_file=config["inventory"],
            cluster=config["cluster"]
        )

    def bootstrap_master(self):
        """
        Bootstrap the first k3s master node using k3sup and the provided configuration.
        Returns:
            int: 0 on success.
        """
        cmd = [
            "k3sup", "install",
            "--cluster",
            "--context", "default",
            "--ip", self.cluster.hosts["master"]["ip"],
            "--user", self.cluster.hosts["master"]["user"],
            "--sudo",
            "--k3s-channel", "stable",
            "--tls-san", self.cluster.hosts["master"]["ip"],
            "--ssh-key", self.config["ssh_key"],
            "--k3s-extra-args",
                f'"--disable traefik --disable servicelb --flannel-iface={ self.cluster.hosts["master"]["interface"] } --node-ip={ self.cluster.hosts["master"]["ip"] } --node-taint node-role.kubernetes.io/master=true:NoSchedule"',
            "--merge",
            "--local-path", self.config["kubectl_config"],
            "--context", "k3s-ha",
        ]
        if self.config["k3s_version"] is not None:
            cmd.append(f"--k3s-version {self.config['k3s_version']}")
        self.helper.run_shell(" ".join(cmd), output_print = True)
        self.helper.log_info(f"Master node { self.cluster.hosts['master']['hostname'] } bootstrapped successfully!")
        return 0

    def get_kube_vip_latest_version(self) -> str:
        """
        Retrieve the latest Kube-VIP version from GitHub releases.
        Returns:
            str: The latest Kube-VIP version string.
        """
        cmd = [
            "curl", "-sL", "https://api.github.com/repos/kube-vip/kube-vip/releases",
            "|", "jq", "-r", '".[0].name"'
        ]
        return self.helper.run_shell(" ".join(cmd), output_return = True).strip("\n")

    def download_kube_vip_file(self):
        """
        Download the Kube-VIP manifest YAML for the specified version and configuration.
        Returns:
            str: Path to the downloaded Kube-VIP YAML file.
        """
        destination = f"/tmp/kube-vip-{ self.config['kube_vip_version'] }.yaml"
        cmd_get_kube_vip_yaml = [
            "ssh", self.cluster.hosts["master"]["hostname"], "sudo",
            "ctr", "run", "--rm", "--net-host", f"ghcr.io/kube-vip/kube-vip:{ self.config['kube_vip_version'] }",
            "vip", "/kube-vip",
            "manifest", "daemonset",
                f"--interface", self.cluster.hosts["master"]["interface"],
                f"--address", self.cluster.hosts["master"]["ip"],
                "--inCluster",
                "--taint",
                "--controlplane",
                "--services",
                "--arp",
                "--leaderElection",
            "|", "tee", f"{ destination }"
        ]
        self.helper.run_shell(" ".join(cmd_get_kube_vip_yaml), output_return = True)
        self.helper.log_info(f"Kube Vip Yaml generated '{ destination }' successfully!")
        return destination

    def install_kube_vip(self):
        """
        Install Kube-VIP on the cluster for high availability networking.
        Returns:
            int: 0 on success.
        """
        if self.config["kube_vip_version"] is None:
            self.config["kube_vip_version"] = self.get_kube_vip_latest_version()
        self.helper.log_info(f"Kube Vip Version: { self.config['kube_vip_version'] }")
        kube_vip_file = self.download_kube_vip_file()
        self.helper.run_shell("kubectl apply -f https://kube-vip.io/manifests/rbac.yaml")
        self.helper.log_info("Kube vip rbac created successfully!")
        cmd_pull_kube_vip_image = [
            "ssh", self.cluster.hosts["master"]["hostname"],
            "sudo", "ctr", "image", "pull", f"ghcr.io/kube-vip/kube-vip:{ self.config['kube_vip_version'] }"
        ]
        self.helper.run_shell(" ".join(cmd_pull_kube_vip_image), output_print = False, output_return = False)
        self.helper.run_shell(f"kubectl apply -f { kube_vip_file }")
        self.helper.log_info("Kube-VIP for HA installed!")
        return 0

    def bootstrap_masters_join_cluster(self):
        """
        Join additional master nodes to the k3s cluster using k3sup.
        """
        for node in self.cluster.hosts["masters"]:
            node = list(node.values())[0]
            cmd_node_join_cluster = [
                "k3sup", "join",
                "--ip", node["ip"],
                "--user", node["user"],
                "--sudo",
                "--server",
                "--server-ip", self.cluster.hosts["master"]["ip"],
                "--k3s-channel", "stable",
                "--ssh-key", self.config["ssh_key"],
                "--k3s-extra-args",
                    f'"--disable traefik --disable servicelb --flannel-iface={ node['interface'] } --node-ip={ node['ip'] } --node-taint node-role.kubernetes.io/master=true:NoSchedule"',
            ]
            if self.config["k3s_version"] is not None:
                cmd_node_join_cluster.append(f"--k3s-version {self.config['k3s_version']}")
            self.helper.run_shell(" ".join(cmd_node_join_cluster))
            self.helper.log_info(f"Node { node['hostname'] } has joined successfully!")
        return

    def bootstrap_worker_join_cluster(self):
        """
        Join worker nodes to the k3s cluster using k3sup.
        """
        for node in self.cluster.hosts["workers"]:
            node = list(node.values())[0]
            cmd_node_join_cluster = [
                "k3sup", "join",
                "--ip", node["ip"],
                "--user", node["user"],
                "--sudo",
                "--server-ip", self.cluster.hosts["master"]["ip"],
                "--k3s-channel", "stable",
                "--ssh-key", self.config["ssh_key"],
                "--k3s-extra-args",
                    '"--node-label worker=true"'
            ]
            if self.config["k3s_version"] is not None:
                cmd_node_join_cluster.append(f"--k3s-version {self.config['k3s_version']}")
            self.helper.run_shell(" ".join(cmd_node_join_cluster))
            self.helper.log_info(f"Node { node['hostname'] } has joined successfully!")
        return

    def run(self):
        """
        Execute the full cluster provisioning workflow: bootstrap master, install Kube-VIP,
        join additional masters and workers, and install the Kube-VIP cloud provider.
        Returns:
            int: 0 on success.
        """
        # Get hosts info
        self.helper.log_info(f"Cluster: { json.dumps(self.cluster.hosts, indent=2) }")
        self.bootstrap_master()
        self.install_kube_vip()
        self.bootstrap_masters_join_cluster()
        self.bootstrap_worker_join_cluster()
        self.helper.run_shell("kubectl apply -f https://raw.githubusercontent.com/kube-vip/kube-vip-cloud-provider/main/manifest/kube-vip-cloud-controller.yaml")
        self.helper.log_info("Kube-VIP Cloud Provider installed successfully!")
        return 0

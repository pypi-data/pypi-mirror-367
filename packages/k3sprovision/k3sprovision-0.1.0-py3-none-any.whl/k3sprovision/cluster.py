import json
from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from .helper import Helper


class Cluster:
    """
    Represents a k3s cluster and provides methods to gather host information from an Ansible inventory.
    """
    def __init__(self, inventory_file: str, cluster: str):
        """
        Initialize the Cluster object and load inventory/variables.
        Args:
            inventory_file (str): Path to the Ansible inventory file.
            cluster (str): Name of the cluster group in the inventory.
        Raises:
            Exception: If inventory or variable manager cannot be loaded.
        """
        self.inventory_file = inventory_file
        self.cluster = cluster
        self.hosts = {}

        try:
            loader = DataLoader()
            self.__inventory = InventoryManager(loader=loader, sources=inventory_file)
            self.__variable_manager = VariableManager(loader=loader, inventory=self.__inventory)
        except Exception as exc:
            Helper.log_error(f"Failed to Read inventory: {self.inventory_file}. Exception: {exc}")
            raise Exception(f"Failed to Read inventory: {self.inventory_file}. Exception: {exc}")

        self.hosts = self.__get_hosts()

    def __get_facts(self, hostname: str) -> dict:
        """
        Gather Ansible facts for a given host using the setup module.
        Args:
            hostname (str): Hostname to gather facts for.
        Returns:
            dict: The facts dictionary for the host.
        Raises:
            Exception: If facts cannot be gathered or parsed.
        """
        cmd = [
            "ansible", hostname,
            "--module-name", "setup",
            "--inventory", self.inventory_file, "-o"
        ]
        result_stdout = Helper.run_shell(" ".join(cmd), output_return = True)
        try:
            start_index = result_stdout.find('{')
            if start_index != -1:
                facts = json.loads(result_stdout[start_index:])
            else:
                Helper.log_error(f"Failed to gather facts for host: { hostname }. Bad result stdout for { ' '.join(cmd) }: { result_stdout }")
                raise Exception(f"Failed to gather facts for host: { hostname }. Bad result stdout for { ' '.join(cmd) }: { result_stdout }")
        except Exception as this_expection:
            Helper.log_error(f"Failed to gather facts for host: { hostname }. Exception { this_expection }")
            raise Exception(f"Failed to gather facts for host: { hostname }. Exception { this_expection }")
        return facts

    def __get_vars(self, hostname: str) -> dict:
        """
        Get host variables and network interface information for a given host.
        Args:
            hostname (str): Hostname to get variables for.
        Returns:
            dict: Dictionary with hostname, ip, user, and interface.
        Raises:
            Exception: If variables cannot be retrieved.
        """
        inventory_vars = self.__variable_manager.get_vars(
            host = self.__inventory.get_host(hostname)
        )
        facts = self.__get_facts(hostname)["ansible_facts"]
        try:
            vars = {
                "hostname": hostname,
                "ip": inventory_vars["ansible_host"],
                "user": inventory_vars["ansible_user"],
                "interface": facts["ansible_default_ipv4"]["interface"]
            }
        except Exception as exc:
            Helper.log_error(f"Failed to get vars for host { hostname }. Exception: { exc }")
            raise Exception(f"Failed to get vars for host { hostname }. Exception: { exc }")
        return vars

    def __get_hosts(self) -> dict:
        """
        Build a dictionary of all hosts in the cluster, including master, masters, and workers.
        Returns:
            dict: Dictionary with keys 'master', 'masters', and 'workers', each containing host info.
        """
        hosts = {
            "master": {},
            "masters": [],
            "workers": []
        }
        hosts["master"] = self.__get_vars(
            str(self.__inventory.get_hosts(f"master_{ self.cluster }")[0])
        )
        for host_grp in ["masters", "workers"]:
            for host in self.__inventory.get_hosts(f"{ host_grp }_{ self.cluster }"):
                hostname = str(host)
                hosts[host_grp].append(
                    {
                        hostname: self.__get_vars(hostname)
                    }
                )
        return hosts

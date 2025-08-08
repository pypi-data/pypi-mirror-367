#!/usr/bin/env python3
# eformer.escale.tpexec.tpu_patcher - Ray TPU Cluster Setup for TPU Slices
# This script properly configures Ray to recognize all TPU cores across hosts.
# Copyright 2025 The EasyDeL/eFormer Author @erfanzar (Erfan Zare Chavoshi).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

import requests
import yaml

TPU_VERSION = os.getenv("TPU_VERSION", "v4")
TPU_SLICE_SIZE = int(os.getenv("TPU_SLICE_SIZE", "8"))
TPU_CORES_PER_HOST = int(os.getenv("TPU_CORES_PER_HOST", "4"))
SSH_USER = os.getenv("PATCHER_USER")
INTERNAL_IPS = ["0.0.0.0"]
EXTERNAL_IPS = ["0.0.0.0"]


def find_ray_in_current_env() -> pathlib.Path:
    """Return the absolute path to 'ray' inside the current venv (or system)."""
    if ray := os.getenv("RAY_EXECUTABLE_PATH"):
        return pathlib.Path(ray).expanduser().resolve()

    bin_dir = pathlib.Path(sys.executable).parent
    ray_path = bin_dir / "ray"

    if ray_path.is_file():
        return ray_path

    ray_path = shutil.which("ray")
    if ray_path:
        return pathlib.Path(ray_path)

    raise FileNotFoundError("ray executable could not be located")


RAY_PATH = str(find_ray_in_current_env())


def get_external_ip():
    """Get the external IP address of the machine."""
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        if response.status_code == 200:
            return response.text
        response = requests.get("https://ipinfo.io/ip", timeout=5)
        if response.status_code == 200:
            return response.text
        response = requests.get("https://checkip.amazonaws.com", timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        return "Could not determine external IP"
    except Exception as e:
        return f"Error getting external IP: {e}"


def get_local_ip():
    """Get the local IP address of the machine."""
    try:
        hostname_output = subprocess.check_output("hostname -I", shell=True).decode().strip()
        return hostname_output.split()[0]
    except Exception as e:
        print(f"Error getting local IP: {e}")
        return "127.0.0.1"


def run_ssh_command(
    target_ip,
    command,
    use_sudo=False,
):
    """Run a command on a remote host via SSH."""
    print(f"Running SSH command on {target_ip}: {command}")

    if use_sudo:
        full_command = f"sudo {command}"
    else:
        full_command = command

    ssh_command = [
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "ConnectTimeout=5",
        f"{SSH_USER}@{target_ip}",
        full_command,
    ]

    try:
        subprocess.run(ssh_command, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"SSH command failed on {target_ip}")
        return False


def run_local_command(
    command,
    use_sudo=False,
    check=True,
    capture_output=False,
):
    """Run a command locally with optional output capture."""
    if isinstance(command, list):
        cmd_str = " ".join(command)
    else:
        cmd_str = command

    print(f"Running local command: {cmd_str}")

    if use_sudo and not isinstance(command, list):
        full_command = f"sudo {command}"
    elif use_sudo and isinstance(command, list):
        full_command = ["sudo", *command]
        full_command = " ".join(full_command)
    else:
        full_command = command
        if isinstance(full_command, list):
            full_command = " ".join(full_command)
    try:
        if capture_output:
            if isinstance(full_command, list):
                result = subprocess.run([full_command], shell=True, capture_output=True)
            else:
                result = subprocess.run([full_command], shell=True, capture_output=True)
            return result.stdout
        else:
            if isinstance(full_command, list):
                subprocess.run(full_command, shell=True, check=check)
            else:
                subprocess.run(full_command, shell=True, check=check)
            return True
    except subprocess.CalledProcessError:
        print(f"Local command failed: {cmd_str}")
        return False if not capture_output else ""
    except FileNotFoundError:
        print(f"Command not found: {cmd_str}")
        return False if not capture_output else ""


def create_verification_script():
    """Create a Python script to verify the Ray cluster setup."""
    script_content = """
import ray
import time
import sys
import os

# Try to connect multiple times
for i in range(5):
    try:
        ray.init(address='auto')
        break
    except Exception as e:
        print(f"Connection attempt {i+1} failed: {e}")
        time.sleep(5)
        if i == 4:  # Last attempt failed
            print("Could not connect to Ray cluster")
            sys.exit(1)

# Print cluster resources
try:
    resources = ray.cluster_resources()
    print("\\nCLUSTER RESOURCES:\\n==================")
    for k, v in sorted(resources.items()):
        print(f"{k}: {v}")

    # Check if we have the expected TPUs
    tpu_count = resources.get('TPU', 0)
    print(f"\\nTOTAL TPU COUNT: {tpu_count}")

    # Get expected TPU count from environment variable
    expected_tpu = int(os.environ.get('EXPECTED_TPU_COUNT', 64))
    if tpu_count < expected_tpu * 0.9:  # Allow for 10% missing
        print(f"WARNING: Not all TPU cores are detected! Expected ~{expected_tpu}")
        sys.exit(2)
    else:
        print(f"SUCCESS: TPU cores detected ({tpu_count}/{expected_tpu})")
except Exception as e:
    print(f"Error getting cluster resources: {e}")
    sys.exit(3)

ray.shutdown()
"""

    with open("/tmp/verify_ray_tpu.py", "w") as f:
        f.write(script_content)


def check_ray_running(ip):
    """Check if Ray is already running on a node."""
    local_ip = get_local_ip()

    if local_ip == ip:
        try:
            subprocess.check_output("ps aux | grep -v grep | grep 'ray::IDLE'", shell=True)
            return True
        except subprocess.CalledProcessError:
            return False
    else:
        return run_ssh_command(ip, "ps aux | grep -v grep | grep 'ray::IDLE'", False)


def start_ray_head(head_ip, use_external):
    """Start Ray head node."""
    global TPU_CORES_PER_HOST, TPU_VERSION, TPU_SLICE_SIZE

    print(f"Starting Ray head node on {head_ip}")
    local_ip = get_local_ip()

    if check_ray_running(head_ip):
        print(f"Ray is already running on head node {head_ip}. Stopping it first...")
        if local_ip == head_ip:
            run_local_command([RAY_PATH, "stop"], False)
        else:
            run_ssh_command(head_ip, f"{RAY_PATH} stop", False)
        time.sleep(3)

    resources = json.dumps(
        {
            "TPU": TPU_CORES_PER_HOST,
            f"TPU-{TPU_VERSION}-{TPU_SLICE_SIZE}-head": 1,
            f"accelerator_type:TPU-{TPU_VERSION.upper()}": 1,
        }
    )
    if local_ip == head_ip:
        print("Starting Ray head node locally")
        cmd = (
            RAY_PATH,
            "start",
            "--head",
            "--port=6379",
            f"--resources='{resources}'",
            f"--node-ip-address={head_ip}",
            "--dashboard-host=0.0.0.0",
        )
        success = run_local_command(cmd, False)
    else:
        print("Starting Ray head node remotely")
        cmd = (
            f"{RAY_PATH} start --head --port=6379 --resources='{resources}' --node-ip-address={head_ip} "
            "--dashboard-host=0.0.0.0"
        )
        success = run_ssh_command(head_ip, cmd, False)

    if not success:
        print("Failed to start Ray head node")
        return False

    return True


def start_ray_worker(head_ip, worker_ip, use_external, worker_count):
    """Start Ray worker node."""
    global TPU_CORES_PER_HOST, TPU_VERSION, INTERNAL_IPS
    i = 0
    for idx, ip in enumerate(INTERNAL_IPS):
        if ip == worker_ip:
            i = idx - 1
            break

    print(f"Starting Ray worker on {worker_ip} (index {i})")
    local_ip = get_local_ip()
    if check_ray_running(worker_ip):
        print(f"Ray is already running on worker node {worker_ip}. Stopping it first...")
        if local_ip == worker_ip:
            run_local_command([RAY_PATH, "stop"], False)
        else:
            run_ssh_command(worker_ip, f"{RAY_PATH} stop", False)
        time.sleep(3)
    resources = (
        f'{{"TPU":{TPU_CORES_PER_HOST},"TPU-{TPU_VERSION}-worker-{i}":1,"accelerator_type:TPU-{TPU_VERSION.upper()}":1}}'
    )
    if local_ip == worker_ip:
        print("Starting Ray worker locally")
        cmd = f"{RAY_PATH} start --address={head_ip}:6379 --resources='{resources}' --node-ip-address={worker_ip}"
        success = run_local_command(cmd, False)
    else:
        print("Starting Ray worker remotely")
        cmd = f"{RAY_PATH} start --address={head_ip}:6379 --resources='{resources}' --node-ip-address={worker_ip}"
        success = run_ssh_command(worker_ip, cmd, False)

    if success:
        print(f"Successfully started Ray worker on {worker_ip}")
        return True
    else:
        print(f"Failed to start Ray worker on {worker_ip}")
        return False


def verify_ray_cluster(head_ip, expected_tpu_count, allow_head_only=False):
    """Verify Ray cluster setup."""
    print("Verifying Ray cluster setup...")
    if allow_head_only and expected_tpu_count == 0:
        print("Head-only node detected (no TPU resources)")
    create_verification_script()
    env = os.environ.copy()
    env["EXPECTED_TPU_COUNT"] = str(expected_tpu_count)
    try:
        subprocess.run(["python", "/tmp/verify_ray_tpu.py"], env=env, check=True)
        print("Verification successful!")
        status = 0
    except subprocess.CalledProcessError as e:
        print(f"Verification failed with status {e.returncode}")
        status = e.returncode
    os.remove("/tmp/verify_ray_tpu.py")
    return status == 0


def stop_cluster(use_external):
    """Stop Ray cluster on all nodes."""
    global EXTERNAL_IPS, INTERNAL_IPS

    ips = EXTERNAL_IPS if use_external else INTERNAL_IPS

    print("Stopping Ray on all nodes...")
    local_ip = get_local_ip()

    for ip in ips:
        print(f"Stopping Ray on {ip}...")

        if local_ip == ip:
            print("Stopping Ray locally")
            run_local_command(f"{RAY_PATH} stop", False)
        else:
            run_ssh_command(ip, f"{RAY_PATH} stop", False)

    print("Ray cluster stopped on all nodes.")


def setup_cluster(use_external):
    """Set up Ray cluster."""
    global TPU_CORES_PER_HOST, TPU_VERSION, TPU_SLICE_SIZE, EXTERNAL_IPS, INTERNAL_IPS

    ips = EXTERNAL_IPS if use_external else INTERNAL_IPS

    head_ip = ips[0]
    worker_ips = ips[1:]

    print(f"Setting up Ray cluster with {'external' if use_external else 'internal'} IPs")
    print(f"TPU Version: {TPU_VERSION}")
    print(f"TPU Slice Size: {TPU_SLICE_SIZE}")
    print(f"TPU Cores per Host: {TPU_CORES_PER_HOST}")
    print(f"SSH User: {SSH_USER}")
    print(f"Head node: {head_ip}")
    print(f"Worker nodes: {', '.join(worker_ips)}")
    stop_cluster(use_external)
    print("Waiting for processes to fully stop...")
    time.sleep(5)
    if not start_ray_head(head_ip, use_external):
        print("Failed to start Ray head node. Exiting.")
        return False
    print("Waiting for head node to initialize...")
    time.sleep(10)
    for worker_ip in worker_ips:
        print(f"Starting worker node at {worker_ip}")
        start_ray_worker(head_ip, worker_ip, use_external, len(worker_ips))

    print("Ray cluster setup complete!")
    print(f"Total expected TPU cores: {TPU_SLICE_SIZE}")
    print("Waiting for workers to register resources...")
    time.sleep(15)
    verify_ray_cluster(head_ip, TPU_SLICE_SIZE)

    print("")
    print("IMPORTANT: To use Ray in your applications, initialize with:")
    print(f"ray.init(address='{head_ip}:6379')")

    return True


def test_ssh_connectivity(use_external):
    """Test SSH connectivity to all nodes."""
    global EXTERNAL_IPS, INTERNAL_IPS, SSH_USER

    ips = EXTERNAL_IPS if use_external else INTERNAL_IPS

    print("Testing SSH connectivity to all nodes...")
    all_good = True

    for ip in ips:
        print(f"Testing connection to {ip}... ", end="")

        ssh_command = [
            "ssh",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "ConnectTimeout=5",
            "-o",
            "BatchMode=yes",
            f"{SSH_USER}@{ip}",
            "echo OK",
        ]

        try:
            subprocess.run(
                ssh_command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print("SUCCESS")
        except subprocess.CalledProcessError:
            print("FAILED")
            all_good = False

    if all_good:
        print("All SSH connections successful!")
        return True
    else:
        print("Some SSH connections failed. Please check your SSH setup.")
        print("Make sure your SSH key is added to the authorized_keys file on all nodes.")
        print(f"You may need to run: ssh-copy-id {SSH_USER}@<node-ip>")
        return False


def read_ips_from_yaml(yaml_file):
    """Read IPs from YAML file."""
    global INTERNAL_IPS, EXTERNAL_IPS

    try:
        with open(yaml_file, "r") as file:
            data = yaml.safe_load(file)

        INTERNAL_IPS = data.get("internal_ips", [])
        EXTERNAL_IPS = data.get("external_ips", [])

        if not INTERNAL_IPS:
            print("ERROR: No internal IPs found in the YAML file", file=sys.stderr)
            return False

        print(f"Read {len(INTERNAL_IPS)} internal IPs and {len(EXTERNAL_IPS)} external IPs from {yaml_file}")
        return True

    except Exception as e:
        print(f"ERROR: {e!s}", file=sys.stderr)
        return False


def main():
    global TPU_VERSION, TPU_SLICE_SIZE, SSH_USER, INTERNAL_IPS, EXTERNAL_IPS

    parser = argparse.ArgumentParser(description="Ray TPU Cluster Setup for TPU Slices")
    parser.add_argument("--external", action="store_true", help="Use external IPs instead of internal IPs")
    parser.add_argument("--stop", action="store_true", help="Stop the Ray cluster")
    parser.add_argument("--verify", action="store_true", help="Verify the Ray cluster setup")
    parser.add_argument("--tpu-version", default=TPU_VERSION, help=f"Set TPU version (default: {TPU_VERSION})")
    parser.add_argument(
        "--tpu-slice",
        type=int,
        default=TPU_SLICE_SIZE,
        help=f"Set TPU slice size (default: {TPU_SLICE_SIZE})",
    )
    parser.add_argument("--num-slices", type=int, default=1, help="Number of TPU slices to combine (default: 1)")
    parser.add_argument("--ssh-user", default=SSH_USER, help=f"SSH username to use (default: {SSH_USER})")
    parser.add_argument("--config", help="Path to YAML config file with IP addresses")
    parser.add_argument("--test-ssh", action="store_true", help="Test SSH connectivity to all nodes")
    parser.add_argument(
        "--internal-ips",
        help="Comma-separated list of internal IPs for all slices (e.g. 10.164.0.3,10.164.0.7,...)",
    )
    parser.add_argument(
        "--external-ips",
        help="Comma-separated list of external IPs for all slices (e.g. 35.224.1.1,35.224.1.2,...)",
    )
    parser.add_argument("--self-job", action="store_true", help="Run only on the current machine")
    parser.add_argument("--slice-config", help="Path to YAML config file with slice configurations")
    parser.add_argument("--head-node-ip", help="IP address of external head node (if not using first IP in list)")
    parser.add_argument("--head-only", action="store_true", help="Run this node as head only (no TPU resources)")
    args = parser.parse_args()
    using_external = args.external or args.internal_ips is None
    TPU_VERSION = args.tpu_version
    TPU_SLICE_SIZE = args.tpu_slice
    num_slices = args.num_slices
    total_tpu_cores = TPU_SLICE_SIZE * num_slices

    if args.ssh_user:
        SSH_USER = args.ssh_user

    if args.internal_ips:
        INTERNAL_IPS = args.internal_ips.split(",")
        print(f"Using internal IPs from command line: {INTERNAL_IPS}")

    if args.external_ips:
        EXTERNAL_IPS = args.external_ips.split(",")
        print(f"Using external IPs from command line: {EXTERNAL_IPS}")

    if args.config:
        if not read_ips_from_yaml(args.config):
            print("Failed to read configuration from YAML file.")
            return 1

    slice_configs = []
    if args.slice_config:
        try:
            with open(args.slice_config, "r") as file:
                slice_data = yaml.safe_load(file)
                slice_configs = slice_data.get("slices", [])
                print(f"Loaded {len(slice_configs)} slice configurations")
        except Exception as e:
            print(f"Error reading slice config: {e}")
            return 1
    else:
        ips_to_use = EXTERNAL_IPS if using_external else INTERNAL_IPS
        total_hosts = len(ips_to_use)
        if total_hosts % num_slices != 0:
            print(f"Warning: {total_hosts} hosts cannot be evenly divided into {num_slices} slices")

        hosts_per_slice = total_hosts // num_slices

        for i in range(num_slices):
            start_idx = i * hosts_per_slice
            end_idx = start_idx + hosts_per_slice
            slice_ips = ips_to_use[start_idx:end_idx]

            slice_configs.append(
                {
                    "name": f"slice-{i + 1}",
                    "ips": slice_ips,
                    "tpu_cores": TPU_SLICE_SIZE,
                }
            )

    print("\nSlice Configuration:")
    print("====================")
    for i, slice_config in enumerate(slice_configs):
        print(f"Slice {i + 1}: {slice_config['name']}")
        print(f"  IPs: {slice_config['ips']}")
        print(f"  TPU Cores: {slice_config['tpu_cores']}")
    print(f"Total TPU Cores: {total_tpu_cores}")
    print("====================\n")

    if args.self_job:
        local_ip = get_external_ip() if using_external else get_local_ip()
        external_head_ip = args.head_node_ip
        is_head_only = args.head_only

        print(f"Running in self-job mode on {local_ip}")
        if external_head_ip:
            print(f"Using external head node at: {external_head_ip}")
        if is_head_only:
            print("Running as head-only node (no TPU resources)")

        print(f"Using Ray command: {RAY_PATH}")

        try:
            subprocess.run([RAY_PATH, "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print("ERROR: Ray command not found or not working.")
            print("Please install Ray with: pip install -U ray")
            print("Make sure ray is in your PATH or in ~/.local/bin/")
            print("Exec", str(e))
            return 1

        print("Stopping any existing Ray processes...")
        try:
            subprocess.run([RAY_PATH, "stop"], stderr=subprocess.DEVNULL)
        except Exception:
            print("No Ray process was running or could not stop Ray")

        time.sleep(3)

        if args.stop:
            run_local_command(f"{RAY_PATH} stop", False)
            return 0

        is_external_head = external_head_ip and local_ip == external_head_ip

        if external_head_ip:
            head_ip = external_head_ip
        else:
            ips_to_use = EXTERNAL_IPS if using_external else INTERNAL_IPS
            if not ips_to_use:
                print("Error: No IPs provided")
                return 1
            head_ip = ips_to_use[0]

        # Check if current machine is the head
        is_head_node = is_external_head or (local_ip == head_ip and not external_head_ip)

        if is_head_node:
            print(f"This machine ({local_ip}) is the HEAD node")

            if is_head_only:
                resources = {"head-node": 1, "control-plane": 1, "ray-cluster-head": 1}
                print("Starting as head-only node (no TPU resources)")
            else:
                print("Starting as head node with TPU resources")

                slice_idx = -1
                host_idx_in_slice = -1

                for i, slice_config in enumerate(slice_configs):
                    if local_ip in slice_config["ips"]:
                        slice_idx = i
                        host_idx_in_slice = slice_config["ips"].index(local_ip)
                        break

                if slice_idx == -1 and not is_head_only:
                    ips_to_use = EXTERNAL_IPS if using_external else INTERNAL_IPS
                    if local_ip in ips_to_use:
                        host_idx = ips_to_use.index(local_ip)
                        hosts_per_slice = len(ips_to_use) // num_slices
                        slice_idx = host_idx // hosts_per_slice
                        host_idx_in_slice = host_idx % hosts_per_slice
                    else:
                        print(f"Warning: Local IP {local_ip} not found in slice configuration")
                        slice_idx = 0
                        host_idx_in_slice = 0

                resources = {
                    "TPU": TPU_CORES_PER_HOST,
                    f"TPU-{TPU_VERSION}": TPU_CORES_PER_HOST,
                    f"TPU-{TPU_VERSION}-{TPU_SLICE_SIZE}-head": 1,
                    f"TPU-{TPU_VERSION}-{total_tpu_cores}-global-head": 1,
                    f"accelerator_type:TPU-{TPU_VERSION.upper()}": 1,
                    "head-node": 1,
                    "ray-cluster-head": 1,
                }

                if slice_idx >= 0:
                    resources[f"slice-{slice_idx}"] = 1
                    resources[f"slice-{slice_idx}-host-{host_idx_in_slice}"] = 1

            resources_str = str(resources).replace("'", '"')
            cmd = [
                RAY_PATH,
                "start",
                "--head",
                "--port=6379",
                f"--resources='{resources_str}'",
                f"--node-ip-address={local_ip}",
                "--dashboard-host=0.0.0.0",
            ]

            print(f"Starting Ray head with command: {' '.join(cmd)}")
            success = run_local_command(cmd, False)

            if success:
                print("\nRay head started successfully!")
                print(f"Dashboard available at: http://{local_ip}:8265")
                print(f"Ray cluster address: {local_ip}:6379")
                if is_head_only:
                    print("\nWaiting for TPU workers to connect...")
                    print("Run the script on TPU nodes with --head-node-ip " + local_ip)
            else:
                print("Failed to start Ray head")
                return 1

        else:
            print(f"This machine ({local_ip}) is a WORKER node")
            print(f"Will connect to head node at: {head_ip}")

            ips_to_use = EXTERNAL_IPS if using_external else INTERNAL_IPS
            if external_head_ip and external_head_ip in ips_to_use:
                ips_to_use = [ip for ip in ips_to_use if ip != external_head_ip]

            slice_idx = -1
            host_idx_in_slice = -1

            for i, slice_config in enumerate(slice_configs):
                if local_ip in slice_config["ips"]:
                    slice_idx = i
                    host_idx_in_slice = slice_config["ips"].index(local_ip)
                    break

            if slice_idx == -1:
                if local_ip in ips_to_use:
                    host_idx = ips_to_use.index(local_ip)
                    hosts_per_slice = len(ips_to_use) // num_slices
                    slice_idx = host_idx // hosts_per_slice
                    host_idx_in_slice = host_idx % hosts_per_slice
                else:
                    print(f"Error: Local IP {local_ip} not found in worker configuration")
                    return 1

            is_slice_head = False
            if slice_configs and slice_idx >= 0:
                slice_config = slice_configs[slice_idx]
                is_slice_head = (host_idx_in_slice == 0) and (slice_idx > 0 or external_head_ip)

            resources = {
                "TPU": TPU_CORES_PER_HOST,
                f"TPU-{TPU_VERSION}": TPU_CORES_PER_HOST,
                f"accelerator_type:TPU-{TPU_VERSION.upper()}": 1,
                f"slice-{slice_idx}": 1,
                f"slice-{slice_idx}-host-{host_idx_in_slice}": 1,
            }

            if is_slice_head:
                resources[f"TPU-{TPU_VERSION}-{TPU_SLICE_SIZE}-slice-{slice_idx}-head"] = 1
                print(f"This worker is slice head for slice {slice_idx}")
            else:
                resources[f"TPU-{TPU_VERSION}-worker"] = 1
                resources[f"TPU-{TPU_VERSION}-worker-{slice_idx}-{host_idx_in_slice}"] = 1

            resources_str = json.dumps(resources)
            cmd = f"{RAY_PATH} start --address={head_ip}:6379 --resources='{resources_str}' --node-ip-address={local_ip}"

            print(f"Starting Ray worker with command: {cmd}")
            success = run_local_command(cmd, False)

            if success:
                print("\nRay worker started successfully!")
                print(f"Connected to head at: {head_ip}:6379")
                print(f"Worker resources: {resources}")
            else:
                print("Failed to start Ray worker")
                return 1

        if is_head_node and args.verify:
            print("\nWaiting for cluster to stabilize...")
            time.sleep(10)
            expected_tpu = total_tpu_cores if not is_head_only else total_tpu_cores - TPU_CORES_PER_HOST

            if verify_ray_cluster(head_ip, expected_tpu):
                print("Cluster verification successful!")
            else:
                print("Cluster verification failed!")
                return 1

        return 0

    if args.test_ssh:
        if not test_ssh_connectivity(using_external):
            return 1
        return 0

    if args.stop:
        stop_cluster(using_external)
        return 0
    elif args.verify:
        head_ip = EXTERNAL_IPS[0] if using_external else INTERNAL_IPS[0]
        if verify_ray_cluster(head_ip, total_tpu_cores):
            return 0
        else:
            return 1
    else:
        if setup_cluster(using_external):
            return 0
        else:
            return 1


if __name__ == "__main__":
    sys.exit(main())

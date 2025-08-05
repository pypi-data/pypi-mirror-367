# Flow SDK

[![PyPI](https://img.shields.io/pypi/v/flow-compute.svg)](https://pypi.org/project/flow-compute/)
[![Python](https://img.shields.io/pypi/pyversions/flow-compute.svg)](https://pypi.org/project/flow-compute/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE.txt)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://github.com/foundrytechnologies/flow-v2)
[![Tests](https://img.shields.io/github/actions/workflow/status/foundrytechnologies/flow-v2/tests.yml?label=tests)](https://github.com/foundrytechnologies/flow-v2/actions)
[![Coverage](https://img.shields.io/codecov/c/github/foundrytechnologies/flow-v2)](https://codecov.io/gh/foundrytechnologies/flow-v2)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Discord](https://img.shields.io/discord/1234567890?label=discord)](https://discord.gg/flow-sdk)

**Launch GPU jobs instantly, without DevOps.**

```bash
pip install flow-compute
flow run -c "python train.py"
⠋ Starting GPU task (8x H100)...
✓ Running on NVIDIA H100 80GB HBM3
```

## Why Flow?

Flow SDK lets you run GPU workloads effortlessly:

* **Rapid Iteration**: Launch containers-in-VM in seconds—not minutes (`flow dev`).
* **Zero DevOps**: Skip Kubernetes, driver installs, and cloud consoles.
* **Cost Protection**: Built-in `max_price_per_hour` safeguards.
* **Proven Patterns**: Inspired by best practices at DeepMind, Meta, and OpenAI.

→ [Flow's Design Philosophy](docs/background.md)

## Why Cloud GPUs?

* **Elasticity**: Instantly scale 1 to 1000 GPUs. Pay only for usage.
* **No CapEx**: Zero upfront investment. No long procurement cycles.
* **Efficient Pricing**: Pay per GPU-hour, optimizing experimentation and utilization.

## Quick Start

Get an API key: [app.mithril.ai](https://app.mithril.ai/account/apikeys)

```bash
pip install flow-compute
flow init
flow dev -c 'python train.py'
```

Instantly runs on 8x H100 GPUs. Each command (`flow dev -c`) launches in a fresh container within seconds.

**Workflow Examples:**

* **Batch Jobs**: `flow run "python train.py" -i 8xh100`
* **Config YAML**: `flow run job.yaml`
* **SLURM Script**: `flow run script.slurm`
* **Python API**: `flow.run("train.py", instance_type="8xh100")`
* **Serverless Decorator**: `@flow.function(gpu="a100")`

→ [Choose Your Workflow](#choosing-your-workflow)


## Ideal Use Cases

Flow excels for:

* **Rapid Experimentation**: Short iteration cycles.
* **Elastic, Burst Workloads**: Quick scaling for training runs or hyperparameter tuning.
* **Collaborative GPU Sharing**: Team-friendly development environments.

Avoid Flow for:

* Always-on services with sub-second latency requirements.
* Small models easily run locally.
* Data with strict compliance (healthcare/finance).

## Architecture

Flow SDK cleanly abstracts GPU workload management:

```
Your Code → Flow Unified API → Cloud GPU Infra
```

* **Unified API**: Single interface for multi-cloud GPU infrastructure.
* **Automatic Management**: Drivers, environment, and instances provisioned seamlessly.
* **Real-time Monitoring**: Logs, SSH access, and live tracking built-in.


## Installation

```bash
curl -sSL https://raw.githubusercontent.com/foundrytechnologies/flow-sdk/main/setup.sh | bash
flow init
```

→ [Full Installation Guide](#installation)

## Authentication

Interactive setup:

```bash
flow init
```

Verify:

```bash
flow status
```

## Core Patterns

| Workflow   | Use Case                         | Start-up |
| ---------- | -------------------------------- | -------- |
| `flow dev` | Fast iterative development       | < 5s     |
| `flow run` | Batch workloads, reproducibility | ~10 min |
| Python API | Programmatic submission          | ~10 min |

## Basic Usage

### Python API

```python
import flow
from flow import TaskConfig

# Simple GPU job - automatically uploads your local code
task = flow.run("python train.py", instance_type="a100")

# Wait for completion
task.wait()
print(task.logs())

# Full configuration
config = TaskConfig(
    name="distributed-training",
    instance_type="8xa100",  # 8x A100 GPUs
    command=["python", "-m", "torch.distributed.launch", 
             "--nproc_per_node=8", "train.py"],
    volumes=[{"size_gb": 100, "mount_path": "/data"}],
    max_price_per_hour=25.0,  # Cost protection
    max_run_time_hours=24.0   # Time limit
)
task = flow.run(config)

# Monitor execution
print(f"Status: {task.status}")
print(f"Shell: {task.shell_command}")
print(f"Cost: {task.cost_per_hour}")
```

### Code Upload

By default, Flow automatically uploads your current directory to the GPU instance:

```python
# This uploads your local files and runs them on GPU
task = flow.run("python train.py", instance_type="a100")

# Disable code upload (use pre-built Docker image)
task = flow.run(
    "python /app/train.py",
    instance_type="a100",
    image="mycompany/training:latest",
    upload_code=False
)
```

Use `.flowignore` file to exclude files from upload (same syntax as `.gitignore`).

### Handling Dependencies

Your code is uploaded, but dependencies need to be installed:

```python
# Install dependencies from pyproject.toml
task = flow.run(
    "pip install . && python train.py",
    instance_type="a100"
)

# Using uv (recommended for speed)
task = flow.run(
    "uv pip install . && python train.py",
    instance_type="a100"
)

# Pre-installed in Docker image (fastest)
task = flow.run(
    "python train.py",
    instance_type="a100",
    image="pytorch/pytorch:2.0.0-cuda11.8-cudnn8"  # PyTorch pre-installed
)

# Using private ECR images (auto-authenticates with AWS credentials)
task = flow.run(
    "python train.py",
    instance_type="a100",
    image="123456789.dkr.ecr.us-east-1.amazonaws.com/my-ml-image:latest",
    env={
        "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
        "AWS_SECRET_ACCESS_KEY": os.environ["AWS_SECRET_ACCESS_KEY"],
    }
)
```

### Command Line

```bash
# Quick interactive GPU instance
flow run --instance-type 8xh100            # Launch 8x H100 instance
flow run -i 8xa100                         # 8x A100 GPUs
flow run -i 4xa100                         # 4x A100 GPUs
flow run -i h100 --name dev-box           # Named single H100 instance

# Submit tasks from config
flow run config.yaml                       # From YAML file
flow run job.yaml --watch                  # Watch progress

# Monitor tasks
flow status                                # List all tasks
flow logs task-abc123 -f                   # Stream logs
flow ssh task-abc123                       # SSH access

# Manage tasks
flow cancel task-abc123                    # Stop execution
flow cancel --name-pattern "dev-*"         # Cancel all tasks starting with "dev-"
flow cancel -n "flow-dev-*" --yes          # Cancel matching tasks without confirmation
```

### YAML Configuration

```yaml
# config.yaml
name: model-training
instance_type: 4xa100
command: python train.py --epochs 100
env:
  BATCH_SIZE: "256"
  LEARNING_RATE: "0.001"
volumes:
  - size_gb: 500
    mount_path: /data
    name: training-data
max_price_per_hour: 20.0
max_run_time_hours: 72.0
ssh_keys:
  - my-ssh-key
```

## Development Environment

The `flow dev` command provides a persistent development environment with fast, container-based execution. It's perfect for iterative development where you want to:
- Start a VM once and use it all day
- Run commands in isolated containers
- Reset environments quickly without restarting the VM
- Avoid the overhead of VM provisioning for each run

### Quick Start

```bash
# Start or connect to your dev VM (defaults to 8xh100)
flow dev

# Run a command in a container
flow dev -c 'python train.py'

# Run interactive Python
flow dev -c python

# Use a specific Docker image
flow dev -c 'python test.py' --image pytorch/pytorch:latest

# Check dev environment status
flow dev --status

# Reset all containers (VM stays running)
flow dev --reset

# Stop the dev VM when done
flow dev --stop
```

### How It Works

1. **Persistent VM**: The first `flow dev` starts a VM that stays running
2. **Container Execution**: Each `flow dev -c` command runs in a fresh container
3. **Fast Iteration**: Containers start in seconds, not minutes
4. **Shared Workspace**: Your code is available at `/workspace` in all containers
5. **Automatic Cleanup**: Containers are removed after each command

### Uploading Code

Your dev VM needs access to your code. You have two options:

```bash
# Option 1: Auto-upload on VM creation (default)
flow dev  # Uploads current directory automatically

# Option 2: Manual upload later
flow dev --status  # Get your dev VM ID
flow upload-code <dev-vm-id>  # Upload code changes
```

### Examples

```bash
# Start dev environment with specific instance type
flow dev  # Defaults to 8xh100
flow dev -i a100  # Use A100 instead

# Run training in a container
flow dev -c 'python train.py --epochs 10'

# Run Jupyter notebook
flow dev -c 'jupyter notebook --ip=0.0.0.0 --no-browser'

# Install dependencies and run
flow dev -c 'pip install -r requirements.txt && python app.py'

# Use GPU in container and check stat
flow dev -c 'nvidia-smi'

# Run with custom environment
flow dev -c 'python script.py' --image custom/ml-env:latest
```

### Comparison with `flow run`

| Feature | `flow dev` | `flow run` |
|---------|------------|------------|
| VM Lifecycle | Persistent (stays running) | Per-task (terminated after) |
| Startup Time | Fast (containers) | Slower (VM provisioning) |
| Use Case | Development/iteration | Production/long runs |
| Cost | Pay for VM uptime | Pay per task |
| Environment | Containers on VM | Direct on VM |

## SLURM Users

Flow provides full compatibility with existing SLURM scripts while offering modern cloud-native features:

- **Direct script support**: `flow run job.slurm` automatically parses #SBATCH directives
- **Familiar commands**: `flow status` (squeue), `flow cancel` (scancel)
- **Interactive development**: `flow dev` replaces srun with fast container-based execution
- **Cost control**: Built-in price caps instead of account-based billing

[→ Full SLURM Migration Guide](docs/guides/slurm-migration.md)

## Instance Types

| Type | GPUs | Total Memory | Aliases |
|------|------|--------------|---------|
| `a100` | 1x A100 | 80GB | `1xa100` |
| `4xa100` | 4x A100 | 320GB | - |
| `8xa100` | 8x A100 | 640GB | - |
| `h100` | 1x H100 | 80GB | `1xh100` |
| `8xh100` | 8x H100 | 640GB | - |

```python
# Examples
flow.run("python train.py", instance_type="a100")     # Single GPU
flow.run("python train.py", instance_type="4xa100")   # Multi-GPU
flow.run("python train.py", instance_type="8xh100")   # Maximum performance
```

## Task Management

### Task Object

```python
# Get task handle
task = flow.run(config)
# Or retrieve existing
task = flow.get_task("task-abc123")

# Properties
task.task_id          # Unique identifier
task.status           # Current state
task.shell_command    # Shell connection string
task.cost_per_hour    # Current pricing
task.created_at       # Submission time

# Methods
task.wait(timeout=3600)       # Block until complete
task.refresh()                # Update status
task.cancel()                 # Terminate execution
```

### Logging

```python
# Get recent logs
logs = task.logs(tail=100)

# Stream in real-time
for line in task.logs(follow=True):
    if "loss:" in line:
        print(line)
```

### SSH Access

```python
# Interactive shell
task.shell()

# Run command
task.shell("nvidia-smi")
task.shell("tail -f /workspace/train.log")

# Multi-node access
task.shell(node=1)  # Connect to specific node
```

### Extended Information

```python
# Get task creator
user = task.get_user()
print(f"Created by: {user.username} ({user.email})")

# Get instance details
instances = task.get_instances()
for inst in instances:
    print(f"Node {inst.instance_id}:")
    print(f"  Public IP: {inst.public_ip}")
    print(f"  Private IP: {inst.private_ip}")
    print(f"  Status: {inst.status}")
```

## Persistent Storage

### Volume Management

```python
# Create volume (currently creates block storage)
with Flow() as client:
    vol = client.create_volume(size_gb=1000, name="datasets")

# Use in task
config = TaskConfig(
    name="training",
    instance_type="a100",
    command="python train.py",
    volumes=[{
        "volume_id": vol.volume_id,
        "mount_path": "/data"
    }]
)

# Or reference by name
config.volumes = [{
    "name": "datasets",
    "mount_path": "/data"
}]
```

### Dynamic Volume Mounting

Mount volumes to already running tasks without restart:

```bash
# CLI usage
flow mount <volume> <task>

# Examples
flow mount vol_abc123 task_xyz789      # By IDs
flow mount training-data gpu-job-1      # By names
flow mount :1 :2                        # By indices
```

```python
# Python API
flow.mount_volume("training-data", task.task_id)
# Volume available at /mnt/training-data immediately
```

**Multi-Instance Tasks**: 
- **Block volumes**: Cannot be mounted to multi-instance tasks (block storage limitation)
- **File shares**: Can be mounted to all instances simultaneously (when `interface="file"`)

**Note**: Flow SDK currently creates block storage volumes, which need to be formatted on first use. The underlying FCP platform also supports file shares (pre-formatted, multi-node accessible), but this is not yet exposed in the SDK.

### Docker Cache Optimization

Speed up container starts by caching Docker images:

```python
# Create a persistent cache volume
cache = flow.create_volume(size_gb=100, name="docker-cache")

# Use it in your tasks
task = flow.run(
    "python train.py",
    instance_type="a100",
    image="pytorch/pytorch:2.0.0-cuda11.8-cudnn8",
    volumes=[{
        "volume_id": cache.volume_id,
        "mount_path": "/var/lib/docker"
    }]
)
# First run: ~5 minutes (downloads image)
# Subsequent runs: ~30 seconds (uses cache)
```

## Zero-Import Remote Execution

Run existing Python functions on GPUs without modifying your code:

```python
from flow import invoke

# Execute any function from any file on GPU
result = invoke(
    "train.py",           # Your existing Python file
    "train_model",        # Function name  
    args=["s3://data"],   # Arguments
    gpu="a100"            # GPU type
)
```

Perfect for: existing codebases, Jupyter notebooks, and keeping ML code pure Python.

[→ Full Invoker Pattern Guide](docs/INVOKER_PATTERN.md)

## Decorator Pattern

Use Python decorators for serverless-style GPU functions:

```python
from flow import function

@function(gpu="a100")
def train_model(data_path: str, epochs: int = 100):
    # Your ML code here
    return {"accuracy": 0.95}

# Remote execution on GPU
result = train_model.remote("s3://data.csv", epochs=50)

# Local execution for testing
local_result = train_model("./local_data.csv")
```

[→ Full Decorator Pattern Guide](docs/guides/decorator-pattern.md)

## Data Mounting

Flow SDK provides seamless data access from S3 and volumes through the Flow client API:

### Quick Start

```python
# Mount S3 dataset
from flow import Flow

with Flow() as client:
    task = client.submit(
        "python train.py --data /data",
        gpu="a100",
        mounts="s3://my-bucket/datasets/imagenet"
    )

# Mount multiple sources
with Flow() as client:
    task = client.submit(
        "python train.py",
        gpu="a100:4",
        mounts={
            "/datasets": "s3://ml-bucket/imagenet",
            "/models": "volume://pretrained-models",  # Auto-creates if missing
            "/outputs": "volume://training-outputs"
        }
    )
```

### Supported Sources

- **S3**: Read-only access via s3fs (`s3://bucket/path`)
  - Requires AWS credentials in environment
  - Cached locally for performance
  
- **Volumes**: Persistent read-write storage (`volume://name`)
  - Auto-creates with 100GB if not found
  - High-performance NVMe storage

### Example: Training Pipeline

```python
# Set AWS credentials (from secure source)
import os
os.environ["AWS_ACCESS_KEY_ID"] = get_secret("aws_key")
os.environ["AWS_SECRET_ACCESS_KEY"] = get_secret("aws_secret")

# Submit training with data mounting
with Flow() as client:
    task = client.submit(
        """
        python train.py \\
            --data /datasets/train \\
            --validation /datasets/val \\
            --output /outputs
        """,
        gpu="a100:8",
        mounts={
            "/datasets": "s3://ml-datasets/imagenet",
            "/outputs": "volume://experiment-results"
        }
    )
```

See the [Data Mounting Guide](docs/DATA_MOUNTING_GUIDE.md) for detailed documentation.

## Distributed Training

### Single-Node Multi-GPU (Recommended)

```python
config = TaskConfig(
    name="distributed-training",
    instance_type="8xa100",  # 8x A100 GPUs on single node
    command="torchrun --nproc_per_node=8 --standalone train.py"
)
```

### Multi-Node Training

For multi-node training, explicitly set coordination environment variables:

```python
config = TaskConfig(
    name="multi-node-training",
    instance_type="8xa100",
    num_instances=4,  # 32 GPUs total
    env={
        "FLOW_NODE_RANK": "0",  # Set per node: 0, 1, 2, 3
        "FLOW_NUM_NODES": "4",
        "FLOW_MAIN_IP": "10.0.0.1"  # IP of rank 0 node
    },
    command=[
        "torchrun",
        "--nproc_per_node=8",
        "--nnodes=4",
        "--node_rank=$FLOW_NODE_RANK",
        "--master_addr=$FLOW_MAIN_IP",
        "--master_port=29500",
        "train.py"
    ]
)
```

## Advanced Features

### Cost Optimization

```python
# Use spot instances with price cap
config = TaskConfig(
    name="experiment",
    instance_type="a100",
    max_price_per_hour=5.0,  # Use spot if available
    max_run_time_hours=12.0  # Prevent runaway costs
)
```

### Environment Setup

```python
# Custom container
config.image = "pytorch/pytorch:2.0.0-cuda11.8-cudnn8"

# Environment variables
config.env = {
    "WANDB_API_KEY": "...",
    "HF_TOKEN": "...",
    "CUDA_VISIBLE_DEVICES": "0,1,2,3"
}

# Working directory
config.working_dir = "/workspace"
```

### Data Access

```python
# S3 integration
config = TaskConfig(
    name="s3-processing",
    instance_type="a100",
    command="python process.py",
    env={
        "AWS_ACCESS_KEY_ID": "...",
        "AWS_SECRET_ACCESS_KEY": "..."
    }
)

# Or use mounts parameter (simplified API)
with Flow() as client:
    task = client.submit(
        "python analyze.py",
        gpu="a100",
        mounts={
            "/input": "s3://my-bucket/data/",
            "/output": "volume://results"
        }
    )
```

## Error Handling

Flow provides structured errors with recovery guidance:

```python
from flow.errors import (
    FlowError,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
    QuotaExceededError
)

try:
    task = flow.run(config)
except ValidationError as e:
    print(f"Configuration error: {e.message}")
    for suggestion in e.suggestions:
        print(f"  - {suggestion}")
except QuotaExceededError as e:
    print(f"Quota exceeded: {e.message}")
    print("Suggestions:", e.suggestions)
except FlowError as e:
    print(f"Error: {e}")
```

## Common Patterns

### Interactive Development

#### Development Environment (flow dev)

The `flow dev` command provides the fastest way to iterate on GPU code:

```bash
# Start a persistent dev VM (defaults to 8xh100)
flow dev  # Creates 8xh100 instance
flow dev -i a100  # Or specify different type

# Iterate quickly with containers
flow dev -c 'python experiment.py --lr 0.01'
flow dev -c 'python experiment.py --lr 0.001'
flow dev -c 'python experiment.py --lr 0.0001'

# Each command runs in seconds, not minutes!
```

#### Google Colab Integration

Connect Google Colab notebooks to Flow GPU instances:

```bash
# Launch GPU instance configured for Colab
flow colab connect --instance-type a100 --hours 4

# You'll receive:
# 1. SSH tunnel command to run locally
# 2. Connection URL for Colab
```

Then in Google Colab:
1. Go to Runtime → Connect to local runtime
2. Paste the connection URL
3. Click Connect

Your Colab notebook now runs on Flow GPU infrastructure!

#### Direct Jupyter Notebooks

Run Jupyter directly on Flow instances:

```python
# Launch Jupyter server
config = TaskConfig(
    name="notebook",
    instance_type="a100",
    command="jupyter lab --ip=0.0.0.0 --no-browser",
    ports=[8888],
    max_run_time_hours=8.0
)
task = flow.run(config)
print(f"Access at: {task.endpoints['jupyter']}")
```

### Checkpointing

```python
# Resume training from checkpoint
config = TaskConfig(
    name="resume-training",
    instance_type="a100",
    command="python train.py --resume",
    volumes=[{
        "name": "checkpoints",
        "mount_path": "/checkpoints"
    }]
)
```

### Experiment Sweep

```python
# Run multiple experiments
for lr in [0.001, 0.01, 0.1]:
    config = TaskConfig(
        name=f"exp-lr-{lr}",
        instance_type="a100",
        command=f"python train.py --lr {lr}",
        env={"WANDB_RUN_NAME": f"lr_{lr}"}
    )
    flow.run(config)
```

## Architecture

Flow SDK follows Domain-Driven Design with clear boundaries:

### High-Level Overview

```
┌─────────────────────────────────────────────┐
│          User Interface Layer               │
│        (Python API, CLI, YAML)              │
├─────────────────────────────────────────────┤
│           Core Domain Layer                 │
│     (TaskConfig, Task, Volume models)       │
├─────────────────────────────────────────────┤
│        Provider Abstraction Layer           │
│         (IProvider Protocol)                │
├─────────────────────────────────────────────┤
│        Provider Implementations             │
│     (FCP, AWS, GCP, Azure - future)         │
└─────────────────────────────────────────────┘
```

### Key Components

- **Flow SDK** (`src/flow/`): High-level Python SDK for ML/AI workloads
- **Mithril CLI** (`mithril/`): Low-level IaaS control following Unix philosophy
- **Provider Abstraction**: Cloud-agnostic interface for multi-cloud support

### Current Provider Support

**FCP (ML Foundry)** - Production Ready
- Ubuntu 22.04 environment with bash
- 10KB startup script limit
- Spot instances with preemption handling
- Block storage volumes (file shares available in some regions)
- See [FCP provider documentation](src/flow/providers/fcp/README.md) for implementation details

**AWS, GCP, Azure** - Planned
- Provider abstraction designed for multi-cloud
- Contributions welcome

### Additional Documentation

- [Architecture Overview](docs/ARCHITECTURE.md) - System design and concepts
- [FCP Provider Details](src/flow/providers/fcp/README.md) - Provider-specific implementation
- [Colab Troubleshooting](docs/COLAB_TROUBLESHOOTING.md) - Colab setup guide
- [Configuration Guide](docs/CONFIGURATION.md) - Configuration options
- [Data Handling](docs/DATA_HANDLING.md) - Data management patterns

### Example Code

- [Verify Instance Setup](examples/01_verify_instance.py) - Basic GPU verification
- [Jupyter Server](examples/02_jupyter_server.py) - Launch Jupyter on GPU
- [Multi-Node Training](examples/03_multi_node_training.py) - Distributed training setup
- [S3 Data Access](examples/04_s3_data_access.py) - Cloud storage integration
- [More Examples](examples/) - Additional usage patterns

## Advanced Features

* **Spot Pricing**: `max_price_per_hour` controls cost.
* **Docker Integration**: Prebuilt images or dynamic dependency installation.
* **SLURM Compatibility**: Transparent SLURM script migration.

## Get Started

Visit our [documentation](https://github.com/foundrytechnologies/flow-v2) or join the [Discord community](https://discord.gg/flow-sdk).

---

Flow SDK: Simplify ML development, accelerate innovation.
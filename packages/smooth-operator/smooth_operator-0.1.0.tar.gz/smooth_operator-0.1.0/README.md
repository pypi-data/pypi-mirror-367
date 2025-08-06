# Smooth Operator

A CLI client for managing Drupal sites across multiple operation channels (Pantheon, Lando).

## Description

Smooth Operator is a powerful CLI tool designed to simplify the management of Drupal sites hosted on Pantheon. It provides a unified interface for working with multiple operational channels (Lando, Drush, Terminus, GitLab) and supports both individual and bulk site operations.

The tool is built with modern Python (3.8+) and leverages asynchronous programming for efficient operation, especially when managing multiple sites simultaneously.

## Key Features

- **Site Management**: Clone, list, and manage Pantheon sites
- **Extension Inventory**: Analyze and catalog site extensions
- **Upstream Updates**: Apply complex, manifest-driven update workflows to multiple sites
- **Batch Processing**: Efficiently process large numbers of sites with configurable batching
- **Parallel Execution**: Run operations concurrently for improved performance
- **Structured Logging**: Comprehensive logging with structured data for better troubleshooting
- **Rich Terminal Output**: Human-friendly terminal output with color and formatting

## Architecture

Smooth Operator is built around several core components:

1. **Channels**: Abstractions for interacting with external systems (Terminus, Lando)
2. **Commands**: CLI commands organized by domain (site, extension, upstream)
3. **Operations**: Core business logic components for specific operational tasks
4. **Executor**: Task execution engine with dependency management
5. **Utilities**: Shared functionality for logging, filtering, async operations, etc.

The system uses a task-based approach for complex operations, with tasks organized in a dependency graph for proper execution order.

## Technologies Used

- **Click/Typer**: Modern Python CLI framework with strong typing support
- **Rich**: Terminal formatting library for creating beautiful CLI output
- **StructLog**: Structured logging library for comprehensive, machine-parseable logs
- **Pydantic**: Data validation and settings management using Python type annotations
- **Asyncio**: Python's built-in asynchronous I/O framework for concurrent operations
- **HTTPX**: Modern, async-capable HTTP client for API interactions
- **JSONPickle**: Advanced JSON serialization for complex Python objects
- **PyYAML**: YAML parser for configuration files

## Installation Options

### PyPI Installation (Recommended)

The simplest way to install Smooth Operator:

```bash
# Install from PyPI
pip install smooth-operator

# Verify installation
smooth-operator --version
```

### Docker Installation

If you prefer using Docker:

```bash
# Pull the Docker image
docker pull yourusername/smooth-operator:latest

# Run Smooth Operator commands
docker run -it yourusername/smooth-operator:latest [command]

# Using with local files (mount volumes)
docker run -it -v $(pwd):/workspace -w /workspace yourusername/smooth-operator:latest [command]
```

### Development Installation

For contributors or local development:

```bash
# Clone the repository
git clone https://github.com/yourusername/smooth-operator.git
cd smooth-operator

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Standalone Executable (Linux)

For users who prefer a standalone executable without Python dependencies:

```bash
# Download the executable
wget https://github.com/yourusername/smooth-operator/releases/latest/download/smooth-operator-linux

# Make it executable
chmod +x smooth-operator-linux

# Move to a directory in your PATH (optional)
sudo mv smooth-operator-linux /usr/local/bin/smooth-operator
```

## Terminus Configuration

Smooth Operator can work with Terminus in two ways:

### Option 1: Using Lando (Default)

```bash
# Start Lando
lando start

# Authenticate with Terminus
lando terminus auth:login --machine-token=YOUR_PANTHEON_MACHINE_TOKEN
```

### Option 2: Using External Terminus

If you have Terminus installed directly on your system:

1. Create a configuration file at `~/.smooth_operator/config.yml`:

```yaml
terminus:
  terminus_path: "/path/to/your/terminus"
  use_lando: false

logging:
  level: INFO
  file: smooth_operator.log

parallel:
  default: false
  max_workers: 5
```

## Configuration

Create a `.smooth_operator.yml` file in your home directory or project directory:

```yaml
terminus:
  binary: terminus

lando:
  sites_path: ~/pantheon

gitlab:
  api_url: https://gitlab.example.com/api/v4
  token: YOUR_GITLAB_TOKEN

logging:
  level: INFO
  file: smooth_operator.log

parallel:
  default: false
  max_workers: 5
```

## Usage

### Basic Commands

```bash
# List all sites
smooth-operator site list

# Clone a site
smooth-operator site clone source-site target-site --source-env=live --target-env=dev

# Get extension inventory
smooth-operator extension inventory --site=example-site
```

### Upstream Updates

The upstream updater is a powerful feature that allows you to define and execute complex update processes across multiple sites using JSON manifests:

```bash
# Run upstream updates on specific sites
smooth-operator upstream update manifest.json --site=example-site

# Run updates with batching for many sites
smooth-operator upstream update manifest.json --batch --batch-size=5 --wait=60

# Run updates in parallel for faster processing
smooth-operator upstream update manifest.json --parallel --max-workers=3

# Filter sites by tag
smooth-operator upstream update manifest.json --tag=client-a --tag=production
```

See the [Upstream Updater documentation](smooth_operator/operations/updater/README.md) for detailed information on creating manifests and available options.

## License

Proprietary

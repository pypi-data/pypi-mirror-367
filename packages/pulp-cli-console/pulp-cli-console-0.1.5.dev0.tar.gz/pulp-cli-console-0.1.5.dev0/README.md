# Pulp CLI Console

A command-line interface for Pulp, providing console administrative functionality.

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Basic Configuration](#basic-configuration)
  - [Advanced Options](#advanced-options)
  - [Environment Variables](#environment-variables)
- [Usage](#usage)
  - [Task Management](#task-management)
  - [Vulnerability Management](#vulnerability-management)
  - [Performance Monitoring](#performance-monitoring)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debug Mode](#debug-mode)
  - [Logs](#logs)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Pulp CLI Console provides a set of commands to manage Pulp resources from the command line. It extends the base Pulp CLI functionality with console-specific administrative tools for system operators and administrators.

The console offers capabilities for task management, vulnerability scanning, system monitoring, and more, all through a unified command-line interface.

## Requirements

- Python 3.8 or higher
- Access to a Pulp 3.x server
- Network connectivity to your Pulp server
- Appropriate user permissions on the Pulp server

## Installation

You can install the Pulp CLI Console using pip:

```bash
pip install pulp-cli-console
```

For development or the latest features, you can install directly from the repository:

```bash
pip install git+https://github.com/pulp/pulp-cli-console.git
```

## Configuration

### Basic Configuration

The Pulp CLI Console requires configuration to connect to your Pulp server. Create a configuration file at `~/.config/pulp/cli.toml`:

```toml
[cli]
base_url = "https://pulp.example.com"
verify_ssl = true
format = "json"
timeout = 30
username = "admin"
password = "password"  # Consider using environment variables instead
```

### Advanced Options

You can customize various aspects of the CLI behavior:

```toml
[cli]
base_url = "https://pulp.example.com"
verify_ssl = true
cert = "/path/to/client/cert.pem"  # Optional client certificate
key = "/path/to/client/key.pem"    # Optional client key
ca_cert = "/path/to/ca/cert.pem"   # Custom CA certificate
format = "json"                    # Output format: json, yaml, or none
timeout = 60                       # Request timeout in seconds
limit = 100                        # Default pagination limit
interactive = true                 # Enable interactive prompts
quiet = false                      # Suppress non-error output
verbose = 0                        # Verbosity level (0-3)
# Use one of the following authentication methods
username = "admin"
password = "password"
token = "your-api-token"           # API token authentication
refresh_token = "refresh-token"    # For OAuth2 refresh token flow
```

### Environment Variables

You can also use environment variables for configuration, which is recommended for sensitive information:

```bash
# Base configuration
export PULP_BASE_URL="https://pulp.example.com"
export PULP_VERIFY_SSL="true"

# Authentication
export PULP_USERNAME="admin"
export PULP_PASSWORD="password"

# Alternative authentication
export PULP_TOKEN="your-api-token"
```

## Usage

### Task Management

The CLI provides commands for managing administrative tasks:

```bash
# List all tasks
pulp console task list

# Filter tasks by state
pulp console task list --state=completed

# List tasks with pagination
pulp console task list --limit=10 --offset=20

# Filter tasks by name
pulp console task list --name="sync" --name-contains="content"

# Filter tasks by time
pulp console task list --started-at-gte="2023-01-01T00:00:00Z"

# Show detailed information for a specific task
pulp console task show --href=/pulp/api/v3/tasks/1234abcd/

# Cancel a running task
pulp console task cancel --href=/pulp/api/v3/tasks/1234abcd/
```

#### Available Filters for Tasks

- `--limit`: Limit the number of tasks shown
- `--offset`: Skip a number of tasks
- `--name`: Filter by task name
- `--name-contains`: Filter tasks containing this name
- `--logging-cid-contains`: Filter by logging correlation ID
- `--state`: Filter by task state
- `--state-in`: Filter by multiple states (comma-separated)
- `--task-group`: Filter by task group
- `--parent-task`: Filter by parent task
- `--worker`: Filter by worker
- `--created-resources`: Filter by created resources
- `--started-at-gte/--started-at-lte`: Filter by start time
- `--finished-at-gte/--finished-at-lte`: Filter by finish time
- `--reserved-resource/--reserved-resource-in`: Filter by reserved resources
- `--exclusive-resource/--exclusive-resource-in`: Filter by exclusive resources
- `--shared-resource/--shared-resource-in`: Filter by shared resources

### Vulnerability Management

The CLI provides commands for managing vulnerability reports:

```bash
# List vulnerability reports
pulp console vulnerability list

# Show a specific vulnerability report
pulp console vulnerability show --href=/api/pulp/vulnerability-reports/123/

# Create a vulnerability report
pulp console vulnerability create --file=/path/to/packages.json
```

#### Vulnerability Commands

- `list`: List all vulnerability reports
- `show`: Display details of a specific vulnerability report
- `create`: Create a new vulnerability report from a JSON file

#### Options for Vulnerability Commands

- `--href`: Reference to a specific vulnerability report (for show command)
- `--file`: JSON file containing npm packages (required for create command)
- `--chunk-size`: Size of chunks for uploading files (for create command)
- `--severity`: Filter by vulnerability severity (critical, high, medium, low)
- `--status`: Filter by status (open, in-progress, resolved, false-positive)

### Performance Monitoring

```bash
# Get system performance metrics
pulp console monitor performance

# View resource utilization
pulp console monitor resources

# Check Pulp server health
pulp console monitor health
```

## Troubleshooting

### Common Issues

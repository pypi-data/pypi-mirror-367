# Luminaut

Casting light on shadow cloud deployments. Detect exposure of resources deployed in AWS.

![Luminaut Picture](https://raw.githubusercontent.com/luminaut-org/luminaut/refs/heads/main/.github/images/luminaut_readme_300.png)

![Under Development](https://img.shields.io/badge/Status-Under%20Development-orange)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fluminaut-org%2Fluminaut%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
[![Test](https://github.com/luminaut-org/luminaut/actions/workflows/test.yml/badge.svg)](https://github.com/luminaut-org/luminaut/actions/workflows/test.yml)
[![Build artifacts](https://github.com/luminaut-org/luminaut/actions/workflows/build.yml/badge.svg)](https://github.com/luminaut-org/luminaut/actions/workflows/build.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=luminaut-org_luminaut&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=luminaut-org_luminaut)
![PyPI - Downloads](https://img.shields.io/pypi/dm/luminaut)
![PyPI - Version](https://img.shields.io/pypi/v/luminaut)
![GitHub License](https://img.shields.io/github/license/luminaut-org/luminaut)

## Introduction

Luminaut is a utility to scope cloud environment exposure for triage. The goal is to quickly identify exposed resources and collect information to start an investigation.

Starting from the public IP addresses of AWS Elastic Network Interfaces (ENIs) and GCP Compute Engine instances, plus public URIs of GCP Cloud Run services, Luminaut gathers information about the associated resources, security configurations, and related events. The framework includes active scanning tools like nmap and whatweb, to identify services running on exposed ports, and passive sources like Shodan.

By combining cloud configuration data with external sources, Luminaut provides context to guide the next steps of an investigation.

Luminaut supports both AWS and GCP environments, with modular architecture allowing for the addition of new cloud providers, tools, and services as needed.

![Luminaut execution](https://raw.githubusercontent.com/luminaut-org/luminaut/refs/heads/main/.github/images/luminaut_execution.png)
![Luminaut result - IP address 1](https://raw.githubusercontent.com/luminaut-org/luminaut/refs/heads/main/.github/images/luminaut_result_ip_1.png)
![Luminaut result - IP address 2](https://raw.githubusercontent.com/luminaut-org/luminaut/refs/heads/main/.github/images/luminaut_result_ip_2.png)

## Features

### AWS

- Enumerate ENIs with public IPs.
- Gather information about associated EC2 instances and Elastic load balancers.
- Identify permissive rules for attached security groups.
- Scan CloudTrail history for related events to answer who, what, and when.
  - Supports querying for activity related to discovered ENI, EC2, ELB, and Security Group resources.
  - Optionally specify a time frame to limit the scan to a specific time period.
- Query AWS Config for resource configuration changes over time.
  - Supports scanning AWS Config history for the discovered ENI and EC2 Instance associated with the ENI.
  - Optionally specify a time frame to limit the scan to a specific time period.
- Skip scanning and reporting on resources based on the resource id or tag values
  - Supports skipping based on the resource id of the ENI.

### GCP

- Enumerate Compute Engine instances with public IPs.
- Enumerate Cloud Run services with public URIs.
- Identify permissive firewall rules that allow external access to instances.
- Query GCP audit logs for instance and service lifecycle events to answer who, what, and when.
  - Supports querying for activity related to discovered Compute Engine instances and Cloud Run services.
  - Optionally specify a time frame to limit the scan to a specific time period.

### Active scanning

- [nmap](https://nmap.org/) to scan common ports and services against identified IP addresses.
  - nmap will only scan ports associated with permissive security group rules or a load balancer listener.
- [whatweb](https://github.com/urbanadventurer/WhatWeb) to identify services running on ports associated with exposed security group ports.
  - whatweb will only scan ports associated with permissive security group rules or a load balancer listener.

### Passive sources

- [shodan](https://www.shodan.io/) to gather information about exposed services and vulnerabilities.

### Reporting

- Console output with rich formatting, displaying key information.
- HTML capture of console output to preserve prior executions.
- CSV Timeline of events from CloudTrail, GCP audit logs, and other sources.
- JSON lines output with full event information for parsing and integration with other tools.

## Installation

Luminaut is available on PyPI and can be installed with pip:

```bash
pip install luminaut
```

There is also a docker image available on GitHub, you can pull it locally by running: 

```bash
docker pull ghcr.io/luminaut-org/luminaut
```

Additional installation information is available within the [Luminaut documentation](https://luminaut-org.github.io/luminaut/installation.html)

## Usage

Luminaut requires access to cloud providers with appropriate credentials and permissions. Configure your system with the necessary credentials for the cloud providers you want to scan:

- **AWS**: Configure AWS credentials using the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).
- **GCP**: Configure GCP credentials using the [gcloud CLI](https://cloud.google.com/sdk/docs/initializing).

See the [Configuration documentation](https://luminaut-org.github.io/luminaut/configuration.html) for required cloud provider permissions.

No arguments are required to run luminaut. The default is to look for a `luminaut.toml` file in the same directory
and run available tools to start detecting resources.

The default configuration options are shown in the [Configuration](#configuration) section.

Luminaut help is available with the argument `--help`.

```bash
$ luminaut --help                       
usage: luminaut [-h] [--config CONFIG] [--log LOG] [--verbose]

Luminaut: Casting light on shadow cloud deployments. 

options:
  -h, --help       show this help message and exit
  --config CONFIG  Configuration file. (default: luminaut.toml)
  --log LOG        Log file. (default: luminaut.log)
  --verbose        Verbose output in the log file. (default: False)
```

See more usage information and examples in the [Luminaut documentation](https://luminaut-org.github.io/luminaut/usage.html)

## Configuration

See the [documentation on Luminaut configuration](https://luminaut-org.github.io/luminaut/configuration.html)

## Examples

See `examples/` for scripts that demonstrate the usage of Luminaut as a Python package.

## Contributing

If you would like to contribute to Luminaut, please follow the guidelines in the [CONTRIBUTING.md](.github/CONTRIBUTING.md) file.

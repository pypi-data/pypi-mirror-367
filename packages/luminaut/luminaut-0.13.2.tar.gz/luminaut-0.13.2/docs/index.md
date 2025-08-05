---
title: Luminaut Documentation
layout: splash
header:
  overlay_color: "#555"
excerpt: "Casting light on shadow cloud deployments."
---

![Luminaut Picture](https://raw.githubusercontent.com/luminaut-org/luminaut/refs/heads/main/.github/images/luminaut_readme_300.png)

Luminaut is a utility to scope cloud environment exposure for triage. The goal is to quickly identify exposed resources and collect information to start an investigation.

Starting from the public IP addresses of AWS Elastic Network Interfaces (ENIs), Luminaut gathers information about the associated EC2 instances, load balancers, security groups, and related events. The framework also includes active scanning tools like nmap and whatweb, to identify services running on exposed ports, and passive sources like Shodan. Luminaut also supports Google Cloud Platform compute instances and Cloud Run services, allowing it to gather information about exposed resources in GCP environments.

By combining cloud configuration data with external sources, Luminaut provides context to guide the next steps of an investigation.

While supporting AWS and GCP, Luminaut can be extended to support other cloud providers and services. The framework is designed to be modular, allowing for the addition of new tools and services as needed.

![Luminaut execution](https://raw.githubusercontent.com/luminaut-org/luminaut/refs/heads/main/.github/images/luminaut_execution.png)
![Luminaut result - IP address 1](https://raw.githubusercontent.com/luminaut-org/luminaut/refs/heads/main/.github/images/luminaut_result_ip_1.png)
![Luminaut result - IP address 2](https://raw.githubusercontent.com/luminaut-org/luminaut/refs/heads/main/.github/images/luminaut_result_ip_2.png)

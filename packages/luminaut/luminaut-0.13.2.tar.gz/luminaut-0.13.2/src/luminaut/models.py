import json
import textwrap
import tomllib
from collections.abc import Iterable, Mapping, MutableSequence
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum, auto
from ipaddress import IPv4Address, IPv6Address, ip_address
from pathlib import Path
from typing import Any, BinaryIO, ClassVar, Self, TypeVar
from typing import Protocol as TypingProtocol
from urllib.parse import urlparse

from google.cloud.compute_v1 import types as gcp_compute_v1_types
from google.cloud.run_v2 import types as gcp_run_v2_types
from rich.emoji import Emoji

T = TypeVar("T")
IPAddress = IPv4Address | IPv6Address
QUAD_ZERO_ADDRESSES = (IPv4Address("0.0.0.0"), IPv6Address("::"))  # noqa: S104


def convert_tag_set_to_dict(tag_set: Iterable[dict[str, str]]) -> dict[str, str]:
    tags = {}
    for tag in tag_set:
        if (key := tag.get("key")) and (value := tag.get("value")):
            tags[key] = value
    return tags


class IsDataclass(TypingProtocol):
    # From: https://github.com/microsoft/pyright/issues/629
    # checking for this attribute seems to currently be
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: ClassVar[dict]


@dataclass
class ConfigDiff:
    added: dict[str, Any] = field(default_factory=dict)
    removed: dict[str, Any] = field(default_factory=dict)
    changed: dict[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return any([self.added, self.removed, self.changed])


def generate_config_diff(
    first: IsDataclass | dict[str, Any], second: IsDataclass | dict[str, Any]
) -> ConfigDiff:
    diff = ConfigDiff()

    if hasattr(first, "__dataclass_fields__"):
        first = asdict(first)  # type: ignore
    elif not isinstance(first, dict):
        raise ValueError(
            f"First argument must be a dataclass or dict, not {type(first)}"
        )
    if hasattr(second, "__dataclass_fields__"):
        second = asdict(second)  # type: ignore
    elif not isinstance(second, dict):
        raise ValueError(
            f"Second argument must be a dataclass or dict, not {type(second)}"
        )

    first_keys = set(first.keys())
    second_keys = set(second.keys())
    common_keys = first_keys & second_keys

    diff.added = {key: second[key] for key in second_keys - common_keys}
    diff.removed = {key: first[key] for key in first_keys - common_keys}
    diff.changed = {
        key: {"old": first[key], "new": second[key]}
        for key in common_keys
        if first[key] != second[key]
    }

    return diff


class Direction(StrEnum):
    INGRESS = auto()
    EGRESS = auto()


class FirewallAction(StrEnum):
    ALLOW = auto()
    DENY = auto()


class Protocol(StrEnum):
    TCP = auto()
    UDP = auto()
    ICMP = auto()
    ICMPv6 = auto()
    ALL = "-1"


class ResourceType(StrEnum):
    EC2_Instance = "AWS::EC2::Instance"
    EC2_NetworkInterface = "AWS::EC2::NetworkInterface"
    EC2_SecurityGroup = "AWS::EC2::SecurityGroup"
    ELB_LoadBalancer = "AWS::ElasticLoadBalancingV2::LoadBalancer"
    GCP_Instance = "GCP::Compute::Instance"
    GCP_Service = "GCP::Run::Service"
    GCP_Task = "GCP::Run::Task"
    GCP_Firewall = "GCP::Compute::Firewall"
    GCP_Firewall_Rule = "GCP::Compute::FirewallRule"
    Hostname = "Hostname"


class SecurityGroupRuleTargetType(StrEnum):
    CIDR = auto()
    SECURITY_GROUP = auto()
    PREFIX_LIST = auto()


@dataclass
class LuminautConfigTool:
    enabled: bool = True
    timeout: int | None = None

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> Self:
        return cls(
            enabled=config.get("enabled", True),
            timeout=config.get("timeout"),
        )


@dataclass
class LuminautConfigToolShodan(LuminautConfigTool):
    api_key: str | None = None

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> Self:
        shodan_config = super().from_dict(config)
        shodan_config.api_key = config.get("api_key")
        return shodan_config


@dataclass
class LuminautConfigAwsAllowedResource:
    type: ResourceType | None = None
    id: str | None = None
    tags: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        if resource_type := data.get("type"):
            resource_type = ResourceType(resource_type)

        return cls(
            type=resource_type,
            id=data.get("id"),
            tags=data.get("tags", {}),
        )


@dataclass
class LuminautConfigtoolAwsEvents(LuminautConfigTool):
    start_time: datetime | None = None
    end_time: datetime | None = None

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> Self:
        aws_events_config = super().from_dict(config)
        if start_time := config.get("start_time"):
            aws_events_config.start_time = start_time
        if end_time := config.get("end_time"):
            aws_events_config.end_time = end_time
        return aws_events_config


@dataclass
class LuminautConfigToolAws(LuminautConfigTool):
    aws_profile: str | None = None
    aws_regions: list[str] | None = field(default_factory=list)
    config: LuminautConfigtoolAwsEvents = field(
        default_factory=lambda: LuminautConfigtoolAwsEvents(enabled=True)
    )
    cloudtrail: LuminautConfigtoolAwsEvents = field(
        default_factory=lambda: LuminautConfigtoolAwsEvents(enabled=True)
    )
    allowed_resources: list[LuminautConfigAwsAllowedResource] = field(
        default_factory=list
    )

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> Self:
        aws_config = super().from_dict(config)

        aws_config.aws_profile = config.get("aws_profile")

        # Don't override defaults
        if aws_regions := config.get("aws_regions"):
            aws_config.aws_regions = aws_regions
        if config_dict := config.get("config"):
            aws_config.config = LuminautConfigtoolAwsEvents.from_dict(config_dict)
        if cloudtrail_dict := config.get("cloudtrail"):
            aws_config.cloudtrail = LuminautConfigtoolAwsEvents.from_dict(
                cloudtrail_dict
            )

        aws_config.allowed_resources = [
            LuminautConfigAwsAllowedResource.from_dict(x)
            for x in config.get("allowed_resources", [])
        ]

        return aws_config


@dataclass
class LuminautConfigToolGcpAuditLogs(LuminautConfigTool):
    start_time: datetime | None = None
    end_time: datetime | None = None

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> Self:
        audit_logs_config = super().from_dict(config)
        if start_time := config.get("start_time"):
            # Parse ISO format datetime string to datetime object
            if isinstance(start_time, str):
                audit_logs_config.start_time = datetime.fromisoformat(
                    start_time.replace("Z", "+00:00")
                )
            else:
                audit_logs_config.start_time = start_time
        if end_time := config.get("end_time"):
            # Parse ISO format datetime string to datetime object
            if isinstance(end_time, str):
                audit_logs_config.end_time = datetime.fromisoformat(
                    end_time.replace("Z", "+00:00")
                )
            else:
                audit_logs_config.end_time = end_time
        return audit_logs_config


@dataclass
class LuminautConfigToolGcp(LuminautConfigTool):
    projects: list[str] = field(default_factory=list)
    regions: list[str] = field(default_factory=list)
    compute_zones: list[str] = field(default_factory=list)
    audit_logs: LuminautConfigToolGcpAuditLogs = field(
        default_factory=lambda: LuminautConfigToolGcpAuditLogs(enabled=True)
    )

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> Self:
        gcp_config = super().from_dict(config)
        gcp_config.projects = config.get("projects", [])
        gcp_config.regions = config.get("regions", [])
        gcp_config.compute_zones = config.get("compute_zones", [])
        if audit_logs_dict := config.get("audit_logs"):
            gcp_config.audit_logs = LuminautConfigToolGcpAuditLogs.from_dict(
                audit_logs_dict
            )
        return gcp_config


@dataclass
class LuminautConfigReport:
    console: bool = True
    json: bool = False
    json_file: Path | None = None
    html: bool = False
    html_file: Path | None = None
    timeline: bool = False
    timeline_file: Path | None = None

    @classmethod
    def from_toml(cls, config: dict[str, Any]) -> Self:
        def path_or_none(value: str | None) -> Path | None:
            return Path(value) if value else None

        json_file_path = path_or_none(config.get("json_file"))
        html_file_path = path_or_none(config.get("html_file"))
        timeline_file_path = path_or_none(config.get("timeline_file"))

        return cls(
            console=config.get("console", True),
            json=config.get("json", False),
            json_file=json_file_path,
            html=config.get("html", False),
            html_file=html_file_path,
            timeline=config.get("timeline", False),
            timeline_file=timeline_file_path,
        )


@dataclass
class LuminautConfig:
    report: LuminautConfigReport = field(default_factory=LuminautConfigReport)
    aws: LuminautConfigToolAws = field(default_factory=LuminautConfigToolAws)
    gcp: LuminautConfigToolGcp = field(default_factory=LuminautConfigToolGcp)
    nmap: LuminautConfigTool = field(default_factory=LuminautConfigTool)
    shodan: LuminautConfigToolShodan = field(default_factory=LuminautConfigToolShodan)
    whatweb: LuminautConfigTool = field(default_factory=LuminautConfigTool)

    @classmethod
    def from_toml(cls, toml_file: BinaryIO) -> Self:
        toml_data = tomllib.load(toml_file)

        luminaut_config = cls(
            report=LuminautConfigReport.from_toml(toml_data.get("report", {}))
        )

        if tool_config := toml_data.get("tool"):
            luminaut_config.aws = LuminautConfigToolAws.from_dict(
                tool_config.get("aws", {})
            )
            luminaut_config.gcp = LuminautConfigToolGcp.from_dict(
                tool_config.get("gcp", {})
            )
            luminaut_config.nmap = LuminautConfigTool.from_dict(
                tool_config.get("nmap", {})
            )
            luminaut_config.shodan = LuminautConfigToolShodan.from_dict(
                tool_config.get("shodan", {})
            )
            luminaut_config.whatweb = LuminautConfigTool.from_dict(
                tool_config.get("whatweb", {})
            )
        return luminaut_config


@dataclass
class GcpNetworkInterface:
    resource_id: str
    public_ip: str | None = None
    network: str | None = None
    network_attachment: str | None = None
    internal_ip: str | None = None
    alias_ip_ranges: list[str] = field(default_factory=list)

    @classmethod
    def from_gcp(cls, network_interface: gcp_compute_v1_types.NetworkInterface) -> Self:
        public_ip = None
        if len(network_interface.access_configs) > 0:
            access_config = network_interface.access_configs[0]
            if not access_config.nat_i_p:
                raise ValueError(
                    f"Instance {network_interface.name} has no public IP in access config."
                )
            public_ip = access_config.nat_i_p

        return cls(
            public_ip=public_ip,
            resource_id=network_interface.name,
            internal_ip=network_interface.network_i_p,
            network=network_interface.network,
            network_attachment=network_interface.network_attachment,
            alias_ip_ranges=[
                alias_range.ip_cidr_range
                for alias_range in network_interface.alias_ip_ranges
            ],
        )

    def get_project_name(self) -> str | None:
        """Extract project name from network URL."""
        if not self.network:
            return None

        # Network format: https://www.googleapis.com/compute/v1/projects/{project}/global/networks/{network}
        network_parts = self.network.split("/")
        num_network_parts = 7
        if len(network_parts) >= num_network_parts and network_parts[5] == "projects":
            return network_parts[6]
        return None

    def get_network_name(self) -> str | None:
        """Extract network name from network URL."""
        if not self.network:
            return None

        # Network format: https://www.googleapis.com/compute/v1/projects/{project}/global/networks/{network}
        network_parts = self.network.split("/")
        num_network_identifier_parts = 10
        if (
            len(network_parts) >= num_network_identifier_parts
            and network_parts[8] == "networks"
        ):
            return network_parts[9]
        return None

    def build_rich_text(self) -> str:
        rich_text = f"Public IP: [dark_orange3]{self.public_ip}[/dark_orange3] Private IP: [orange3]{self.internal_ip}[/orange3] from [cyan]{self.resource_id}[/cyan]\n"
        if self.alias_ip_ranges:
            rich_text += f"  Alias ranges: [dark_orange3]{', '.join(self.alias_ip_ranges)}[/dark_orange3]\n"
        return rich_text


@dataclass
class GcpInstance:
    resource_id: str
    name: str
    network_interfaces: list[GcpNetworkInterface] = field(default_factory=list)
    creation_time: datetime | None = None
    zone: str | None = None
    status: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    resource_type: ResourceType = ResourceType.GCP_Instance

    def get_public_ips(self) -> list[str]:
        """Return a list of public IPs from the network interfaces."""
        return [nic.public_ip for nic in self.network_interfaces if nic.public_ip]

    def has_public_ip(self) -> bool:
        return bool(self.get_public_ips())

    def get_networks(self) -> list[str]:
        """Return a list of distinct network names from all network interfaces."""
        networks = set()
        for nic in self.network_interfaces:
            if network_name := nic.get_network_name():
                networks.add(network_name)
        return list(networks)

    def build_rich_text(self) -> str:
        rich_text = f"[dark_orange3]{self.name}[/dark_orange3] Id: {self.resource_id} ([green]{self.status}[/green]) Created: {self.creation_time or 'Unknown'}\n"
        if description := self.description:
            rich_text += f"  Description: {description}\n"
        for nic in self.network_interfaces:
            # Indent each network interface line
            rich_text += (
                "\n".join(["  " + line for line in nic.build_rich_text().splitlines()])
                + "\n"
            )
        return rich_text

    @classmethod
    def from_gcp(cls, instance: gcp_compute_v1_types.Instance) -> Self:
        return cls(
            resource_id=str(instance.id),
            name=instance.name,
            network_interfaces=[
                GcpNetworkInterface.from_gcp(nic) for nic in instance.network_interfaces
            ],
            creation_time=datetime.fromisoformat(instance.creation_timestamp),
            zone=instance.zone.split("/")[-1],
            status=instance.status,
            description=instance.description,
            tags=list(instance.tags.items)
            if hasattr(instance, "tags") and instance.tags.items
            else [],
        )


@dataclass
class GcpFirewallRule:
    resource_id: str
    name: str
    direction: Direction
    priority: int
    action: FirewallAction
    source_ranges: list[str] = field(default_factory=list)
    allowed_protocols: list[dict[str, Any]] = field(
        default_factory=list
    )  # protocol and ports
    creation_timestamp: datetime | None = None
    disabled: bool = False
    target_tags: list[str] = field(default_factory=list)

    def build_rich_text(self) -> str:
        """Build rich text representation of the firewall rule."""
        # Format source ranges - show first few if many
        if self.source_ranges:
            max_to_show = 3
            if len(self.source_ranges) <= max_to_show:
                sources = ", ".join(self.source_ranges)
            else:
                sources = f"{', '.join(self.source_ranges[:max_to_show])} (+{len(self.source_ranges) - max_to_show} more)"
            source_text = f"[green]{sources}[/green]"
        else:
            source_text = "[green]Any source[/green]"

        protocol_text = self.build_protocol_text()

        # Build action and status indicators
        action_color = "green" if self.action == FirewallAction.ALLOW else "red"
        action_text = f"[{action_color}]{self.action}[/{action_color}]"

        status_text = "[red](DISABLED)[/red]" if self.disabled else ""

        # Combine everything
        rich_text = f"  {action_text} {source_text} {protocol_text} Priority: {self.priority} {status_text}"

        # Add target tags if present
        if self.target_tags:
            tags_text = ", ".join(self.target_tags)
            rich_text += f" Target tags: [cyan]{tags_text}[/cyan]"

        return rich_text + "\n"

    def build_protocol_text(self) -> str:
        """Build rich text representation of protocols."""
        if not self.allowed_protocols:
            return "[magenta]All protocols[/magenta]"

        protocol_parts = []
        for protocol_info in self.allowed_protocols:
            protocol_name, ports = self._extract_protocol_info(protocol_info)
            formatted_protocol = self._format_protocol_display(protocol_name, ports)
            protocol_parts.append(formatted_protocol)

        return ", ".join(protocol_parts)

    @classmethod
    def from_gcp(cls, firewall_rule: gcp_compute_v1_types.Firewall) -> Self:
        direction = (
            Direction.INGRESS
            if firewall_rule.direction == "INGRESS"
            else Direction.EGRESS
        )
        action = (
            FirewallAction.ALLOW
            if hasattr(firewall_rule, "allowed") and firewall_rule.allowed
            else FirewallAction.DENY
        )
        source_ranges = list(getattr(firewall_rule, "source_ranges", []))
        allowed_protocols = [
            {
                "IPProtocol": protocol.I_p_protocol,
                "ports": list(protocol.ports) if protocol.ports else [],
            }
            for protocol in (firewall_rule.allowed or [])
        ]
        creation_timestamp = (
            datetime.fromisoformat(firewall_rule.creation_timestamp)
            if firewall_rule.creation_timestamp
            else None
        )

        return cls(
            resource_id=str(firewall_rule.id),
            name=firewall_rule.name,
            direction=direction,
            priority=firewall_rule.priority,
            action=action,
            source_ranges=source_ranges,
            allowed_protocols=allowed_protocols,
            creation_timestamp=creation_timestamp,
            disabled=getattr(firewall_rule, "disabled", False),
            target_tags=list(getattr(firewall_rule, "target_tags", [])),
        )

    def is_permissive(self) -> bool:
        """Check if this firewall rule allows external access."""
        # Only ALLOW rules that are enabled and INGRESS can be permissive
        if (
            self.action != FirewallAction.ALLOW
            or self.disabled
            or self.direction != Direction.INGRESS
        ):
            return False

        # If no source ranges specified, it allows all traffic (permissive)
        if not self.source_ranges:
            return True

        # Check each source range to see if any allow external access
        for source_range in self.source_ranges:
            if self._is_external_source_range(source_range):
                return True

        return False

    def _is_external_source_range(self, source_range: str) -> bool:
        """Check if a source range allows external (non-private) access."""
        try:
            # Handle CIDR notation or single IP
            if "/" in source_range:
                network = ip_address(source_range.split("/")[0])
            else:
                network = ip_address(source_range)

            # Check if it's a global (external) IP address
            # is_global returns True for public IPs, False for private/reserved IPs
            return network.is_global or network in QUAD_ZERO_ADDRESSES
        except ValueError:
            # If we can't parse the IP, assume it's permissive for safety
            return True

    def generate_scan_targets(
        self, ip: str, default_ports: Iterable["ScanTarget"]
    ) -> set["ScanTarget"]:
        """Generate scan targets from this firewall rule."""
        if not self.is_permissive():
            return set()

        ports = set()
        for protocol_info in self.allowed_protocols:
            ports.update(self._process_protocol(protocol_info, ip, default_ports))
        return ports

    def _process_protocol(
        self,
        protocol_info: dict[str, Any],
        ip: str,
        default_ports: Iterable["ScanTarget"],
    ) -> set["ScanTarget"]:
        """Process a single protocol configuration."""
        ports = set()
        protocol_name, port_ranges = self._extract_protocol_info(protocol_info)

        # Skip ICMP protocols
        if protocol_name.upper() in ("ICMP", "ICMPV6"):
            return ports

        # If no specific ports are defined, use default ports
        if not port_ranges:
            if protocol_name.upper() in ("TCP", "UDP", "ALL"):
                ports.update(default_ports)
            return ports

        # Process each port range
        for port_range in port_ranges:
            ports.update(self._parse_port_range(port_range, ip))
        return ports

    def _extract_protocol_info(
        self, protocol_info: dict[str, Any]
    ) -> tuple[str, list[str]]:
        """Extract protocol name and ports from protocol info dict."""
        protocol_name = protocol_info.get("IPProtocol", "Unknown")
        ports = protocol_info.get("ports", [])
        return protocol_name, ports

    def _format_protocol_display(self, protocol_name: str, ports: list[str]) -> str:
        """Format protocol name and ports for display."""
        if ports:
            if len(ports) == 1:
                port_text = f"[blue]{ports[0]}[/blue]"
            else:
                port_text = f"[blue]{', '.join(ports)}[/blue]"
            return f"[magenta]{protocol_name}[/magenta]/{port_text}"
        return f"[magenta]{protocol_name}[/magenta]/all ports"

    def _parse_port_range(self, port_range: str, ip: str) -> set["ScanTarget"]:
        """Parse a port range string and return ScanTargets."""
        ports = set()
        if "-" in port_range:
            # Handle port ranges like "80-443"
            start_port, end_port = port_range.split("-", 1)
            try:
                start = int(start_port)
                end = int(end_port)
                # Use the ScanTarget class directly since it's defined later in this file
                for port_num in range(start, end + 1):
                    ports.add(ScanTarget(target=ip, port=port_num))
            except ValueError:
                # Invalid port range, skip
                pass
        else:
            # Single port
            try:
                port = int(port_range)
                ports.add(ScanTarget(target=ip, port=port))
            except ValueError:
                # Invalid port, skip
                pass
        return ports


@dataclass
class GcpFirewallRules:
    """Collection of related GCP firewall rules"""

    rules: list[GcpFirewallRule] = field(default_factory=list)
    resource_id: str = ""
    resource_type: ResourceType = ResourceType.GCP_Firewall

    def __bool__(self) -> bool:
        return bool(self.rules)

    def build_rich_text(self) -> str:
        """Build rich text representation of all firewall rules."""
        # Only show ingress rules
        ingress_rules = [
            rule for rule in self.rules if rule.direction == Direction.INGRESS
        ]

        if ingress_rules:
            rich_text = f"[dark_orange3]GCP Firewall Rules[/dark_orange3] ({len(self.rules)} rules)\n"
            rich_text += "[bold]Ingress Rules:[/bold]\n"
            for rule in sorted(ingress_rules, key=lambda r: r.priority):
                rich_text += rule.build_rich_text()
            return rich_text

        return "[yellow]No ingress firewall rules[/yellow]\n"


@dataclass
class Container:
    """A representation of a container"""

    image: str
    name: str | None = None
    command: list[str] | None = None
    network_ports: list[int] = field(default_factory=list)

    @classmethod
    def from_gcp(cls, container: gcp_run_v2_types.Container) -> Self:
        return cls(
            image=container.image,
            name=container.name,
            command=list(container.command),
            network_ports=[port.container_port for port in container.ports or []],
        )

    def build_rich_text(self) -> str:
        rich_text = f"Name: [dark_orange3]{self.name or 'Unnamed Container'}[/dark_orange3] Image: [blue]{self.image}[/blue]"
        if self.command:
            rich_text += f" Command: [green]{' '.join(self.command)}[/green]"
        if self.network_ports:
            rich_text += (
                f" Ports: [cyan]{', '.join(map(str, self.network_ports))}[/cyan]"
            )
        return rich_text + "\n"


@dataclass
class GcpTask:
    """A GCP Cloud Run Task"""

    resource_id: str
    name: str
    creation_time: datetime | None = None
    update_time: datetime | None = None
    containers: list[Container] = field(default_factory=list)
    resource_type: ResourceType = ResourceType.GCP_Task

    @classmethod
    def from_gcp(cls, task: gcp_run_v2_types.Task) -> Self:
        containers = [Container.from_gcp(container) for container in task.containers]

        return cls(
            resource_id=task.uid,
            name=task.name,
            creation_time=task.create_time.ToDatetime(),
            update_time=task.update_time.ToDatetime(),
            containers=containers,
        )

    def build_rich_text(self) -> str:
        rich_text = f"Name: [dark_orange3]{self.name or 'Unnamed Task'}[/dark_orange3] Id: {self.resource_id}\n"
        if self.creation_time:
            rich_text += f"  Created at: [blue]{self.creation_time}[/blue]\n"
        if self.update_time:
            rich_text += f"  Last updated at: [blue]{self.update_time}[/blue]\n"
        for container in self.containers:
            rich_text += container.build_rich_text()
        return rich_text


@dataclass
class GcpService:
    """A GCP Cloud Run Service"""

    resource_id: str
    name: str
    uri: str
    creation_time: datetime | None = None
    update_time: datetime | None = None
    created_by: str | None = None
    last_modified_by: str | None = None
    ingress: str | None = None
    urls: list[str] = field(default_factory=list)
    containers: list[Container] = field(default_factory=list)
    resource_type: ResourceType = ResourceType.GCP_Service

    @classmethod
    def from_gcp(cls, service: gcp_run_v2_types.Service) -> Self:
        containers = [
            Container.from_gcp(container) for container in service.template.containers
        ]

        # Extract the service name from the full path
        # service.name format: projects/{project}/locations/{region}/services/{service-name}
        service_name = (
            service.name.split("/")[-1] if "/" in service.name else service.name
        )

        return cls(
            resource_id=service.name,
            name=service_name,
            uri=service.uri,
            creation_time=datetime.fromisoformat(service.create_time.rfc3339()),  # type: ignore
            update_time=datetime.fromisoformat(service.update_time.rfc3339()),  # type: ignore
            created_by=service.creator,
            last_modified_by=service.last_modifier,
            ingress=service.ingress.name if service.ingress else None,
            urls=list(service.urls),
            containers=containers,
        )

    def allows_ingress(self) -> bool:
        """Check if the service has external ingress."""
        return self.ingress in [
            gcp_run_v2_types.IngressTraffic.INGRESS_TRAFFIC_ALL.name,
            gcp_run_v2_types.IngressTraffic.INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER.name,
            gcp_run_v2_types.IngressTraffic.INGRESS_TRAFFIC_UNSPECIFIED.name,
        ]

    def build_rich_text(self) -> str:
        rich_text = f"Name: [dark_orange3]{self.name or 'Unnamed Service'}[/dark_orange3] Id: {self.resource_id}\n"
        if self.created_by:
            rich_text += f"  Created by: [green]{self.created_by}[/green] at [blue]{self.creation_time}[/blue]\n"
        if self.last_modified_by:
            rich_text += f"  Last modified by: [green]{self.last_modified_by}[/green] at [blue]{self.update_time}[/blue]\n"
        if self.ingress:
            rich_text += f"  Ingress: [cyan]{self.ingress}[/cyan]\n"
        if self.urls:
            rich_text += f"  URLs: [blue]{', '.join(self.urls)}[/blue]\n"
        container_text = ""
        for container in self.containers:
            # Indent each container line by 2 spaces
            container_text += container.build_rich_text()
        if container_text:
            rich_text += "  Containers:\n"
            rich_text += textwrap.indent(container_text, "    ")
        return rich_text


@dataclass
class SecurityGroupRule:
    direction: Direction
    protocol: "Protocol"
    from_port: int
    to_port: int
    rule_id: str
    description: str | None = None
    # Target is a CIDR block or a security group ID
    target: str | None = None
    target_type: SecurityGroupRuleTargetType | None = None

    def build_rich_text(self) -> str:
        return f"  [green]{self.target}[/green] {self.direction} [blue]{self.from_port}[/blue] to [blue]{self.to_port}[/blue] [magenta]{self.protocol}[/magenta] ({self.rule_id}: {self.description})\n"

    def is_permissive(self) -> bool:
        if self.target_type == SecurityGroupRuleTargetType.CIDR and isinstance(
            self.target, str
        ):
            ip = ip_address(self.target.split("/")[0])
            return ip.is_global or ip in QUAD_ZERO_ADDRESSES

        # Prefix lists, security groups, and non-global IPs are
        # not considered permissive in the context of the individual rule.
        # Prefix lists and security group targets require further
        # inspection for overall service permissiveness in the context
        # of the environment.
        return False

    @classmethod
    def from_describe_rule(cls, rule: dict[str, Any]) -> Self:
        # Parse the result from calling boto3.ec2.client.describe_security_group_rules

        if pl_id := rule.get("PrefixListId"):
            target = pl_id
            target_type = SecurityGroupRuleTargetType.PREFIX_LIST
        elif target_group_id := rule.get("ReferencedGroupInfo", {}).get("GroupId"):
            target = target_group_id
            target_type = SecurityGroupRuleTargetType.SECURITY_GROUP
        elif ip_range := (rule.get("CidrIpv4") or rule.get("CidrIpv6")):
            target = ip_range
            target_type = SecurityGroupRuleTargetType.CIDR
        else:
            raise NotImplementedError(
                f"Unknown target type for rule: {rule.get('SecurityGroupRuleId')}"
            )

        return cls(
            direction=Direction.EGRESS if rule["IsEgress"] else Direction.INGRESS,
            protocol=Protocol(rule["IpProtocol"]),
            from_port=rule["FromPort"],
            to_port=rule["ToPort"],
            rule_id=rule["SecurityGroupRuleId"],
            description=rule.get("Description"),
            target=target,
            target_type=target_type,
        )


@dataclass
class SecurityGroup:
    group_id: str
    group_name: str
    rules: list[SecurityGroupRule] = field(default_factory=list)
    resource_id: str = ""
    resource_type: ResourceType = ResourceType.EC2_SecurityGroup

    def __post_init__(self) -> None:
        if not self.resource_id:
            self.resource_id = self.group_id

    def build_rich_text(self) -> str:
        rich_text = (
            f"[dark_orange3]{self.group_name}[/dark_orange3] ({self.group_id})\n"
        )
        for rule in self.rules:
            if hasattr(rule, "build_rich_text"):
                rich_text += rule.build_rich_text()
        return rich_text


@dataclass
class AwsLoadBalancerListener:
    resource_id: str
    arn: str
    port: int
    protocol: str
    tags: dict[str, str] = field(default_factory=dict)

    def build_rich_text(self) -> str:
        return f"[blue]{self.port}[/blue]/[magenta]{self.protocol}[/magenta]"

    @classmethod
    def from_describe_listener(cls, listener: dict[str, Any]) -> Self:
        return cls(
            resource_id=listener["ListenerArn"],
            arn=listener["ListenerArn"],
            port=listener["Port"],
            protocol=listener["Protocol"],
        )


@dataclass
class AwsLoadBalancer:
    resource_id: str
    name: str
    arn: str
    dns_name: str
    type: str
    vpc_id: str
    state: str
    scheme: str
    created_time: datetime
    security_groups: list[SecurityGroup] = field(default_factory=list)
    subnets: list[str] = field(default_factory=list)
    listeners: list[AwsLoadBalancerListener] = field(default_factory=list)
    tags: dict[str, str] = field(default_factory=dict)
    resource_type: ResourceType = ResourceType.ELB_LoadBalancer

    def build_rich_text(self) -> str:
        headline = f"[dark_orange3]{self.resource_id}[/dark_orange3] {self.scheme} ({self.state}) Created: {self.created_time}\n"
        listener_details = [listener.build_rich_text() for listener in self.listeners]

        if listener_details:
            return headline + "  Listeners: " + ", ".join(listener_details) + "\n"
        return headline

    @classmethod
    def from_describe_elb(cls, elb: dict[str, Any]) -> Self:
        security_groups = [
            SecurityGroup(group_id=sg_id, group_name="")
            for sg_id in elb["SecurityGroups"]
        ]
        subnets = [az["SubnetId"] for az in elb["AvailabilityZones"]]

        return cls(
            resource_id=elb["LoadBalancerName"],
            name=elb["LoadBalancerName"],
            arn=elb["LoadBalancerArn"],
            dns_name=elb["DNSName"],
            type=elb["Type"],
            vpc_id=elb["VpcId"],
            state=elb["State"]["Code"],
            scheme=elb["Scheme"],
            created_time=elb["CreatedTime"],
            security_groups=security_groups,
            subnets=subnets,
        )


@dataclass
class AwsNetworkInterface:
    resource_id: str
    public_ip: str
    private_ip: str
    attachment_id: str
    attachment_time: datetime
    attachment_status: str
    availability_zone: str
    status: str
    vpc_id: str
    security_groups: list[SecurityGroup] = field(default_factory=list)
    ec2_instance_id: str | None = None
    public_dns_name: str | None = None
    private_dns_name: str | None = None
    description: str | None = None
    interface_type: str | None = None
    subnet_id: str | None = None
    tags: dict[str, str] = field(default_factory=dict)
    resource_type: ResourceType = ResourceType.EC2_NetworkInterface

    def build_rich_text(self) -> str:
        rich_text = f"[dark_orange3]{self.resource_id}[/dark_orange3] in [cyan]{self.vpc_id} ({self.availability_zone})[/cyan]\n"
        if self.ec2_instance_id:
            rich_text += f"EC2: [dark_orange3]{self.ec2_instance_id}[/dark_orange3] attached at [none]{self.attachment_time}\n"
        if self.security_groups:
            security_group_list = ", ".join(
                [
                    f"[dark_orange3]{sg.group_name}[/dark_orange3] ({sg.group_id})"
                    for sg in self.security_groups
                ]
            )
            rich_text += f"Security Groups: {security_group_list}\n"
        return rich_text


@dataclass
class AwsEc2InstanceStateReason:
    # https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_StateReason.html
    code: int | None = None
    message: str | None = None

    def __bool__(self) -> bool:
        return isinstance(self.message, str) and len(self.message) > 0

    @classmethod
    def from_aws_config(cls, state: dict[str, Any]) -> Self:
        if not state:
            return cls()
        return cls(
            code=state.get("code"),
            message=state.get("message"),
        )


@dataclass
class AwsEc2InstanceState:
    # https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_InstanceState.html
    code: int | None = None
    name: str | None = None

    def __bool__(self) -> bool:
        return isinstance(self.name, str) and len(self.name) > 0

    @classmethod
    def from_aws_config(cls, state: dict[str, Any]) -> Self:
        if not state:
            return cls()
        return cls(
            code=state.get("code"),
            name=state.get("name"),
        )


@dataclass
class AwsEc2Instance:
    resource_id: str
    image_id: str
    launch_time: datetime
    tags: dict[str, str]
    platform_details: str
    private_dns_name: str
    private_ip_address: str
    public_dns_name: str
    network_interfaces: list[AwsNetworkInterface | dict[str, Any]]
    security_groups: list[SecurityGroup | dict[str, Any]]
    state: AwsEc2InstanceState | None
    state_reason: AwsEc2InstanceStateReason | None
    usage_operation: str
    usage_operation_update_time: datetime
    subnet_id: str
    vpc_id: str
    public_ip_address: str | None = None
    resource_type: ResourceType = ResourceType.EC2_Instance

    @classmethod
    def from_aws_config(cls, configuration: dict[str, Any]) -> Self:
        tags = convert_tag_set_to_dict(configuration["tags"])

        return cls(
            resource_id=configuration["instanceId"],
            image_id=configuration["imageId"],
            launch_time=datetime.fromisoformat(configuration["launchTime"]),
            tags=tags,
            platform_details=configuration["platformDetails"],
            private_dns_name=configuration["privateDnsName"],
            private_ip_address=configuration["privateIpAddress"],
            public_dns_name=configuration["publicDnsName"],
            public_ip_address=configuration.get("publicIpAddress"),
            network_interfaces=configuration["networkInterfaces"],
            security_groups=configuration["securityGroups"],
            state=AwsEc2InstanceState.from_aws_config(configuration["state"]),
            state_reason=AwsEc2InstanceStateReason.from_aws_config(
                configuration["stateReason"]
            ),
            usage_operation=configuration["usageOperation"],
            usage_operation_update_time=datetime.fromisoformat(
                configuration["usageOperationUpdateTime"]
            ),
            subnet_id=configuration["subnetId"],
            vpc_id=configuration["vpcId"],
        )


@dataclass
class AwsConfigItem:
    resource_type: ResourceType
    resource_id: str
    account: str
    region: str
    arn: str
    config_capture_time: datetime
    config_status: str
    configuration: AwsEc2Instance | str
    tags: dict[str, str]
    resource_creation_time: datetime | None = None
    diff_to_prior: ConfigDiff | None = None

    @staticmethod
    def build_configuration(
        resource_type: ResourceType,
        configuration: str,
    ) -> AwsEc2Instance | str:
        try:
            loaded_configuration = json.loads(configuration)
        except json.JSONDecodeError:
            return configuration

        if resource_type == ResourceType.EC2_Instance:
            return AwsEc2Instance.from_aws_config(loaded_configuration)
        return configuration

    @classmethod
    def from_aws_config(cls, aws_config: Mapping[str, Any]) -> Self:
        config_resource_type = ResourceType(aws_config["resourceType"])

        return cls(
            resource_type=config_resource_type,
            resource_id=aws_config["resourceId"],
            resource_creation_time=aws_config.get("resourceCreationTime"),
            account=aws_config["accountId"],
            region=aws_config["awsRegion"],
            arn=aws_config["arn"],
            config_capture_time=aws_config["configurationItemCaptureTime"],
            config_status=aws_config["configurationItemStatus"],
            configuration=cls.build_configuration(
                config_resource_type,
                aws_config["configuration"],
            ),
            tags=aws_config["tags"],
        )


@dataclass
class NmapPortServices:
    port: int
    protocol: Protocol
    state: str
    name: str | None = None
    product: str | None = None
    version: str | None = None

    def build_rich_text(self) -> str:
        rich_text = f"[green]{self.protocol}/{self.port}[/green] Status: [cyan]{self.state}[/cyan]"

        service_details = ""
        for attr in ["name", "product", "version"]:
            if value := getattr(self, attr):
                service_details += f"{attr.capitalize()}: [cyan]{value}[/cyan] "

        if service_details:
            rich_text += f" {service_details}"

        if not rich_text.endswith("\n"):
            rich_text += "\n"

        return rich_text

    @classmethod
    def from_nmap_port_data(cls, port_data: dict[str, Any]) -> Self:
        """Create NmapPortServices from raw nmap port data."""
        return cls(
            port=int(port_data["portid"]),
            protocol=Protocol(port_data["protocol"]),
            name=port_data["service"].get("name"),
            product=port_data["service"].get("product"),
            version=port_data["service"].get("version"),
            state=port_data["state"],
        )


@dataclass
class ShodanService:
    timestamp: datetime
    port: int | None = None
    protocol: Protocol | None = None
    product: str | None = None
    data: str | None = None
    operating_system: str | None = None
    cpe: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    http_server: str | None = None
    http_title: str | None = None
    opt_heartbleed: str | None = None
    opt_vulnerabilities: list["Vulnerability"] = field(default_factory=list)

    def build_rich_text(self) -> str:
        rich_text = ""
        if self.protocol and self.port:
            rich_text = f"[green]{self.protocol}/{self.port}[/green]"
        if self.product:
            rich_text += f" {self.product}"

        if self.timestamp:
            rich_text += f" (as of {self.timestamp})"

        if rich_text:
            # Add newline after title line
            rich_text += "\n"

        http_information = self._build_html_info_rich_text()

        if http_information:
            rich_text += "  " + http_information + "\n"

        if self.opt_vulnerabilities:
            rich_text += "".join(
                x.build_rich_text() for x in self.opt_vulnerabilities[:5]
            )
            max_to_display = 5
            if len(self.opt_vulnerabilities) > max_to_display:
                rich_text += f"  {len(self.opt_vulnerabilities)} total vulnerabilities found. See JSON for full report.\n"

        return rich_text

    def _build_html_info_rich_text(self) -> str:
        http_information = ""
        if self.http_server:
            http_information += f"HTTP Server: {self.http_server}"
        if self.http_title:
            if http_information:
                http_information += " "
            http_information += f"HTTP Title: {self.http_title}"
        return http_information

    @classmethod
    def from_shodan_host(cls, service: Mapping[str, Any]) -> Self:
        vulns = []
        for cve, vuln_data in service.get("vulns", {}).items():
            vulns.append(
                Vulnerability.from_shodan(
                    cve,
                    vuln_data,
                    datetime.fromisoformat(service["timestamp"]),
                )
            )

        return cls(
            timestamp=datetime.fromisoformat(service["timestamp"]),
            port=service.get("port"),
            protocol=Protocol(service["transport"])
            if service.get("transport")
            else None,
            product=service.get("product"),
            data=service.get("data"),
            operating_system=service.get("os"),
            cpe=service.get("cpe", []),
            tags=service.get("tags", []),
            http_server=service.get("http", {}).get("server"),
            http_title=service.get("http", {}).get("title"),
            opt_heartbleed=service.get("opts", {}).get("heartbleed"),
            opt_vulnerabilities=vulns,
        )


@dataclass
class Hostname:
    name: str
    timestamp: datetime | None = None
    resource_id: str = ""
    resource_type: ResourceType = ResourceType.Hostname

    def __post_init__(self) -> None:
        if not self.resource_id:
            self.resource_id = self.name

    def build_rich_text(self) -> str:
        rich_text = f" Hostname: [dark_orange3]{self.name}[/dark_orange3]"
        if self.timestamp:
            rich_text += f" (as of {self.timestamp})"
        return rich_text + "\n"


@dataclass
class Vulnerability:
    cve: str
    cvss: float | None = None
    cvss_version: int | None = None
    summary: str | None = None
    references: list[str] = field(default_factory=list)
    timestamp: datetime | None = None

    def build_rich_text(self) -> str:
        emphasis = self.cve
        if self.cvss:
            emphasis += f" (CVSS: {self.cvss})"

        return f"  Vulnerability: [red]{emphasis}[/red]\n"

    @classmethod
    def from_shodan(
        cls, cve: str, shodan_data: Mapping[str, Any], timestamp: datetime
    ) -> Self:
        return cls(
            cve=cve,
            cvss=shodan_data.get("cvss"),
            cvss_version=shodan_data.get("cvss_version"),
            summary=shodan_data.get("summary"),
            references=shodan_data.get("references", []),
            timestamp=timestamp,
        )


@dataclass
class Whatweb:
    summary_text: str
    json_data: list[dict[str, Any]]

    def __bool__(self) -> bool:
        return bool(self.summary_text) or bool(self.json_data)

    def build_rich_text(self) -> str:
        rich_text = ""
        for item in self.json_data:
            if target := item.get("target"):
                rich_text += f"- [green]{target}[/green]"
                if value_text := self.build_value_rich_text(item):
                    rich_text += f"\n{value_text}\n"
        return rich_text

    @staticmethod
    def build_value_rich_text(item: dict[str, Any]) -> str:
        item_text = ""
        if not (plugins := item.get("plugins")):
            return item_text

        plugins_to_skip = [
            "Cookies",
            "Country",
            "HttpOnly",
            "IP",
            "Meta-Refresh-Redirect",
            "Script",
            "PasswordField",
            "X-Frame-Options",
            "X-UA-Compatible",
            "X-XSS-Protection",
        ]

        for key, value in plugins.items():
            if key in plugins_to_skip:
                continue
            item_text += f"  [dark_orange3]{key}[/dark_orange3]"
            value_text = ""
            if value:
                if strings := value.get("string", []):
                    value_text += ", ".join(strings)
                if versions := value.get("version", []):
                    value_text += ", ".join(versions)
            if value_text:
                escaped_value_text = value_text.replace("[", "\\[")
                item_text += f": {escaped_value_text}"
            item_text += "\n"
        return item_text


class TimelineEventType(StrEnum):
    COMPUTE_INSTANCE_STATE_CHANGE = "Instance state changed"
    COMPUTE_INSTANCE_CREATED = "Instance created"
    COMPUTE_INSTANCE_TERMINATED = "Instance terminated"
    COMPUTE_INSTANCE_LAUNCH_TIME_UPDATED = "Instance launch time updated"
    COMPUTE_INSTANCE_NETWORKING_CHANGE = "Instance networking change"
    SECURITY_GROUP_ASSOCIATION_CHANGE = "Security group changed"
    SECURITY_GROUP_RULE_CHANGE = "Security group rule changed"
    FIREWALL_RULE_CREATED = "Firewall rule created"
    FIREWALL_RULE_UPDATED = "Firewall rule updated"
    FIREWALL_RULE_DELETED = "Firewall rule deleted"
    RESOURCE_CREATED = "Resource created"
    SERVICE_CREATED = "Service created"
    SERVICE_DELETED = "Service deleted"
    SERVICE_UPDATED = "Service updated"
    SERVICE_DEFINITION_REVISION_CREATED = "Service definition revision created"
    SERVICE_DEFINITION_REVISION_DELETED = "Service definition revision deleted"


@dataclass
class TimelineEvent:
    timestamp: datetime
    source: str
    event_type: TimelineEventType
    resource_id: str
    resource_type: ResourceType
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def build_rich_text(self) -> str:
        return f"[green]{self.timestamp.astimezone(UTC)}[/green] {self.event_type}: [magenta]{self.message}[/magenta] ({self.resource_type} {self.resource_id})\n"


@dataclass
class ScanTarget:
    target: str
    port: int
    schema: str | None = None

    def __str__(self) -> str:
        if self.schema:
            return f"{self.schema.lower()}://{self.target}:{self.port}"
        return f"{self.target}:{self.port}"

    def __hash__(self) -> int:
        return hash((self.target, self.port, self.schema))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ScanTarget):
            return False
        return (self.target, self.port, self.schema) == (
            other.target,
            other.port,
            other.schema,
        )


FindingServices = MutableSequence[NmapPortServices | ShodanService | Whatweb]
FindingResource = (
    AwsConfigItem
    | AwsLoadBalancer
    | AwsNetworkInterface
    | GcpInstance
    | GcpFirewallRules
    | GcpService
    | GcpTask
    | SecurityGroup
    | Hostname
)
FindingResources = MutableSequence[FindingResource]


@dataclass
class ScanFindings:
    tool: str
    services: FindingServices = field(default_factory=list)
    resources: FindingResources = field(default_factory=list)
    events: list[TimelineEvent] = field(default_factory=list)
    emoji_name: str | None = "mag"

    def __bool__(self) -> bool:
        return bool(self.services or self.resources or self.events)

    def build_rich_text(self) -> str:
        rich_title = f"[bold underline]{Emoji(self.emoji_name) if self.emoji_name else ''} {self.tool}[/bold underline]\n"

        rich_text = self.build_rich_text_for_attributes()

        if rich_text:
            return rich_title + rich_text

        return (
            rich_title
            + "No findings to report to the console. See JSON report for full details.\n"
        )

    def build_rich_text_for_attributes(self) -> str:
        rich_text = ""
        for attribute in ["services", "resources", "events"]:
            attribute_title = f"[bold]{attribute.title()}[/bold]:\n"
            items = getattr(self, attribute)
            attribute_text = [
                item.build_rich_text()
                for item in items
                if hasattr(item, "build_rich_text")
            ]

            if attribute_text:
                rich_text += attribute_title + "".join(attribute_text)

            other_items = len(items) - len(attribute_text)
            if other_items:
                other_text = f"  {other_items} {'additional ' if attribute_text else ''}{attribute} discovered.\n"
                if not len(rich_text):
                    rich_text += attribute_title
                rich_text += other_text

        return rich_text


@dataclass
class ScanResult:
    """All associated findings for a single IP address or URL."""

    ip: str | None = None
    url: str | None = None
    findings: list[ScanFindings] = field(default_factory=list)
    region: str | None = None
    eni_id: str | None = None

    def build_rich_panel(self) -> tuple[str, str]:
        rich_text = "\n".join(finding.build_rich_text() for finding in self.findings)
        title = self.ip or self.url or "No IP or URL"
        if self.region:
            title += f" | {self.region}"
        return title, rich_text

    def get_eni_resources(self) -> list[AwsNetworkInterface]:
        eni_resources = []
        for finding in self.findings:
            eni_resources.extend(
                resource
                for resource in finding.resources
                if isinstance(resource, AwsNetworkInterface)
            )
        return eni_resources

    def get_security_group_rules(self) -> list[SecurityGroupRule]:
        sg_rules = []
        for finding in self.findings:
            for resource in finding.resources:
                if isinstance(resource, SecurityGroup):
                    sg_rules.extend(resource.rules)
        return sg_rules

    def get_gcp_firewall_rules(self) -> list[GcpFirewallRule]:
        """Get all GCP firewall rules from the scan findings."""
        firewall_rules = []
        for finding in self.findings:
            for resource in finding.resources:
                if isinstance(resource, GcpFirewallRules):
                    firewall_rules.extend(resource.rules)
        return firewall_rules

    def get_resources_by_type(self, resource_type: type[T]) -> list[T]:
        resources = []
        for finding in self.findings:
            resources.extend(
                resource
                for resource in finding.resources
                if isinstance(resource, resource_type)
            )
        return resources

    def generate_ip_port_targets(self) -> list[str]:
        if not self.ip:
            return []
        return [str(x) for x in self.generate_ip_scan_targets(self.ip)]

    def generate_scan_targets(self) -> set[ScanTarget]:
        if self.ip:
            return self.generate_ip_scan_targets(self.ip)
        if self.url:
            return self.generate_url_scan_targets()
        return set()

    def generate_default_scan_targets(self, target: str) -> set[ScanTarget]:
        return {
            ScanTarget(target=target, port=80, schema="http"),
            ScanTarget(target=target, port=443, schema="https"),
            ScanTarget(target=target, port=3000, schema="http"),
            ScanTarget(target=target, port=5000, schema="http"),
            ScanTarget(target=target, port=8000, schema="http"),
            ScanTarget(target=target, port=8080, schema="http"),
            ScanTarget(target=target, port=8443, schema="https"),
            ScanTarget(target=target, port=8888, schema="http"),
        }

    def generate_url_scan_targets(self) -> set[ScanTarget]:
        if not self.url:
            return set()

        site = urlparse(self.url)

        # Handle case where URL has no scheme (e.g., "example.com")
        # urlparse treats it as path instead of hostname
        if not site.netloc and site.path:
            # Assume it's a hostname without scheme
            hostname = site.path
            return self.generate_default_scan_targets(hostname)

        if not site.hostname:
            return set()
        if not site.port:
            return self.generate_default_scan_targets(site.hostname)

        # Infer scheme from port if not provided
        schema = site.scheme or ("https" if site.port in {443, 5443, 8443} else "http")

        return {
            ScanTarget(
                target=site.hostname,
                port=site.port,
                schema=schema,
            )
        }

    def generate_ip_scan_targets(self, ip: str) -> set[ScanTarget]:
        ports = set()
        default_targets = self.generate_default_scan_targets(ip)

        if sg_ports := self.generate_scan_targets_from_security_groups(
            ip, default_targets
        ):
            ports.update(sg_ports)

        if gcp_ports := self.generate_scan_targets_from_gcp_firewall_rules(
            ip, default_targets
        ):
            ports.update(gcp_ports)

        if elb_ports := self.generate_scan_targets_from_elb_listeners(ip):
            ports.update(elb_ports)

        # If no ports found from security groups, GCP firewall rules, or ELB listeners, use default scan targets
        if not ports:
            ports = default_targets

        return ports

    def generate_scan_targets_from_security_groups(
        self, ip: str, default_ports: Iterable[ScanTarget]
    ) -> set[ScanTarget]:
        ports = set()
        if security_group_rules := self.get_security_group_rules():
            for sg_rule in security_group_rules:
                if sg_rule.protocol in (Protocol.ICMP, Protocol.ICMPv6):
                    continue
                if sg_rule.protocol == Protocol.ALL:
                    ports.update(default_ports)
                ports.update(
                    {
                        ScanTarget(target=ip, port=x)
                        for x in range(sg_rule.from_port, sg_rule.to_port + 1)
                    }
                )
        return ports

    def generate_scan_targets_from_gcp_firewall_rules(
        self, ip: str, default_ports: Iterable[ScanTarget]
    ) -> set[ScanTarget]:
        """Generate scan targets from GCP firewall rules."""
        ports = set()
        if firewall_rules := self.get_gcp_firewall_rules():
            for fw_rule in firewall_rules:
                ports.update(fw_rule.generate_scan_targets(ip, default_ports))
        return ports

    def generate_scan_targets_from_elb_listeners(self, ip: str) -> set[ScanTarget]:
        ports = set()
        if load_balancers := self.get_resources_by_type(AwsLoadBalancer):
            for elb in load_balancers:
                for listener in elb.listeners:
                    ports.add(
                        ScanTarget(
                            target=ip,
                            port=listener.port,
                            schema=listener.protocol.lower(),
                        )
                    )
        return ports

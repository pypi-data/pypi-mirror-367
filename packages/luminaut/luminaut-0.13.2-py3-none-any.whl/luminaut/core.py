import asyncio
import logging
import sys

from luminaut import models
from luminaut.report import (
    console,
    write_csv_timeline,
    write_html_report,
    write_jsonl_report,
)
from luminaut.scanner import Scanner

logger = logging.getLogger(__name__)


class Luminaut:
    def __init__(self, config: models.LuminautConfig | None = None):
        self.config = config if config else models.LuminautConfig()
        self.scanner = Scanner(config=self.config)

    def run(self):
        scan_results = self.discover_public_ips()
        scan_results = self.gather_public_ip_context(scan_results)
        self.report(scan_results)

    def report(self, scan_results: list[models.ScanResult]) -> None:
        if self.config.report.json:
            if self.config.report.json_file:
                with self.config.report.json_file.open("w") as target:
                    write_jsonl_report(scan_results, target)
                logger.info("Saved scan results to %s", self.config.report.json_file)
            else:
                write_jsonl_report(scan_results, sys.stdout)

        if self.config.report.timeline and self.config.report.timeline_file:
            with self.config.report.timeline_file.open(
                "w", encoding="utf-8", newline=""
            ) as target:
                write_csv_timeline(scan_results, target)
            logger.info("Saved timeline to %s", self.config.report.timeline_file)

        if self.config.report.console:
            for scan_result in scan_results:
                title, text = scan_result.build_rich_panel()
                console.rule(title, align="left")
                console.print(text)

        if self.config.report.html and self.config.report.html_file:
            write_html_report(self.config.report.html_file)

    def discover_public_ips(self) -> list[models.ScanResult]:
        return self.scanner.aws() + self.scanner.gcp()

    def gather_public_ip_context(
        self, scan_results: list[models.ScanResult]
    ) -> list[models.ScanResult]:
        return asyncio.run(self.process_all_scan_results(scan_results))

    def run_nmap(self, scan_result: models.ScanResult) -> list[models.ScanFindings]:
        if not self.config.nmap.enabled:
            return []

        scan_targets = scan_result.generate_scan_targets()

        target = list({scan_target.target for scan_target in scan_targets})
        if not target:
            logger.warning(
                "No valid targets found for nmap scan on target: %s",
                scan_result.url or scan_result.ip,
            )
            return []

        target_ports = list({str(scan_target.port) for scan_target in scan_targets})
        if not target_ports:
            logger.warning(
                "No valid ports found for nmap scan on target: %s",
                scan_result.url or scan_result.ip,
            )
            return []
        return self.scanner.nmap(target[0], ports=target_ports).findings

    def query_shodan(self, scan_result: models.ScanResult) -> list[models.ScanFindings]:
        if (
            self.config.shodan.enabled
            and scan_result.ip
            and (shodan_finding := self.scanner.shodan(scan_result.ip))
        ):
            return [shodan_finding]
        return []

    def run_whatweb(self, scan_result: models.ScanResult) -> list[models.ScanFindings]:
        if self.config.whatweb.enabled:
            targets = scan_result.generate_ip_port_targets()
            if targets and (whatweb_findings := self.scanner.whatweb(targets)):
                return [whatweb_findings]
        return []

    async def _run_nmap_async(
        self, scan_result: models.ScanResult
    ) -> list[models.ScanFindings]:
        """Async wrapper for nmap scanning."""
        return await asyncio.to_thread(self.run_nmap, scan_result)

    async def _query_shodan_async(
        self, scan_result: models.ScanResult
    ) -> list[models.ScanFindings]:
        """Async wrapper for Shodan querying."""
        return await asyncio.to_thread(self.query_shodan, scan_result)

    async def _run_whatweb_async(
        self, scan_result: models.ScanResult
    ) -> list[models.ScanFindings]:
        """Async wrapper for whatweb scanning."""
        return await asyncio.to_thread(self.run_whatweb, scan_result)

    async def process_scan_result(
        self, scan_result: models.ScanResult
    ) -> models.ScanResult:
        # Run all scanner operations concurrently for each scan result
        nmap_task = asyncio.create_task(self._run_nmap_async(scan_result))
        shodan_task = asyncio.create_task(self._query_shodan_async(scan_result))
        whatweb_task = asyncio.create_task(self._run_whatweb_async(scan_result))

        # Wait for all tasks to complete
        nmap_findings, shodan_findings, whatweb_findings = await asyncio.gather(
            nmap_task, shodan_task, whatweb_task
        )

        # Update scan result with findings
        scan_result.findings += nmap_findings + shodan_findings + whatweb_findings
        return scan_result

    async def process_all_scan_results(
        self, scan_results: list[models.ScanResult]
    ) -> list[models.ScanResult]:
        tasks = [self.process_scan_result(scan_result) for scan_result in scan_results]
        return await asyncio.gather(*tasks)

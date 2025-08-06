"""Command-line interface for IAM JSON Lint."""

import click
import json
from pathlib import Path
from typing import Optional

from .linter import IAMLinter
from .validator import IAMValidator


@click.group()
@click.version_option()
def cli():
    """IAM JSON Lint - A tool for linting and validating IAM policies."""
    pass


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format",
)
@click.option(
    "--severity",
    type=click.Choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
    help="Filter findings by minimum severity level",
)
def lint(file_path: Path, output_format: str, severity: Optional[str]):
    """Lint an IAM policy file using Parliament.

    Exit codes:
    0 - No issues found
    1 - Critical or High severity issues found
    2 - Medium or Low severity issues found
    """
    linter = IAMLinter()

    try:
        findings = linter.lint_file(file_path)

        # Filter by severity if specified
        if severity:
            severity_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
            min_severity = severity_order[severity]
            findings = [
                f
                for f in findings
                if severity_order.get(f.get("severity", "LOW"), 1) >= min_severity
            ]

        if output_format == "json":
            click.echo(json.dumps(findings, indent=2))
        else:
            _print_findings_text(findings, file_path)

        # Exit with appropriate code
        if findings:
            # Check if any findings are CRITICAL or HIGH severity
            has_critical_or_high = any(
                f.get("severity") in ["CRITICAL", "HIGH"] for f in findings
            )
            if has_critical_or_high:
                raise click.Abort()  # Exit code 1
            else:
                # Exit code 2 for medium/low issues (configurable behavior)
                import sys

                sys.exit(2)
        # Exit code 0 for no issues (success)

    except click.Abort:
        raise  # Re-raise to maintain exit code 1
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()  # Exit code 1 for errors


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format",
)
def validate(file_path: Path, output_format: str):
    """Validate IAM policy file structure and syntax.

    Exit codes:
    0 - Valid policy
    1 - Validation errors found
    """
    validator = IAMValidator()

    try:
        errors = validator.validate_file(file_path)

        if output_format == "json":
            click.echo(json.dumps(errors, indent=2))
        else:
            _print_validation_errors_text(errors, file_path)

        # Exit with error code if validation errors found
        if errors:
            raise click.Abort()  # Exit code 1
        # Exit code 0 for valid files

    except click.Abort:
        raise  # Re-raise to maintain exit code 1
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()  # Exit code 1 for errors


@cli.command()
@click.argument(
    "directory_path", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option(
    "--pattern", default="*.json", help="File pattern to match (default: *.json)"
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format",
)
@click.option(
    "--severity",
    type=click.Choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
    help="Filter findings by minimum severity level",
)
def lint_dir(
    directory_path: Path, pattern: str, output_format: str, severity: Optional[str]
):
    """Lint all IAM policy files in a directory.

    Exit codes:
    0 - No issues found in any files
    1 - Critical or High severity issues found
    2 - Medium or Low severity issues found
    """
    linter = IAMLinter()

    try:
        results = linter.lint_directory(directory_path, pattern)

        # Filter by severity if specified
        if severity:
            severity_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
            min_severity = severity_order[severity]
            filtered_results = {}
            for file_path, findings in results.items():
                filtered_findings = [
                    f
                    for f in findings
                    if severity_order.get(f.get("severity", "LOW"), 1) >= min_severity
                ]
                if filtered_findings:  # Only include files with findings
                    filtered_results[file_path] = filtered_findings
            results = filtered_results

        if output_format == "json":
            click.echo(json.dumps(results, indent=2))
        else:
            _print_directory_results_text(results)

        # Exit with appropriate code based on findings
        all_findings = []
        for findings in results.values():
            all_findings.extend(findings)

        if all_findings:
            # Check if any findings are CRITICAL or HIGH severity
            has_critical_or_high = any(
                f.get("severity") in ["CRITICAL", "HIGH"] for f in all_findings
            )
            if has_critical_or_high:
                raise click.Abort()  # Exit code 1
            else:
                # Exit code 2 for medium/low issues (configurable behavior)
                import sys

                sys.exit(2)
        # Exit code 0 for no issues (success)

    except click.Abort:
        raise  # Re-raise to maintain exit code 1
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()  # Exit code 1 for errors


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--key-path",
    "key_paths",
    multiple=True,
    default=["spec.resourceConfig.inlinePolicy[].policy"],
    help="Key path(s) to extract policies from (can be specified multiple times)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format",
)
@click.option(
    "--severity",
    type=click.Choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
    help="Filter findings by minimum severity level",
)
def lint_embedded(file_path: Path, key_paths: tuple, output_format: str, severity: Optional[str]):
    """Lint JSON policies embedded in YAML files.
    
    This command extracts JSON IAM policies from YAML files using configurable key paths
    and lints them using Parliament.
    
    Examples:
    
        # Lint policies from default key path
        iam-json-lint lint-embedded myfile.yaml
        
        # Lint from custom key path
        iam-json-lint lint-embedded myfile.yaml --key-path "data.policies[].content"
        
        # Lint from multiple key paths
        iam-json-lint lint-embedded myfile.yaml --key-path "spec.policies[].policy" --key-path "data.inline[]"

    Exit codes:
    0 - No issues found
    1 - Critical or High severity issues found
    2 - Medium or Low severity issues found
    """
    linter = IAMLinter()

    try:
        findings = linter.lint_embedded_policies(file_path, list(key_paths))

        # Filter by severity if specified
        if severity:
            severity_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
            min_severity = severity_order[severity]
            findings = [
                f
                for f in findings
                if severity_order.get(f.get("severity", "LOW"), 1) >= min_severity
            ]

        if output_format == "json":
            click.echo(json.dumps(findings, indent=2))
        else:
            _print_embedded_findings_text(findings, file_path, key_paths)

        # Exit with appropriate code
        if findings:
            # Check if any findings are CRITICAL or HIGH severity
            has_critical_or_high = any(
                f.get("severity") in ["CRITICAL", "HIGH"] for f in findings
            )
            if has_critical_or_high:
                raise click.Abort()  # Exit code 1
            else:
                # Exit code 2 for medium/low issues (configurable behavior)
                import sys

                sys.exit(2)
        # Exit code 0 for no issues (success)

    except click.Abort:
        raise  # Re-raise to maintain exit code 1
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()  # Exit code 1 for errors


def _print_embedded_findings_text(findings: list, file_path: Path, key_paths: tuple):
    """Print embedded policy findings in human-readable text format."""
    click.echo(f"\n🔍 Embedded policy linting results for: {file_path}")
    click.echo(f"📍 Key paths: {', '.join(key_paths)}")
    click.echo("=" * 60)

    if not findings:
        click.echo("✅ No issues found in embedded policies!")
        return

    # Group findings by source
    findings_by_source = {}
    for finding in findings:
        embedded_source = finding.get('embedded_source', {})
        source_key = f"{embedded_source.get('key_path', 'unknown')}[{embedded_source.get('index', 0)}]"
        if source_key not in findings_by_source:
            findings_by_source[source_key] = []
        findings_by_source[source_key].append(finding)

    for source_key, source_findings in findings_by_source.items():
        click.echo(f"\n📍 Source: {source_key}")
        click.echo("-" * 40)
        
        for i, finding in enumerate(source_findings, 1):
            severity = finding.get("severity", "UNKNOWN")
            emoji = _get_severity_emoji(severity)

            click.echo(f"\n{emoji} Issue #{i} - {severity}")
            click.echo(f"Title: {finding.get('title', 'N/A')}")
            click.echo(f"Issue: {finding.get('issue', 'N/A')}")
            click.echo(f"Description: {finding.get('description', 'N/A')}")

            if finding.get("location"):
                click.echo(f"Location: {finding['location']}")

            if finding.get("detail"):
                click.echo(f"Detail: {finding['detail']}")


def _print_findings_text(findings: list, file_path: Path):
    """Print findings in human-readable text format."""
    click.echo(f"\n🔍 Linting results for: {file_path}")
    click.echo("=" * 60)

    if not findings:
        click.echo("✅ No issues found!")
        return

    for i, finding in enumerate(findings, 1):
        severity = finding.get("severity", "UNKNOWN")
        emoji = _get_severity_emoji(severity)

        click.echo(f"\n{emoji} Issue #{i} - {severity}")
        click.echo(f"Title: {finding.get('title', 'N/A')}")
        click.echo(f"Issue: {finding.get('issue', 'N/A')}")
        click.echo(f"Description: {finding.get('description', 'N/A')}")

        if finding.get("location"):
            click.echo(f"Location: {finding['location']}")

        if finding.get("detail"):
            click.echo(f"Detail: {finding['detail']}")


def _print_validation_errors_text(errors: list, file_path: Path):
    """Print validation errors in human-readable text format."""
    click.echo(f"\n✅ Validation results for: {file_path}")
    click.echo("=" * 60)

    if not errors:
        click.echo("✅ No validation errors found!")
        return

    for i, error in enumerate(errors, 1):
        severity = error.get("severity", "UNKNOWN")
        emoji = "❌" if severity == "ERROR" else "⚠️"

        click.echo(f"\n{emoji} {severity} #{i}")
        click.echo(f"Type: {error.get('type', 'N/A')}")
        click.echo(f"Message: {error.get('message', 'N/A')}")
        click.echo(f"Location: {error.get('location', 'N/A')}")


def _print_directory_results_text(results: dict):
    """Print directory linting results in human-readable text format."""
    click.echo(f"\n🔍 Directory linting results")
    click.echo("=" * 60)

    # Filter out files with no findings for display
    files_with_issues = {
        path: findings for path, findings in results.items() if findings
    }

    if not files_with_issues:
        click.echo("✅ No issues found in any files!")
        return

    total_issues = sum(len(findings) for findings in files_with_issues.values())
    total_files_checked = len(results)
    files_with_issues_count = len(files_with_issues)

    click.echo(f"Checked {total_files_checked} file(s)")
    click.echo(
        f"Found issues in {files_with_issues_count} file(s), total issues: {total_issues}"
    )

    for file_path, findings in files_with_issues.items():
        click.echo(f"\n📄 File: {file_path}")
        click.echo("-" * 40)

        for i, finding in enumerate(findings, 1):
            severity_raw = finding.get("severity", "UNKNOWN")
            severity = (
                severity_raw.upper() if severity_raw else "UNKNOWN"
            ) or "UNKNOWN"
            emoji = _get_severity_emoji(severity)

            # Try to get a meaningful title or fall back to issue type
            title = finding.get("title") or finding.get("issue", "Unknown Issue")

            # Format the display text
            if severity and severity != "UNKNOWN":
                display_text = f"{severity}: {title}"
            else:
                display_text = str(title)

            # Add context from location if available
            location = finding.get("location", {})
            if isinstance(location, dict) and location.get("actions"):
                actions = location["actions"]
                if len(actions) <= 3:
                    action_text = ", ".join(actions)
                else:
                    action_text = f"{', '.join(actions[:3])} and {len(actions)-3} more"
                display_text += f" (affects: {action_text})"

            click.echo(f"  {emoji} {display_text}")


def _get_severity_emoji(severity: str) -> str:
    """Get emoji for severity level."""
    return {
        "CRITICAL": "🚨",
        "HIGH": "🔴",
        "MEDIUM": "🟠",
        "LOW": "🟡",
        "ERROR": "❌",
        "WARNING": "⚠️",
    }.get(severity, "⚪")


if __name__ == "__main__":
    cli()

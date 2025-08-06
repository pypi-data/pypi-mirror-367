"""IAM Policy Linter using Parliament."""

import json
import os
import yaml
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import parliament


class IAMLinter:
    """A linter for IAM policies using Parliament."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the IAM linter.

        Args:
            config: Optional configuration dictionary for Parliament
        """
        self.config = config or {}

    def lint_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Lint an IAM policy file.

        Args:
            file_path: Path to the IAM policy file (JSON or YAML)

        Returns:
            List of findings/issues found by Parliament

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is unsupported or invalid
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read and parse the file
        policy_doc = self._load_policy_file(file_path)

        # Lint the policy
        return self.lint_policy(policy_doc)

    def lint_policy(
        self,
        policy_content: Union[str, Dict[str, Any]],
        file_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Lint a policy using Parliament."""
        try:
            # Convert policy to string if it's a dict
            if isinstance(policy_content, dict):
                policy_str = json.dumps(policy_content)
            else:
                policy_str = policy_content

            # Load config override if available
            config_path = None

            # Try different locations for config_override.yaml
            config_locations = [
                "config_override.yaml",  # Current directory
                os.path.join(
                    os.path.dirname(__file__), "..", "..", "config_override.yaml"
                ),  # Dev environment
                os.path.join(
                    os.path.dirname(__file__), "config_override.yaml"
                ),  # Package data
            ]

            for location in config_locations:
                if os.path.exists(location):
                    config_path = os.path.abspath(location)
                    break

            if config_path:
                # Load the config override first
                parliament.override_config(config_path)

            # Use Parliament to analyze the policy
            result = parliament.analyze_policy_string(
                policy_str, filepath=file_path, include_community_auditors=True
            )

            # Convert Parliament findings to our format
            findings = []
            for finding in result.findings:
                # Enhance finding with config if available
                try:
                    enhanced_finding = parliament.enhance_finding(finding)
                except Exception:
                    # If enhance_finding fails, use original finding
                    enhanced_finding = finding

                findings.append(
                    {
                        "issue": enhanced_finding.issue,
                        "title": enhanced_finding.title
                        or enhanced_finding.issue.replace("_", " ").title(),
                        "description": enhanced_finding.description
                        or f"Policy issue: {enhanced_finding.issue}",
                        "severity": enhanced_finding.severity or "MEDIUM",
                        "detail": enhanced_finding.detail,
                        "location": enhanced_finding.location,
                    }
                )

            return findings

        except Exception as e:
            return [
                {
                    "issue": "EXCEPTION",
                    "title": "Analysis Exception",
                    "description": f"An error occurred during analysis: {str(e)}",
                    "severity": "HIGH",
                    "detail": str(e),
                    "location": {"exception": str(e)},
                }
            ]

    def _load_policy_file(self, file_path: Path) -> Dict[str, Any]:
        """Load a policy file (JSON or YAML).

        Args:
            file_path: Path to the policy file

        Returns:
            Policy document as a dictionary

        Raises:
            ValueError: If the file format is unsupported or invalid
        """
        content = file_path.read_text(encoding="utf-8")

        if file_path.suffix.lower() in [".json"]:
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {file_path}: {e}")

        elif file_path.suffix.lower() in [".yml", ".yaml"]:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in {file_path}: {e}")
        else:
            # Try to auto-detect format
            try:
                # Try JSON first
                return json.loads(content)
            except json.JSONDecodeError:
                try:
                    # Try YAML
                    return yaml.safe_load(content)
                except yaml.YAMLError:
                    raise ValueError(
                        f"Unsupported file format for {file_path}. Must be JSON or YAML."
                    )

    def _format_findings(self, findings: List) -> List[Dict[str, Any]]:
        """Format Parliament findings into a consistent structure.

        Args:
            findings: Raw findings from Parliament

        Returns:
            Formatted findings
        """
        formatted_findings = []

        for finding in findings:
            formatted_finding = {
                "issue": finding.issue,
                "title": finding.title,
                "description": finding.description,
                "severity": finding.severity,
                "location": getattr(finding, "location", None),
                "detail": getattr(finding, "detail", None),
            }
            formatted_findings.append(formatted_finding)

        return formatted_findings

    def lint_directory(
        self, directory_path: Union[str, Path], pattern: str = "*.json"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Lint all policy files in a directory.

        Args:
            directory_path: Path to directory containing IAM policy files
            pattern: File pattern to match (default: "*.json")

        Returns:
            Dictionary mapping file paths to their findings
        """
        directory_path = Path(directory_path)
        results = {}

        # Support both JSON and YAML patterns
        if pattern == "*.json":
            patterns = ["*.json"]
        elif pattern == "*.yaml" or pattern == "*.yml":
            patterns = ["*.yaml", "*.yml"]
        else:
            patterns = [pattern]

        for pattern in patterns:
            for file_path in directory_path.glob(pattern):
                try:
                    findings = self.lint_file(file_path)
                    results[str(file_path)] = findings
                except Exception as e:
                    results[str(file_path)] = [
                        {
                            "issue": "PARSE_ERROR",
                            "title": "File parsing error",
                            "description": str(e),
                            "severity": "HIGH",
                            "location": None,
                            "detail": None,
                        }
                    ]

        return results

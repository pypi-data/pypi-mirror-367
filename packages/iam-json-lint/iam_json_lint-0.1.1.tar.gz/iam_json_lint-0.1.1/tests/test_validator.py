"""Tests for IAM Validator."""

import pytest
from src.iam_json_lint.validator import IAMValidator


class TestIAMValidator:
    """Test cases for IAMValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = IAMValidator()

    def test_valid_policy(self):
        """Test validation of a valid IAM policy."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::my-bucket/*",
                }
            ],
        }

        errors = self.validator.validate_policy(policy)
        assert len(errors) == 0

    def test_missing_version(self):
        """Test validation when Version is missing."""
        policy = {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::my-bucket/*",
                }
            ]
        }

        errors = self.validator.validate_policy(policy)
        assert len(errors) == 1
        assert errors[0]["type"] == "MISSING_REQUIRED_FIELD"
        assert "Version" in errors[0]["message"]

    def test_missing_statement(self):
        """Test validation when Statement is missing."""
        policy = {"Version": "2012-10-17"}

        errors = self.validator.validate_policy(policy)
        assert len(errors) == 1
        assert errors[0]["type"] == "MISSING_REQUIRED_FIELD"
        assert "Statement" in errors[0]["message"]

    def test_invalid_version(self):
        """Test validation with invalid version."""
        policy = {
            "Version": "2020-01-01",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::my-bucket/*",
                }
            ],
        }

        errors = self.validator.validate_policy(policy)
        assert len(errors) == 1
        assert errors[0]["type"] == "INVALID_VALUE"
        assert errors[0]["severity"] == "WARNING"

    def test_missing_effect(self):
        """Test validation when Effect is missing from statement."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Action": "s3:GetObject", "Resource": "arn:aws:s3:::my-bucket/*"}
            ],
        }

        errors = self.validator.validate_policy(policy)
        assert len(errors) == 1
        assert errors[0]["type"] == "MISSING_REQUIRED_FIELD"
        assert "Effect" in errors[0]["message"]

    def test_invalid_effect(self):
        """Test validation with invalid Effect value."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Maybe",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::my-bucket/*",
                }
            ],
        }

        errors = self.validator.validate_policy(policy)
        assert len(errors) == 1
        assert errors[0]["type"] == "INVALID_VALUE"
        assert "Effect" in errors[0]["message"]

    def test_statement_as_single_object(self):
        """Test validation with Statement as single object (not array)."""
        policy = {
            "Version": "2012-10-17",
            "Statement": {
                "Effect": "Allow",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::my-bucket/*",
            },
        }

        errors = self.validator.validate_policy(policy)
        assert len(errors) == 0

    def test_missing_action_and_resource_warnings(self):
        """Test warnings for missing Action and Resource."""
        policy = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow"}]}

        errors = self.validator.validate_policy(policy)
        # Should have warnings for missing Action/NotAction and Resource/NotResource/Principal/NotPrincipal
        warning_types = [
            error["type"] for error in errors if error["severity"] == "WARNING"
        ]
        assert "MISSING_REQUIRED_FIELD" in warning_types
        assert len([e for e in errors if "Action" in e["message"]]) >= 1

    def test_not_a_dict(self):
        """Test validation when policy is not a dictionary."""
        policy = "not a dict"

        errors = self.validator.validate_policy(policy)
        assert len(errors) == 1
        assert errors[0]["type"] == "STRUCTURE_ERROR"

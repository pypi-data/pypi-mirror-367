"""IAM Policy Validator for basic structure and syntax validation."""

import json
import yaml
from typing import Dict, List, Any, Optional, Union
from pathlib import Path


class IAMValidator:
    """A validator for IAM policy basic structure and syntax."""

    # Required top-level keys for IAM policy documents
    REQUIRED_POLICY_KEYS = {"Version", "Statement"}

    # Valid values for Version field
    VALID_VERSIONS = {"2012-10-17", "2008-10-17"}

    # Required keys for Statement elements
    REQUIRED_STATEMENT_KEYS = {"Effect"}

    # Valid values for Effect field
    VALID_EFFECTS = {"Allow", "Deny"}

    def __init__(self):
        """Initialize the IAM validator."""
        pass

    def validate_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Validate an IAM policy file for basic structure and syntax.

        Args:
            file_path: Path to the IAM policy file (JSON or YAML)

        Returns:
            List of validation errors/warnings

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Read and parse the file
            policy_doc = self._load_policy_file(file_path)

            # Validate the policy
            return self.validate_policy(policy_doc)
        except Exception as e:
            return [
                {
                    "type": "PARSE_ERROR",
                    "severity": "ERROR",
                    "message": f"Failed to parse file: {e}",
                    "location": str(file_path),
                }
            ]

    def validate_policy(self, policy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate an IAM policy document structure.

        Args:
            policy: IAM policy document as a dictionary

        Returns:
            List of validation errors/warnings
        """
        errors = []

        # Check top-level structure
        errors.extend(self._validate_top_level(policy))

        # Check Version field
        if "Version" in policy:
            errors.extend(self._validate_version(policy["Version"]))

        # Check Statement field
        if "Statement" in policy:
            errors.extend(self._validate_statements(policy["Statement"]))

        return errors

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
                raise ValueError(f"Invalid JSON: {e}")

        elif file_path.suffix.lower() in [".yml", ".yaml"]:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML: {e}")
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
                    raise ValueError("Unsupported file format. Must be JSON or YAML.")

    def _validate_top_level(self, policy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate top-level policy structure.

        Args:
            policy: Policy document

        Returns:
            List of validation errors
        """
        errors = []

        # Check if policy is a dictionary
        if not isinstance(policy, dict):
            errors.append(
                {
                    "type": "STRUCTURE_ERROR",
                    "severity": "ERROR",
                    "message": "Policy document must be a JSON object",
                    "location": "root",
                }
            )
            return errors

        # Check required keys
        missing_keys = self.REQUIRED_POLICY_KEYS - set(policy.keys())
        for key in missing_keys:
            errors.append(
                {
                    "type": "MISSING_REQUIRED_FIELD",
                    "severity": "ERROR",
                    "message": f"Missing required field: {key}",
                    "location": "root",
                }
            )

        return errors

    def _validate_version(self, version: Any) -> List[Dict[str, Any]]:
        """Validate the Version field.

        Args:
            version: Version field value

        Returns:
            List of validation errors
        """
        errors = []

        if not isinstance(version, str):
            errors.append(
                {
                    "type": "INVALID_TYPE",
                    "severity": "ERROR",
                    "message": "Version must be a string",
                    "location": "Version",
                }
            )
        elif version not in self.VALID_VERSIONS:
            errors.append(
                {
                    "type": "INVALID_VALUE",
                    "severity": "WARNING",
                    "message": f"Version '{version}' is not a standard IAM policy version. "
                    f"Standard versions are: {', '.join(self.VALID_VERSIONS)}",
                    "location": "Version",
                }
            )

        return errors

    def _validate_statements(self, statements: Any) -> List[Dict[str, Any]]:
        """Validate the Statement field.

        Args:
            statements: Statement field value (can be a single statement or list)

        Returns:
            List of validation errors
        """
        errors = []

        # Normalize to list
        if isinstance(statements, dict):
            statements = [statements]
        elif not isinstance(statements, list):
            errors.append(
                {
                    "type": "INVALID_TYPE",
                    "severity": "ERROR",
                    "message": "Statement must be an object or array of objects",
                    "location": "Statement",
                }
            )
            return errors

        # Validate each statement
        for i, statement in enumerate(statements):
            errors.extend(self._validate_single_statement(statement, f"Statement[{i}]"))

        return errors

    def _validate_single_statement(
        self, statement: Any, location: str
    ) -> List[Dict[str, Any]]:
        """Validate a single statement object.

        Args:
            statement: Statement object
            location: Location string for error reporting

        Returns:
            List of validation errors
        """
        errors = []

        if not isinstance(statement, dict):
            errors.append(
                {
                    "type": "INVALID_TYPE",
                    "severity": "ERROR",
                    "message": "Statement must be an object",
                    "location": location,
                }
            )
            return errors

        # Check required keys
        missing_keys = self.REQUIRED_STATEMENT_KEYS - set(statement.keys())
        for key in missing_keys:
            errors.append(
                {
                    "type": "MISSING_REQUIRED_FIELD",
                    "severity": "ERROR",
                    "message": f"Missing required field: {key}",
                    "location": f"{location}.{key}",
                }
            )

        # Validate Effect field
        if "Effect" in statement:
            effect = statement["Effect"]
            if not isinstance(effect, str):
                errors.append(
                    {
                        "type": "INVALID_TYPE",
                        "severity": "ERROR",
                        "message": "Effect must be a string",
                        "location": f"{location}.Effect",
                    }
                )
            elif effect not in self.VALID_EFFECTS:
                errors.append(
                    {
                        "type": "INVALID_VALUE",
                        "severity": "ERROR",
                        "message": f"Effect must be one of: {', '.join(self.VALID_EFFECTS)}",
                        "location": f"{location}.Effect",
                    }
                )

        # Check that at least one of Action/NotAction is present
        if "Action" not in statement and "NotAction" not in statement:
            errors.append(
                {
                    "type": "MISSING_REQUIRED_FIELD",
                    "severity": "WARNING",
                    "message": "Statement should have either Action or NotAction",
                    "location": location,
                }
            )

        # Check that at least one of Resource/NotResource is present for non-identity-based policies
        if (
            "Resource" not in statement
            and "NotResource" not in statement
            and "Principal" not in statement
            and "NotPrincipal" not in statement
        ):
            errors.append(
                {
                    "type": "MISSING_REQUIRED_FIELD",
                    "severity": "WARNING",
                    "message": "Statement should have Resource, NotResource, Principal, or NotPrincipal",
                    "location": location,
                }
            )

        return errors

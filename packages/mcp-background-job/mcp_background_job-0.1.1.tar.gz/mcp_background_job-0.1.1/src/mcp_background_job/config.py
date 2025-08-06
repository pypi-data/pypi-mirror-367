"""Configuration management for MCP Background Job Server."""

import os
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class BackgroundJobConfig(BaseModel):
    """Configuration for the background job server."""

    max_concurrent_jobs: int = Field(
        default=10, description="Maximum number of concurrent jobs", ge=1, le=100
    )
    max_output_size_bytes: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum output buffer size per job in bytes",
        ge=1024,  # At least 1KB
        le=100 * 1024 * 1024,  # At most 100MB
    )
    default_job_timeout: Optional[int] = Field(
        default=None,
        description="Default job timeout in seconds",
        ge=1,
    )
    cleanup_interval_seconds: int = Field(
        default=300,
        description="Cleanup interval for terminated jobs in seconds",
        ge=10,
        le=3600,
    )
    allowed_command_patterns: List[str] = Field(
        default_factory=list,
        description="List of allowed command patterns (empty = allow all)",
    )
    working_directory: str = Field(
        default=".", description="Working directory for job execution"
    )

    @field_validator("allowed_command_patterns", mode="before")
    @classmethod
    def split_command_patterns(cls, v):
        """Split comma-separated command patterns from environment variables."""
        if isinstance(v, str):
            return [pattern.strip() for pattern in v.split(",") if pattern.strip()]
        return v

    @field_validator("working_directory")
    @classmethod
    def validate_working_directory(cls, v):
        """Ensure working directory exists and is accessible."""
        if not os.path.exists(v):
            raise ValueError(f"Working directory does not exist: {v}")
        if not os.path.isdir(v):
            raise ValueError(f"Working directory is not a directory: {v}")
        if not os.access(v, os.R_OK | os.W_OK):
            raise ValueError(f"Working directory is not accessible: {v}")
        return v

    @classmethod
    def from_environment(cls) -> "BackgroundJobConfig":
        """Load configuration from environment variables.

        Environment variables:
        - MCP_BG_MAX_JOBS: Maximum concurrent jobs
        - MCP_BG_MAX_OUTPUT_SIZE: Maximum output buffer size (supports MB suffix)
        - MCP_BG_JOB_TIMEOUT: Default job timeout in seconds
        - MCP_BG_CLEANUP_INTERVAL: Cleanup interval in seconds
        - MCP_BG_ALLOWED_COMMANDS: Comma-separated allowed command patterns
        - MCP_BG_WORKING_DIR: Working directory for job execution
        """
        config_data = {}

        # Parse max jobs
        if max_jobs := os.getenv("MCP_BG_MAX_JOBS"):
            config_data["max_concurrent_jobs"] = int(max_jobs)

        # Parse max output size (support MB suffix)
        if max_output := os.getenv("MCP_BG_MAX_OUTPUT_SIZE"):
            if max_output.upper().endswith("MB"):
                config_data["max_output_size_bytes"] = (
                    int(max_output[:-2]) * 1024 * 1024
                )
            else:
                config_data["max_output_size_bytes"] = int(max_output)

        # Parse job timeout
        if job_timeout := os.getenv("MCP_BG_JOB_TIMEOUT"):
            config_data["default_job_timeout"] = int(job_timeout)

        # Parse cleanup interval
        if cleanup_interval := os.getenv("MCP_BG_CLEANUP_INTERVAL"):
            config_data["cleanup_interval_seconds"] = int(cleanup_interval)

        # Parse allowed commands
        if allowed_commands := os.getenv("MCP_BG_ALLOWED_COMMANDS"):
            config_data["allowed_command_patterns"] = allowed_commands

        # Parse working directory
        if working_dir := os.getenv("MCP_BG_WORKING_DIR"):
            config_data["working_directory"] = working_dir

        return cls(**config_data)


def load_config() -> BackgroundJobConfig:
    """Load configuration from environment variables with fallback to defaults."""
    try:
        return BackgroundJobConfig.from_environment()
    except Exception as e:
        # Log the error and return default config
        import sys

        print(
            f"Warning: Failed to load configuration from environment: {e}",
            file=sys.stderr,
        )
        print("Using default configuration", file=sys.stderr)
        return BackgroundJobConfig()

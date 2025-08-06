"""PostgreSQL CLI Commands for Automagik Hive.

This module provides CLI commands for PostgreSQL container management,
integrating with the PostgreSQL service layer for high-level operations.
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cli.core.postgres_service import PostgreSQLService


class PostgreSQLCommands:
    """PostgreSQL CLI command implementations.

    Provides user-friendly CLI commands for PostgreSQL container
    lifecycle management and workspace validation.
    """

    def __init__(self):
        self._postgres_service = None

    @property
    def postgres_service(self) -> "PostgreSQLService":
        """Lazy load PostgreSQLService only when needed."""
        if self._postgres_service is None:
            from cli.core.postgres_service import PostgreSQLService

            self._postgres_service = PostgreSQLService()
        return self._postgres_service

    def postgres_status(self, workspace_path: str | None = None) -> bool:
        """Show PostgreSQL container status.

        Args:
            workspace_path: Path to workspace (default: current directory)

        Returns:
            True if command executed successfully, False otherwise
        """
        workspace = workspace_path or "."
        workspace = str(Path(workspace).resolve())

        status = self.postgres_service.get_postgres_status(workspace)

        # Show connection info if running
        if "Running" in status:
            conn_info = self.postgres_service.get_postgres_connection_info(workspace)
            if conn_info:
                pass

        return True

    def postgres_start(self, workspace_path: str | None = None) -> bool:
        """Start PostgreSQL container.

        Args:
            workspace_path: Path to workspace (default: current directory)

        Returns:
            True if started successfully, False otherwise
        """
        workspace = workspace_path or "."
        workspace = str(Path(workspace).resolve())

        return bool(self.postgres_service.start_postgres(workspace))

    def postgres_stop(self, workspace_path: str | None = None) -> bool:
        """Stop PostgreSQL container.

        Args:
            workspace_path: Path to workspace (default: current directory)

        Returns:
            True if stopped successfully, False otherwise
        """
        workspace = workspace_path or "."
        workspace = str(Path(workspace).resolve())

        return bool(self.postgres_service.stop_postgres(workspace))

    def postgres_restart(self, workspace_path: str | None = None) -> bool:
        """Restart PostgreSQL container.

        Args:
            workspace_path: Path to workspace (default: current directory)

        Returns:
            True if restarted successfully, False otherwise
        """
        workspace = workspace_path or "."
        workspace = str(Path(workspace).resolve())

        return bool(self.postgres_service.restart_postgres(workspace))

    def postgres_logs(self, workspace_path: str | None = None, tail: int = 50) -> bool:
        """Show PostgreSQL container logs.

        Args:
            workspace_path: Path to workspace (default: current directory)
            tail: Number of lines to show

        Returns:
            True if logs displayed, False otherwise
        """
        workspace = workspace_path or "."
        workspace = str(Path(workspace).resolve())

        return self.postgres_service.show_postgres_logs(workspace, tail)

    def postgres_health(self, workspace_path: str | None = None) -> bool:
        """Check PostgreSQL health and connectivity.

        Args:
            workspace_path: Path to workspace (default: current directory)

        Returns:
            True if healthy, False otherwise
        """
        workspace = workspace_path or "."
        workspace = str(Path(workspace).resolve())

        return bool(self.postgres_service.validate_postgres_health(workspace))

    def postgres_setup(self, workspace_path: str, interactive: bool = True) -> bool:
        """Setup PostgreSQL for workspace initialization.

        Args:
            workspace_path: Path to workspace directory
            interactive: Whether to prompt for user confirmation

        Returns:
            True if setup successful, False otherwise
        """
        workspace = str(Path(workspace_path).resolve())

        return bool(self.postgres_service.setup_postgres(workspace, interactive))


# Convenience functions for direct CLI usage
def postgres_status_cmd(workspace: str | None = None) -> int:
    """CLI entry point for postgres status command."""
    commands = PostgreSQLCommands()
    success = commands.postgres_status(workspace)
    return 0 if success else 1


def postgres_start_cmd(workspace: str | None = None) -> int:
    """CLI entry point for postgres start command."""
    commands = PostgreSQLCommands()
    success = commands.postgres_start(workspace)
    return 0 if success else 1


def postgres_stop_cmd(workspace: str | None = None) -> int:
    """CLI entry point for postgres stop command."""
    commands = PostgreSQLCommands()
    success = commands.postgres_stop(workspace)
    return 0 if success else 1


def postgres_restart_cmd(workspace: str | None = None) -> int:
    """CLI entry point for postgres restart command."""
    commands = PostgreSQLCommands()
    success = commands.postgres_restart(workspace)
    return 0 if success else 1


def postgres_logs_cmd(workspace: str | None = None, tail: int = 50) -> int:
    """CLI entry point for postgres logs command."""
    commands = PostgreSQLCommands()
    success = commands.postgres_logs(workspace, tail)
    return 0 if success else 1


def postgres_health_cmd(workspace: str | None = None) -> int:
    """CLI entry point for postgres health command."""
    commands = PostgreSQLCommands()
    success = commands.postgres_health(workspace)
    return 0 if success else 1

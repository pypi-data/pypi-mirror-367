#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.7"
# dependencies = ["paramiko~=3.4", "gitpython~=3.1", "types-paramiko"]
# ///
"""
File synchronization script that supports Git projects synchronization via rsync or sftp.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Any
import re
import click
import socket
from okit.utils.log import output
from okit.core.base_tool import BaseTool
from okit.core.tool_decorator import okit_tool

# gitpython 和 paramiko 相关 import 延迟到函数内部


class SyncError(Exception):
    """Custom exception for sync related errors."""

    pass


def check_git_repo(directory: str) -> bool:
    """Check if directory is a Git repository using gitpython."""
    if not os.path.isdir(directory):
        output.error(f"Directory does not exist: {directory}")
        sys.exit(1)
    output.info(f"Checking if {directory} is a Git repository...")
    try:
        from git import Repo, InvalidGitRepositoryError

        repo = Repo(directory)
        is_repo = not repo.bare
        if is_repo:
            output.debug(f"{directory} is a valid Git repository")
        else:
            output.warning(
                f"{directory} is not a valid Git repository (bare repository)"
            )
        return is_repo
    except InvalidGitRepositoryError:
        output.warning(f"{directory} is not a Git repository")
        return False
    except Exception as e:
        output.error(f"Failed to check Git repository status for {directory}: {e}")
        return False


def get_git_changes(directory: str) -> List[str]:
    """Get list of changed files in Git repository using gitpython."""
    output.info(f"Getting Git changes for {directory}...")
    try:
        from git import Repo, GitCommandError

        repo = Repo(directory)
        changes = []

        # Get all changed files (staged and unstaged)
        for item in repo.index.diff(None):  # Unstaged changes
            if item.a_path and not item.a_path.startswith(".cursor/"):
                changes.append(item.a_path)

        for item in repo.index.diff("HEAD"):  # Staged changes
            if item.a_path and not item.a_path.startswith(".cursor/"):
                changes.append(item.a_path)

        # Get untracked files
        untracked_files = repo.untracked_files
        for file_path in untracked_files:
            if not file_path.startswith(".cursor/"):
                changes.append(file_path)

        # Remove duplicates while preserving order
        seen = set()
        unique_changes = []
        for file_path in changes:
            if file_path not in seen:
                seen.add(file_path)
                unique_changes.append(file_path)

        output.info(f"Found {len(unique_changes)} changed files in {directory}")
        return unique_changes

    except GitCommandError as e:
        output.error(f"Failed to get Git status for {directory}: {e}")
        raise SyncError(f"Failed to get Git status for {directory}: {e}")
    except Exception as e:
        output.error(f"Unexpected error getting Git changes for {directory}: {e}")
        raise SyncError(f"Unexpected error getting Git changes for {directory}: {e}")


def check_rsync_available() -> bool:
    """Check if rsync is available in the system."""
    output.info("Checking if rsync is available...")
    try:
        subprocess.run(["rsync", "--version"], capture_output=True)
        output.info("rsync is available")
        return True
    except FileNotFoundError:
        output.info("rsync is not available, will use SFTP instead")
        return False


def verify_directory_structure(
    source_dirs: List[str], remote_root: str, ssh_client: Any
) -> bool:
    """Verify if target directories exist on remote server."""
    output.info(f"Verifying target {remote_root} directories exist...")

    for directory in source_dirs:
        project_name = os.path.basename(os.path.abspath(directory))
        target_dir = f"{remote_root}/{project_name}"

        try:
            stdin, stdout, stderr = ssh_client.exec_command(f"test -d '{target_dir}'")
            if stdout.channel.recv_exit_status() != 0:
                output.error(f"Target directory {target_dir} does not exist")
                return False
            output.debug(f"Target directory {target_dir} exists")
        except Exception as e:
            output.error(f"Failed to verify directory {target_dir}: {e}")
            return False

    return True


def ensure_remote_dir(sftp: Any, remote_directory: str) -> None:
    """Ensure remote directory exists, create if necessary."""
    try:
        sftp.stat(remote_directory)
    except FileNotFoundError:
        try:
            sftp.mkdir(remote_directory)
            output.debug(f"Created remote directory: {remote_directory}")
        except Exception as e:
            output.error(f"Failed to create remote directory {remote_directory}: {e}")
            raise


def sync_via_rsync(
    source_dir: str, files: List[str], target: str, dry_run: bool
) -> None:
    # project_name = os.path.basename(os.path.abspath(source_dir))
    output.info(f"Syncing {len(files)} files via rsync to {target}")

    if not files:
        output.info("No files to sync")
        return

    # Create file list for rsync
    file_list = "\n".join(files)

    cmd = ["rsync", "-avz", "--files-from=-", "--relative", source_dir + "/", target]

    if dry_run:
        cmd.insert(1, "--dry-run")

    try:
        result = subprocess.run(cmd, input=file_list, text=True, capture_output=True)

        if result.returncode == 0:
            output.info("rsync completed successfully")
            if dry_run:
                output.result(result.stdout)
        else:
            output.error(f"rsync failed: {result.stderr}")
            raise SyncError(f"rsync failed: {result.stderr}")

    except subprocess.CalledProcessError as e:
        output.error(f"rsync command failed: {e}")
        raise SyncError(f"rsync command failed: {e}")


def sync_via_sftp(
    source_dir: str,
    files: List[str],
    sftp: Any,
    target_root: str,
    dry_run: bool,
    max_depth: int = 5,
    current_depth: int = 1,
    recursive: bool = True,
) -> None:
    # project_name = os.path.basename(os.path.abspath(source_dir))
    output.info(f"Syncing {len(files)} files via SFTP to {target_root}")

    if not files:
        output.info("No files to sync")
        return

    if current_depth > max_depth:
        output.warning(f"Maximum recursion depth {max_depth} reached")
        return

    synced_count = 0
    failed_count = 0

    for file_path in files:
        try:
            # Get relative path from source directory
            abs_file_path = os.path.join(source_dir, file_path)
            if not os.path.exists(abs_file_path):
                output.warning(f"File not found: {abs_file_path}")
                continue

            # Create target path
            target_path = f"{target_root}/{file_path}"
            target_dir = os.path.dirname(target_path)

            if not dry_run:
                # Ensure target directory exists
                try:
                    ensure_remote_dir(sftp, target_dir)
                except Exception as e:
                    output.error(f"Failed to ensure target directory {target_dir}: {e}")
                    failed_count += 1
                    continue

                # Upload file
                try:
                    sftp.put(abs_file_path, target_path)
                    synced_count += 1
                    output.debug(f"Uploaded: {file_path}")
                except Exception as e:
                    output.error(f"Failed to upload {file_path}: {e}")
                    failed_count += 1
            else:
                output.info(f"Would upload: {file_path} -> {target_path}")
                synced_count += 1

        except Exception as e:
            output.error(f"Error processing {file_path}: {e}")
            failed_count += 1

    output.info(
        f"SFTP sync completed: {synced_count} files synced, {failed_count} failed"
    )


def fix_target_root_path(target_root: str) -> str:
    # 检查是否被 git bash 转换成了 /c/Program Files/Git/xxx 或 C:/Program Files/Git/xxx 这种格式
    m = re.match(r"^(/[a-zA-Z]|[A-Z]:)/Program Files/Git(/.*)$", target_root)
    if m:
        # 还原为 /xxx
        return m.group(2)
    return target_root


@okit_tool("gitdiffsync", "Git project synchronization tool", use_subcommands=False)
class GitDiffSync(BaseTool):
    """Git 项目同步工具"""

    def __init__(self, tool_name: str, description: str = ""):
        super().__init__(tool_name, description)

    def _get_cli_help(self) -> str:
        """自定义 CLI 帮助信息"""
        return """
Git Diff Sync Tool - Synchronize changed files from Git repositories to remote servers.
        """.strip()

    def _get_cli_short_help(self) -> str:
        """自定义 CLI 简短帮助信息"""
        return "Synchronize Git project folders to remote Linux server"

    def _add_cli_commands(self, cli_group: click.Group) -> None:
        """添加工具特定的 CLI 命令"""

        # Add as main command (no subcommand)
        @cli_group.command()
        @click.option(
            "-s",
            "--source-dirs",
            multiple=True,
            required=True,
            help="Source directories to sync (must be Git repositories)",
        )
        @click.option("--host", required=True, help="Target host address")
        @click.option(
            "--port", type=int, default=22, show_default=True, help="SSH port number"
        )
        @click.option("--user", required=True, help="SSH username")
        @click.option(
            "--target-root",
            required=True,
            help="Target root directory on remote server",
        )
        @click.option(
            "--dry-run",
            is_flag=True,
            help="Show what would be transferred without actual transfer",
        )
        @click.option(
            "--max-depth",
            type=int,
            default=5,
            show_default=True,
            help="Maximum recursion depth for directory sync",
        )
        @click.option(
            "--recursive/--no-recursive",
            default=True,
            show_default=True,
            help="Enable or disable recursive directory sync",
        )
        def main(
            source_dirs: tuple,
            host: str,
            port: int,
            user: str,
            target_root: str,
            dry_run: bool,
            max_depth: int,
            recursive: bool,
        ) -> None:
            """Synchronize Git project folders to remote Linux server."""
            # Convert tuple to list for compatibility
            source_dirs_list = list(source_dirs)
            self._execute_sync(
                source_dirs_list,
                host,
                port,
                user,
                target_root,
                dry_run,
                max_depth,
                recursive,
            )

    def _execute_sync(
        self,
        source_dirs: List[str],
        host: str,
        port: int,
        user: str,
        target_root: str,
        dry_run: bool,
        max_depth: int,
        recursive: bool,
    ) -> None:
        """Execute the sync operation"""
        try:
            output.info(
                f"Executing sync command, source_dirs: {source_dirs}, host: {host}, target_root: {target_root}, dry_run: {dry_run}"
            )

            import paramiko  # type: ignore
            from paramiko.ssh_exception import AuthenticationException, SSHException  # type: ignore

            target_root = fix_target_root_path(target_root)

            output.debug(f"Source directories: {source_dirs}")
            output.debug(f"Target root: {target_root}")

            if dry_run:
                output.info("Running in dry-run mode")

            output.debug("Verifying Git repositories...")
            for directory in source_dirs:
                if not check_git_repo(directory):
                    output.error(f"Error: {directory} is not a Git repository")
                    sys.exit(1)
                else:
                    output.debug(f"Git repository verified: {directory}")

            output.debug(f"Setting up SSH connection to {host}...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # SSH connection
            with ssh:
                try:
                    ssh.connect(host, port=port, username=user)
                    output.info("SSH connection established successfully")
                except AuthenticationException as e:
                    output.error(f"SSH authentication failed: {str(e)}")
                    sys.exit(1)
                except SSHException as e:
                    output.error(f"SSH connection failed: {str(e)}")
                    sys.exit(1)
                except Exception as e:
                    output.error(f"Unexpected SSH error: {str(e)}")
                    sys.exit(1)

                # Perform synchronization
                output.success(f"Synchronizing {len(source_dirs)} directories...")
                
                for directory in source_dirs:
                    try:
                        output.info(f"Processing directory: {directory}")
                        changes = get_git_changes(directory)
                        if not changes:
                            output.info(f"No changes in {directory}")
                            continue

                        output.info(f"Synchronizing {directory}...")
                        
                        # Determine sync method
                        use_rsync = check_rsync_available()
                        if use_rsync:
                            sync_via_rsync(
                                directory,
                                changes,
                                f"{user}@{host}:{target_root}",
                                dry_run,
                            )
                        else:
                            try:
                                sftp = ssh.open_sftp()
                                sync_via_sftp(
                                    directory,
                                    changes,
                                    sftp,
                                    target_root,
                                    dry_run,
                                    max_depth,
                                    1,
                                    recursive,
                                )
                                sftp.close()
                            except Exception as sftp_error:
                                output.error(f"SFTP error: {sftp_error}")
                                output.error(f"SFTP error: {sftp_error}")
                                continue

                    except Exception as e:
                        output.error(f"Error processing {directory}: {e}")
                        output.error(f"Error processing {directory}: {e}")
                        continue

        except Exception as e:
            output.error(f"Unexpected error: {e}")
            output.error(f"Unexpected error: {e}")
            sys.exit(1)

    def _cleanup_impl(self) -> None:
        """自定义清理逻辑"""
        output.info("Executing custom cleanup logic")
        pass

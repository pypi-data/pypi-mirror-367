from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, field_validator

from .. import SolveigConfig, plugins, utils
from ..plugins.exceptions import PluginException, ProcessingError, ValidationError

if TYPE_CHECKING:
    from .result import CommandResult, ReadResult, RequirementResult, WriteResult
else:
    # Runtime imports - needed for instantiation
    from .result import CommandResult, ReadResult, WriteResult


# Base class for things the LLM can request
class Requirement(BaseModel):
    """
    Important: all statements that have side-effects (prints, network, filesystem operations)
    must be inside separate methods that can be mocked in a MockRequirement class for tests
    """

    comment: str

    @field_validator("comment", mode="before")
    @classmethod
    def strip_name(cls, comment):
        return comment.strip()

    def _print(self, config):
        raise NotImplementedError()

    def solve(self, config):
        self._print(config)

        # Run before hooks - they validate and can throw exceptions
        for before_hook, requirements in plugins.hooks.HOOKS.before:
            if not requirements or any(
                isinstance(self, requirement_type) for requirement_type in requirements
            ):
                try:
                    before_hook(config, self)
                except ValidationError as e:
                    # Plugin validation failed - return appropriate error result
                    return self._create_error_result(
                        f"Pre-processing failed: {e}", accepted=False
                    )
                except PluginException as e:
                    # Other plugin error - return appropriate error result
                    return self._create_error_result(
                        f"Plugin error: {e}", accepted=False
                    )

        # Run the actual requirement solving
        result = self._actually_solve(config)

        # Run after hooks - they can process/modify result or throw exceptions
        for after_hook, requirements in plugins.hooks.HOOKS.after:
            if not requirements or any(
                isinstance(self, requirement_type) for requirement_type in requirements
            ):
                try:
                    after_hook(config, self, result)
                except ProcessingError as e:
                    # Plugin processing failed - return error result
                    return self._create_error_result(
                        f"Post-processing failed: {e}", accepted=result.accepted
                    )
                except PluginException as e:
                    # Other plugin error - return error result
                    return self._create_error_result(
                        f"Plugin error: {e}", accepted=result.accepted
                    )

        return result

    def _actually_solve(self, config) -> RequirementResult:
        raise NotImplementedError()

    def _create_error_result(
        self, error_message: str, accepted: bool
    ) -> RequirementResult:
        """Create appropriate error result for this requirement type."""
        raise NotImplementedError()


class FileRequirement(Requirement):
    path: str

    # Idk if I'm keeping this or how it fits into the current explicit permissions
    # def is_possible(self, config: SolveigConfig) -> bool:
    #     possible = False
    #     for path in config.allowed_paths:
    #         if Path(self.path).is_relative_to(path):
    #             if path.mode == "n":
    #                 return False
    #             elif self.mode_allowed(path.mode):
    #                 possible = True
    #     return possible
    #
    # @staticmethod
    # def mode_allowed(mode: str) -> bool:
    #     raise NotImplementedError()


class ReadRequirement(FileRequirement):
    only_read_metadata: bool

    def _print(self, config):
        abs_path = Path(self.path).expanduser().resolve()
        is_dir = abs_path.is_dir()
        print("  [ Read ]")
        print(f'    comment: "{self.comment}"')
        print(f"    path: {self.path} ({'directory' if is_dir else 'file'})")

    def _create_error_result(self, error_message: str, accepted: bool) -> ReadResult:
        """Create ReadResult with error."""
        return ReadResult(requirement=self, accepted=accepted, error=error_message)

    def _validate_read_access(self, path: str) -> None:
        """Validate read access to path (OS interaction - can be mocked)."""
        utils.file.validate_read_access(path)

    def _read_file_with_metadata(self, path: str, include_content: bool = True) -> dict:
        """Read file with metadata (OS interaction - can be mocked)."""
        return utils.file.read_file_with_metadata(path, include_content=include_content)

    def _ask_directory_consent(self) -> bool:
        """Ask user consent for directory reading (user interaction - can be mocked)."""
        return utils.misc.ask_yes(
            "    ? Allow reading directory listing and metadata? [y/N]: "
        )

    def _ask_file_read_choice(self) -> str:
        """Ask user what type of file read to perform (user interaction - can be mocked)."""
        return (
            input(
                "    ? Allow reading file? [y=content+metadata / m=metadata / N=skip]: "
            )
            .strip()
            .lower()
        )

    def _ask_final_consent(self, has_content: bool) -> bool:
        """Ask final consent to send data (user interaction - can be mocked)."""
        return utils.misc.ask_yes(
            f"    ? Allow sending {'file content and ' if has_content else ''}metadata? [y/N]: "
        )

    def _actually_solve(self, config) -> ReadResult:
        abs_path = Path(self.path).expanduser().resolve()
        is_dir = abs_path.is_dir()

        # Pre-flight validation
        try:
            self._validate_read_access(self.path)
        except (FileNotFoundError, PermissionError) as e:
            print(f"    Skipping - {e}")
            return ReadResult(requirement=self, accepted=False, error=str(e))

        # Handle user interaction for different read types
        if is_dir:
            if self._ask_directory_consent():
                try:
                    file_data = self._read_file_with_metadata(
                        self.path, include_content=False
                    )
                    return ReadResult(
                        requirement=self,
                        accepted=True,
                        metadata=file_data["metadata"],
                        directory_listing=file_data["directory_listing"],
                    )
                except (PermissionError, OSError) as e:
                    return ReadResult(requirement=self, accepted=False, error=str(e))
            else:
                return ReadResult(requirement=self, accepted=False)
        else:
            # File reading with user choices
            # TODO: print the file size here so the user can have some idea of how much data they're sending
            choice_read_file = self._ask_file_read_choice()

            if choice_read_file not in {"m", "y"}:
                return ReadResult(requirement=self, accepted=False)

            # Read metadata first
            try:
                file_data = self._read_file_with_metadata(
                    self.path, include_content=False
                )
            except (PermissionError, OSError) as e:
                return ReadResult(requirement=self, accepted=False, error=str(e))

            print("    [ Metadata ]")
            print(
                utils.misc.format_output(
                    json.dumps(file_data["metadata"]),
                    indent=6,
                    max_lines=config.max_output_lines,
                    max_chars=config.max_output_size,
                )
            )

            content = encoding = None
            if choice_read_file == "y":
                # Read content
                try:
                    file_data = self._read_file_with_metadata(
                        self.path, include_content=True
                    )
                    content = file_data["content"]
                    encoding = file_data["encoding"]
                except (PermissionError, OSError, UnicodeDecodeError) as e:
                    return ReadResult(requirement=self, accepted=False, error=str(e))

                print("    [ Content ]")
                print(
                    "      (Base64)"
                    if encoding == "base64"
                    else utils.misc.format_output(
                        content,
                        indent=6,
                        max_lines=config.max_output_lines,
                        max_chars=config.max_output_size,
                    )
                )

            # Final consent check
            if self._ask_final_consent(content is not None):
                return ReadResult(
                    requirement=self,
                    accepted=True,
                    metadata=file_data["metadata"],
                    content=content,
                    content_encoding=encoding,
                )
            else:
                return ReadResult(requirement=self, accepted=False)


class WriteRequirement(FileRequirement):
    is_directory: bool
    content: str | None = None

    def _print(self, config):
        abs_path = Path(self.path).expanduser().resolve()

        print("  [ Write ]")
        print(f'    comment: "{self.comment}"')
        # TODO also list real path if it's different from the LLM's path (and also for ReadRequirement)
        print(f"    path: {self.path} ({'directory' if self.is_directory else 'file'})")
        print(f"    real path: {abs_path}")
        if self.content:
            print("      [ Content ]")
            formatted_content = utils.misc.format_output(
                self.content,
                indent=8,
                max_lines=config.max_output_lines,
                max_chars=config.max_output_size,
            )
            # TODO: make this print optional, or in a `less`-like window, or it will get messy
            print(formatted_content)

    def _create_error_result(self, error_message: str, accepted: bool) -> WriteResult:
        """Create WriteResult with error."""
        return WriteResult(requirement=self, accepted=accepted, error=error_message)

    def _resolve_path(self, path: str) -> Path:
        """Resolve path (OS interaction - can be mocked)."""
        return Path(path).expanduser().resolve()

    def _path_exists(self, abs_path: Path) -> bool:
        """Check if path exists (OS interaction - can be mocked)."""
        return abs_path.exists()

    def _ask_write_consent(self, operation_type: str, content_desc: str) -> bool:
        """Ask user consent for write operation (user interaction - can be mocked)."""
        return utils.misc.ask_yes(
            f"    ? Allow writing {operation_type}{content_desc}? [y/N]: "
        )

    def _validate_write_access(self, config: SolveigConfig) -> None:
        """Validate write access (OS interaction - can be mocked)."""
        utils.file.validate_write_access(
            file_path=self.path,
            is_directory=self.is_directory,
            content=self.content,
            min_disk_size_left=config.min_disk_space_left,
        )

    def _write_file_or_directory(
        self, path: str, is_directory: bool, content: str
    ) -> None:
        """Write file or directory (OS interaction - can be mocked)."""
        utils.file.write_file_or_directory(path, is_directory, content)

    def _actually_solve(self, config: SolveigConfig) -> WriteResult:
        abs_path = self._resolve_path(self.path)

        # Show warning if path exists
        if self._path_exists(abs_path):
            print("    ! Warning: this path already exists !")

        # Get user consent before attempting operation
        operation_type = "directory" if self.is_directory else "file"
        content_desc = " and contents" if not self.is_directory and self.content else ""

        if self._ask_write_consent(operation_type, content_desc):
            try:
                # Validate write access first
                self._validate_write_access(config)

                # Perform the write operation
                content = self.content if self.content else ""
                self._write_file_or_directory(self.path, self.is_directory, content)

                return WriteResult(requirement=self, accepted=True)

            except FileExistsError as e:
                return WriteResult(requirement=self, accepted=False, error=str(e))
            except PermissionError as e:
                return WriteResult(requirement=self, accepted=False, error=str(e))
            except OSError as e:
                return WriteResult(requirement=self, accepted=False, error=str(e))
            except UnicodeEncodeError as e:
                return WriteResult(
                    requirement=self, accepted=False, error=f"Encoding error: {e}"
                )
        else:
            return WriteResult(requirement=self, accepted=False)


class CommandRequirement(Requirement):
    command: str

    def _print(self, config):
        print("  [ Command ]")
        print(f'    comment: "{self.comment}"')
        print(f"    command: {self.command}")

    def _create_error_result(self, error_message: str, accepted: bool) -> CommandResult:
        """Create CommandResult with error."""
        return CommandResult(
            requirement=self, accepted=accepted, success=False, error=error_message
        )

    def _ask_run_consent(self) -> bool:
        """Ask user consent for running command (user interaction - can be mocked)."""
        return utils.misc.ask_yes("    ? Allow running command? [y/N]: ")

    def _execute_command(self, command: str) -> tuple[str | None, str | None]:
        """Execute command and return stdout, stderr (OS interaction - can be mocked)."""
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=10
        )
        output = result.stdout.strip() if result.stdout else None
        error = result.stderr.strip() if result.stderr else None
        return output, error

    def _ask_output_consent(self) -> bool:
        """Ask user consent for sending output (user interaction - can be mocked)."""
        return utils.misc.ask_yes("    ? Allow sending output? [y/N]: ")

    def _actually_solve(self, config) -> CommandResult:
        if self._ask_run_consent():
            # TODO review the whole 'accepted' thing. If I run a command, but don't send the output,
            #  that's confusing and should be differentiated from not running the command at all.
            #  or if anything at all is refused, maybe just say that in the error
            try:
                output, error = self._execute_command(self.command)
            except Exception as e:
                error_str = str(e)
                print(error_str)
                return CommandResult(
                    requirement=self, accepted=True, success=False, error=error_str
                )

            if output:
                print("    [ Output ]")
                print(
                    utils.misc.format_output(
                        output,
                        indent=6,
                        max_lines=config.max_output_lines,
                        max_chars=config.max_output_size,
                    )
                )
            else:
                print("    [ No Output ]")
            if error:
                print("    [ Error ]")
                print(
                    utils.misc.format_output(
                        error,
                        indent=6,
                        max_lines=config.max_output_lines,
                        max_chars=config.max_output_size,
                    )
                )
            if not self._ask_output_consent():
                output = None
                error = None
            return CommandResult(
                requirement=self,
                accepted=True,
                success=True,
                stdout=output,
                error=error,
            )
        return CommandResult(requirement=self, accepted=False)

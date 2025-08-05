"""File adapter for abstracting file system operations."""

import json
import logging
import shutil
from pathlib import Path
from typing import Any

from glovebox.core.errors import FileSystemError
from glovebox.protocols.file_adapter_protocol import FileAdapterProtocol
from glovebox.utils.error_utils import create_file_error


logger = logging.getLogger(__name__)


class FileAdapter:
    """File system adapter implementation."""

    def read_text(self, path: Path, encoding: str = "utf-8") -> str:
        """Read text content from a file."""
        try:
            with path.open(mode="r", encoding=encoding) as f:
                content = f.read()
            return content
        except FileNotFoundError as e:
            error = create_file_error(path, "read_text", e, {"encoding": encoding})
            logger.error("File not found: %s", path)
            raise error from e
        except PermissionError as e:
            error = create_file_error(path, "read_text", e, {"encoding": encoding})
            logger.error("Permission denied reading file: %s", path)
            raise error from e
        except UnicodeDecodeError as e:
            error = create_file_error(path, "read_text", e, {"encoding": encoding})
            logger.error("Encoding error reading file %s: %s", path, e)
            raise error from e
        except Exception as e:
            error = create_file_error(path, "read_text", e, {"encoding": encoding})
            logger.error("Error reading file %s: %s", path, e)
            raise error from e

    def write_text(self, path: Path, content: str, encoding: str = "utf-8") -> None:
        """Write text content to a file."""
        try:
            # Ensure parent directory exists
            self.create_directory(path.parent)

            with path.open(mode="w", encoding=encoding) as f:
                f.write(content)
        except PermissionError as e:
            error = create_file_error(
                path,
                "write_text",
                e,
                {"encoding": encoding, "content_length": len(content)},
            )
            logger.error("Permission denied writing file: %s", path)
            raise error from e
        except Exception as e:
            error = create_file_error(
                path,
                "write_text",
                e,
                {"encoding": encoding, "content_length": len(content)},
            )
            logger.error("Error writing file %s: %s", path, e)
            raise error from e

    def read_binary(self, path: Path) -> bytes:
        """Read binary content from a file."""
        try:
            with path.open(mode="rb") as f:
                content = f.read()
            return content
        except FileNotFoundError as e:
            error = create_file_error(path, "read_binary", e, {})
            logger.error("File not found: %s", path)
            raise error from e
        except PermissionError as e:
            error = create_file_error(path, "read_binary", e, {})
            logger.error("Permission denied reading file: %s", path)
            raise error from e
        except Exception as e:
            error = create_file_error(path, "read_binary", e, {})
            logger.error("Error reading binary file %s: %s", path, e)
            raise error from e

    def write_binary(self, path: Path, content: bytes) -> None:
        """Write binary content to a file."""
        try:
            # Ensure parent directory exists
            self.create_directory(path.parent)

            with path.open(mode="wb") as f:
                f.write(content)
        except PermissionError as e:
            error = create_file_error(
                path,
                "write_binary",
                e,
                {"content_length": len(content)},
            )
            logger.error("Permission denied writing file: %s", path)
            raise error from e
        except Exception as e:
            error = create_file_error(
                path,
                "write_binary",
                e,
                {"content_length": len(content)},
            )
            logger.error("Error writing binary file %s: %s", path, e)
            raise error from e

    def read_json(self, path: Path, encoding: str = "utf-8") -> dict[str, Any]:
        """Read and parse JSON content from a file.

        This method reads and parses a JSON file, returning the data as a dictionary.
        It preserves the original field names to ensure compatibility with Pydantic models
        that use field aliases.
        """
        try:
            content = self.read_text(path, encoding)
            data = json.loads(content)
            return data if isinstance(data, dict) else {"data": data}
        except json.JSONDecodeError as e:
            error = create_file_error(path, "read_json", e, {"encoding": encoding})
            logger.error("Invalid JSON in file %s: %s", path, e)
            raise error from e
        except FileSystemError:
            # Let FileSystemError from read_text pass through
            raise
        except Exception as e:
            error = create_file_error(path, "read_json", e, {"encoding": encoding})
            logger.error("Error reading JSON file %s: %s", path, e)
            raise error from e

    def write_json(
        self,
        path: Path,
        data: dict[str, Any],
        encoding: str = "utf-8",
        indent: int = 2,
        encoder_cls: type[json.JSONEncoder] = json.JSONEncoder,
    ) -> None:
        """Write data as JSON to a file.

        Args:
            path: Path to write the file
            data: Dictionary data to serialize
            encoding: File encoding
            indent: JSON indentation level
            encoder_cls: JSON encoder class to use for serialization
        """
        try:
            content = json.dumps(
                data, indent=indent, ensure_ascii=False, cls=encoder_cls
            )
            self.write_text(path, content, encoding)
        except TypeError as e:
            error = create_file_error(
                path,
                "write_json",
                e,
                {
                    "encoding": encoding,
                    "indent": indent,
                    "data_type": type(data).__name__,
                },
            )
            logger.error("Cannot serialize data to JSON for file %s: %s", path, e)
            raise error from e
        except FileSystemError:
            # Let FileSystemError from write_text pass through
            raise
        except Exception as e:
            error = create_file_error(
                path,
                "write_json",
                e,
                {
                    "encoding": encoding,
                    "indent": indent,
                    "data_type": type(data).__name__,
                },
            )
            logger.error("Error writing JSON file %s: %s", path, e)
            raise error from e

    def check_exists(self, path: Path) -> bool:
        """Check if a path exists."""
        return path.exists()

    def is_file(self, path: Path) -> bool:
        """Check if a path is a file."""
        return path.is_file()

    def is_dir(self, path: Path) -> bool:
        """Check if a path is a directory."""
        return path.is_dir()

    def create_directory(
        self, path: Path, parents: bool = True, exist_ok: bool = True
    ) -> None:
        """Create a directory."""
        try:
            path.mkdir(parents=parents, exist_ok=exist_ok)
        except PermissionError as e:
            error = create_file_error(
                path, "mkdir", e, {"parents": parents, "exist_ok": exist_ok}
            )
            logger.error("Permission denied creating directory: %s", path)
            raise error from e
        except Exception as e:
            error = create_file_error(
                path, "mkdir", e, {"parents": parents, "exist_ok": exist_ok}
            )
            logger.error("Error creating directory %s: %s", path, e)
            raise error from e

    def copy_file(self, src: Path, dst: Path) -> None:
        """Copy a file from source to destination."""
        try:
            # Ensure destination directory exists
            self.create_directory(dst.parent)

            shutil.copy2(src, dst)
        except FileNotFoundError as e:
            error = create_file_error(
                src, "copy_file", e, {"source": str(src), "destination": str(dst)}
            )
            logger.error("Source file not found: %s", src)
            raise error from e
        except PermissionError as e:
            error = create_file_error(
                src, "copy_file", e, {"source": str(src), "destination": str(dst)}
            )
            logger.error("Permission denied copying file: %s -> %s", src, dst)
            raise error from e
        except FileSystemError:
            # Let FileSystemError from mkdir pass through
            raise
        except Exception as e:
            error = create_file_error(
                src, "copy_file", e, {"source": str(src), "destination": str(dst)}
            )
            logger.error("Error copying file %s to %s: %s", src, dst, e)
            raise error from e

    def list_files(self, path: Path, pattern: str = "*") -> list[Path]:
        """List files in a directory matching a pattern."""
        try:
            if not self.is_dir(path):
                error = create_file_error(
                    path,
                    "list_files",
                    ValueError("Not a directory"),
                    {"pattern": pattern},
                )
                logger.error("Path is not a directory: %s", path)
                raise error

            files = list(path.glob(pattern))
            files = [f for f in files if f.is_file()]
            return files
        except FileSystemError:
            # Let FileSystemError pass through
            raise
        except Exception as e:
            error = create_file_error(path, "list_files", e, {"pattern": pattern})
            logger.error("Error listing files in %s: %s", path, e)
            raise error from e

    def list_directory(self, path: Path) -> list[Path]:
        """List all items in a directory."""
        try:
            if not self.is_dir(path):
                error = create_file_error(
                    path, "list_directory", ValueError("Not a directory"), {}
                )
                logger.error("Path is not a directory: %s", path)
                raise error

            items = list(path.iterdir())
            return items
        except FileSystemError:
            # Let FileSystemError pass through
            raise
        except Exception as e:
            error = create_file_error(path, "list_directory", e, {})
            logger.error("Error listing directory %s: %s", path, e)
            raise error from e

    def check_overwrite_permission(self, files: list[Path]) -> bool:
        """Check if user permits overwriting existing files."""
        existing_files = [f for f in files if self.check_exists(f)]
        if not existing_files:
            return True

        print("\nWarning: The following output files already exist:")
        for f in existing_files:
            print(f" - {f}")

        try:
            response = (
                input("Do you want to overwrite these files? (y/N): ").strip().lower()
            )
        except EOFError:
            print(
                "\nNon-interactive environment detected. Assuming 'No' for overwrite."
            )
            response = "n"

        if response == "y":
            return True
        else:
            logger.warning("Operation cancelled by user (or non-interactive 'No').")
            return False

    def remove_file(self, path: Path) -> None:
        """Remove a file. Does not raise error if file not found."""
        try:
            # missing_ok=True ensures no FileNotFoundError is raised if the path doesn't exist.
            path.unlink(missing_ok=True)
        except PermissionError as e:
            error = create_file_error(path, "remove_file", e, {})
            logger.error("Permission denied removing file: %s", path)
            raise error from e
        except Exception as e:
            # Catch other potential errors like IsADirectoryError
            error = create_file_error(path, "remove_file", e, {})
            logger.error("Error removing file %s: %s", path, e)
            raise error from e

    def remove_dir(self, path: Path, recursive: bool = True) -> None:
        """Remove a directory and optionally its contents.

        Uses shutil.rmtree for recursive removal or path.rmdir for empty directory removal.

        Args:
            path: Path to the directory to remove
            recursive: Whether to recursively remove contents (True) or only if empty (False)

        Raises:
            GloveboxError: If directory cannot be removed
        """
        try:
            if not self.check_exists(path):
                return

            if not self.is_dir(path):
                error = create_file_error(
                    path,
                    "remove_dir",
                    ValueError("Not a directory"),
                    {"recursive": recursive},
                )
                logger.error("Path is not a directory: %s", path)
                raise error

            if recursive:
                shutil.rmtree(path)
            else:
                # This will only work if the directory is empty
                path.rmdir()

        except PermissionError as e:
            error = create_file_error(path, "remove_dir", e, {"recursive": recursive})
            logger.error("Permission denied removing directory: %s", path)
            raise error from e
        except OSError as e:
            error = create_file_error(path, "remove_dir", e, {"recursive": recursive})
            logger.error("OS error removing directory %s: %s", path, e)
            raise error from e
        except Exception as e:
            error = create_file_error(path, "remove_dir", e, {"recursive": recursive})
            logger.error("Error removing directory %s: %s", path, e)
            raise error from e

    def create_timestamped_backup(self, file_path: Path) -> Path | None:
        """Create a timestamped backup of a file."""
        try:
            if not self.is_file(file_path):
                return None

            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_path = file_path.with_suffix(f"{file_path.suffix}.{timestamp}.bak")

            self.copy_file(file_path, backup_path)
            return backup_path
        except Exception as e:
            error = create_file_error(file_path, "create_timestamped_backup", e, {})
            logger.error("Failed to create backup of %s: %s", file_path, e)
            return None

    def get_file_size(self, path: Path) -> int:
        """Get file size safely with proper error handling.

        Args:
            path: Path to file

        Returns:
            int: File size in bytes

        Raises:
            FileSystemError: If file cannot be accessed or sized
        """
        try:
            file_size = path.stat().st_size
            return file_size
        except FileNotFoundError as e:
            error = create_file_error(path, "get_file_size", e)
            logger.error("File not found: %s", path)
            raise error from e
        except PermissionError as e:
            error = create_file_error(path, "get_file_size", e)
            logger.error("Permission denied accessing file: %s", path)
            raise error from e
        except Exception as e:
            error = create_file_error(path, "get_file_size", e)
            logger.error("Error getting file size %s: %s", path, e)
            raise error from e

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize a string for use as a filename."""
        try:
            # Replace invalid filename characters with underscores
            safe_name = "".join(
                c if c.isalnum() or c in ["-", "_", "."] else "_" for c in filename
            )

            # Ensure the name isn't empty
            if not safe_name:
                safe_name = "unnamed"

            return safe_name
        except Exception as e:
            logger.error("Error sanitizing filename '%s': %s", filename, e)
            return "unnamed"


def create_file_adapter() -> FileAdapterProtocol:
    """Create a file adapter with default implementation."""
    return FileAdapter()

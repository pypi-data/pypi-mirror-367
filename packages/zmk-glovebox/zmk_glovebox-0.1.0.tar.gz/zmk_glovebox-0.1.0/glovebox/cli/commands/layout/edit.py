"""Unified layout editing command with atomic operations."""

import json
import logging
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console

from glovebox.adapters import create_file_adapter
from glovebox.cli.commands.layout.base import BaseLayoutCommand
from glovebox.cli.decorators import handle_errors, with_metrics
from glovebox.cli.helpers.auto_profile import resolve_json_file_path
from glovebox.cli.helpers.parameters import (
    JsonFileArgument,
    OutputFormatOption,
    complete_field_paths,
)
from glovebox.layout.models import LayoutBinding, LayoutData
from glovebox.layout.utils.field_parser import (
    extract_field_value_from_model,
    set_field_value_on_model,
)
from glovebox.layout.utils.json_operations import (
    VariableResolutionContext,
    load_layout_file,
)
from glovebox.layout.utils.layer_references import (
    create_layer_mapping_for_add,
    create_layer_mapping_for_move,
    create_layer_mapping_for_remove,
    update_layer_references,
)
from glovebox.layout.utils.variable_resolver import VariableResolver


logger = logging.getLogger(__name__)
console = Console()


class LayoutEditor:
    """Atomic layout editor that performs all operations in memory."""

    def __init__(self, layout_data: LayoutData):
        """Initialize editor with layout data.

        Args:
            layout_data: The layout data to edit
        """
        self.layout_data = layout_data
        self.operations_log: list[str] = []
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def get_field(self, field_path: str) -> Any:
        """Get field value.

        Args:
            field_path: Dot notation path to field

        Returns:
            Field value

        Raises:
            ValueError: If field not found
        """
        try:
            return extract_field_value_from_model(self.layout_data, field_path)
        except Exception as e:
            raise ValueError(f"Cannot get field '{field_path}': {e}") from e

    def set_field(self, field_path: str, value: Any) -> None:
        """Set field value.

        Args:
            field_path: Dot notation path to field
            value: Value to set

        Raises:
            ValueError: If field cannot be set
        """
        try:
            set_field_value_on_model(self.layout_data, field_path, value)
            self.operations_log.append(f"Set {field_path} = {value}")
        except Exception as e:
            raise ValueError(f"Cannot set field '{field_path}': {e}") from e

    def unset_field(self, field_path: str) -> None:
        """Remove field or dictionary key.

        Args:
            field_path: Dot notation path to field

        Raises:
            ValueError: If field cannot be removed
        """
        try:
            parts = field_path.split(".")
            if len(parts) == 1:
                # Top-level field
                if hasattr(self.layout_data, parts[0]):
                    delattr(self.layout_data, parts[0])
                else:
                    raise ValueError(f"Field '{parts[0]}' not found")
            else:
                # Nested field - get parent and remove key
                parent_path = ".".join(parts[:-1])
                key = parts[-1]
                parent = extract_field_value_from_model(self.layout_data, parent_path)

                if isinstance(parent, dict) and key in parent:
                    del parent[key]
                elif isinstance(parent, list) and key.isdigit():
                    parent.pop(int(key))
                else:
                    raise ValueError(f"Cannot unset '{key}' from '{parent_path}'")

            self.operations_log.append(f"Unset {field_path}")
        except Exception as e:
            raise ValueError(f"Cannot unset field '{field_path}': {e}") from e

    def merge_field(self, field_path: str, merge_data: dict[str, Any]) -> None:
        """Merge dictionary into field.

        Args:
            field_path: Dot notation path to field
            merge_data: Dictionary to merge

        Raises:
            ValueError: If merge fails
        """
        try:
            current = self.get_field(field_path)
            if not isinstance(current, dict):
                raise ValueError(f"Field '{field_path}' is not a dictionary")

            merged = deep_merge_dicts(current, merge_data)
            self.set_field(field_path, merged)
            self.operations_log[-1] = f"Merged into {field_path}"
        except Exception as e:
            raise ValueError(f"Cannot merge into field '{field_path}': {e}") from e

    def append_field(self, field_path: str, value: Any) -> None:
        """Append value to array field.

        Args:
            field_path: Dot notation path to field
            value: Value to append

        Raises:
            ValueError: If append fails
        """
        try:
            current = self.get_field(field_path)
            if not isinstance(current, list):
                raise ValueError(f"Field '{field_path}' is not an array")

            if isinstance(value, list):
                current.extend(value)
            else:
                current.append(value)

            self.operations_log.append(f"Appended to {field_path}")
        except Exception as e:
            raise ValueError(f"Cannot append to field '{field_path}': {e}") from e

    def add_layer(self, layer_name: str, layer_data: list[Any] | None = None) -> None:
        """Add new layer.

        Args:
            layer_name: Name of new layer
            layer_data: Optional layer data (creates empty if None)

        Raises:
            ValueError: If layer already exists
        """
        if layer_name in self.layout_data.layer_names:
            raise ValueError(f"Layer '{layer_name}' already exists")

        # Track original layer count before adding
        original_count = len(self.layout_data.layer_names)
        position = original_count  # Adding at the end

        # Add the layer
        self.layout_data.layer_names.append(layer_name)
        self.layout_data.layers.append(layer_data or [])

        # Update layer references
        layer_mapping = create_layer_mapping_for_add(original_count, position)
        self.layout_data, ref_warnings = update_layer_references(
            self.layout_data, layer_mapping
        )
        self.warnings.extend(ref_warnings)

        self.operations_log.append(f"Added layer '{layer_name}'")

    def remove_layer(self, layer_identifier: str) -> None:
        """Remove layer(s) by name, index, or regex pattern.

        Args:
            layer_identifier: Layer identifier - can be:
                - Layer name (exact match)
                - Index (0-based, e.g., "0", "15")
                - Regex pattern (e.g., "Mouse.*", "Mouse*", ".*Index")

        Raises:
            ValueError: If no layers found or invalid identifier
        """
        import re

        # Find layers to remove based on identifier type
        layers_to_remove: list[dict[str, Any]] = []

        # Try to parse as integer index first
        try:
            index = int(layer_identifier)
            if 0 <= index < len(self.layout_data.layer_names):
                layers_to_remove.append(
                    {"name": self.layout_data.layer_names[index], "index": index}
                )
        except ValueError:
            # Not an integer, continue with name/pattern matching
            pass

        if not layers_to_remove:
            # Check for exact layer name match first
            for i, layer_name in enumerate(self.layout_data.layer_names):
                if layer_name == layer_identifier:
                    layers_to_remove.append({"name": layer_name, "index": i})
                    break

        if not layers_to_remove:
            # Try regex pattern matching
            try:
                # Convert shell-style wildcards to regex if needed
                pattern = layer_identifier
                if "*" in pattern and not any(c in pattern for c in "[]{}()^$+?\\|"):
                    # Simple wildcard pattern - convert to regex
                    pattern = pattern.replace("*", ".*")

                # Compile regex pattern
                regex = re.compile(pattern)

                # Find all matching layers
                for i, layer_name in enumerate(self.layout_data.layer_names):
                    if regex.match(layer_name):
                        layers_to_remove.append({"name": layer_name, "index": i})

            except re.error:
                # Invalid regex pattern - no matches
                pass

        if not layers_to_remove:
            # No matches found - log warning but don't raise error for better UX
            available_layers = ", ".join(self.layout_data.layer_names)
            warning_msg = f"No layers found matching identifier '{layer_identifier}'. Available layers: {available_layers}"
            self.warnings.append(warning_msg)
            return

        # Sort by index in descending order to remove from end to start
        # This prevents index shifting issues
        layers_to_remove.sort(key=lambda x: x["index"], reverse=True)

        # Track original layer count and indices being removed
        original_count = len(self.layout_data.layer_names)
        removed_indices = [layer_info["index"] for layer_info in layers_to_remove]

        removed_names: list[str] = []
        for layer_info in layers_to_remove:
            idx = layer_info["index"]
            name = layer_info["name"]

            # Remove layer name and bindings
            self.layout_data.layer_names.pop(idx)
            if idx < len(self.layout_data.layers):
                self.layout_data.layers.pop(idx)

            removed_names.append(name)

        # Update layer references
        layer_mapping = create_layer_mapping_for_remove(original_count, removed_indices)
        self.layout_data, ref_warnings = update_layer_references(
            self.layout_data, layer_mapping
        )
        self.warnings.extend(ref_warnings)

        # Log the operation
        if removed_names:
            self.operations_log.append(f"Removed layers: {', '.join(removed_names)}")

    def move_layer(self, layer_name: str, new_position: int) -> None:
        """Move layer to new position.

        Args:
            layer_name: Layer name to move
            new_position: Target position

        Raises:
            ValueError: If layer not found or position invalid
        """
        if layer_name not in self.layout_data.layer_names:
            raise ValueError(f"Layer '{layer_name}' not found")

        old_index = self.layout_data.layer_names.index(layer_name)
        if new_position < 0 or new_position >= len(self.layout_data.layers):
            raise ValueError(f"Invalid position {new_position}")

        # Track original positions before moving
        original_count = len(self.layout_data.layer_names)

        # Remove from old position
        layer_name = self.layout_data.layer_names.pop(old_index)
        layer_data = self.layout_data.layers.pop(old_index)

        # Insert at new position
        self.layout_data.layer_names.insert(new_position, layer_name)
        self.layout_data.layers.insert(new_position, layer_data)

        # Update layer references
        layer_mapping = create_layer_mapping_for_move(
            original_count, old_index, new_position
        )
        self.layout_data, ref_warnings = update_layer_references(
            self.layout_data, layer_mapping
        )
        self.warnings.extend(ref_warnings)

        self.operations_log.append(
            f"Moved layer '{layer_name}' from position {old_index} to {new_position}"
        )

    def copy_layer(self, source_name: str, target_name: str) -> None:
        """Copy layer with new name.

        Args:
            source_name: Source layer name
            target_name: New layer name

        Raises:
            ValueError: If source not found or target exists
        """
        if source_name not in self.layout_data.layer_names:
            raise ValueError(f"Source layer '{source_name}' not found")
        if target_name in self.layout_data.layer_names:
            raise ValueError(f"Target layer '{target_name}' already exists")

        source_index = self.layout_data.layer_names.index(source_name)
        layer_data = self.layout_data.layers[source_index].copy()

        self.layout_data.layer_names.append(target_name)
        self.layout_data.layers.append(layer_data)

        self.operations_log.append(f"Copied layer '{source_name}' to '{target_name}'")

    def get_layer_names(self) -> list[str]:
        """Get list of layer names."""
        return self.layout_data.layer_names

    def get_variable_usage(self) -> dict[str, list[str]]:
        """Get variable usage information."""
        resolver = VariableResolver(self.layout_data.variables or {})
        return resolver.get_variable_usage(self.layout_data.model_dump())


def parse_comma_separated_fields(field_list: list[str] | None) -> list[str]:
    """Parse comma-separated field names from a list of strings.

    Args:
        field_list: List of field specifications, which may contain comma-separated values

    Returns:
        Flattened list of individual field names

    Examples:
        ["title,description", "version"] -> ["title", "description", "version"]
        ["title", "description"] -> ["title", "description"]
    """
    if not field_list:
        return []

    parsed_fields = []
    for field_spec in field_list:
        # Split by comma and strip whitespace
        fields = [field.strip() for field in field_spec.split(",")]
        # Filter out empty strings
        fields = [field for field in fields if field]
        parsed_fields.extend(fields)

    return parsed_fields


def deep_merge_dicts(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def parse_value(value_str: str) -> Any:
    """Parse value string into appropriate type."""
    # Handle from: syntax for imports
    if value_str.startswith("from:"):
        return ("import", value_str[5:])

    # Try JSON parsing for complex types
    if value_str.startswith(("{", "[", '"')):
        try:
            return json.loads(value_str)
        except json.JSONDecodeError:
            pass

    # Handle ZMK behavior strings (like "&kp Q", "&trans", "&none")
    if value_str.startswith("&"):
        return LayoutBinding.from_str(value_str).model_dump()

    # Boolean values
    if value_str.lower() in ("true", "false"):
        return value_str.lower() == "true"

    # Numeric values
    if value_str.isdigit() or (value_str.startswith("-") and value_str[1:].isdigit()):
        return int(value_str)

    try:
        return float(value_str)
    except ValueError:
        pass

    # Default to string
    return value_str


def resolve_import(source: str, base_path: Path) -> Any:
    """Resolve import source."""
    try:
        # Handle library references first
        if source.startswith("@"):
            # Library reference - resolve it first
            if "$." in source:
                # JSON path syntax: @lib-ref$.path.to.field
                file_part, json_path = source.split("$.", 1)
                from glovebox.cli.helpers.auto_profile import resolve_json_file_path

                file_path = resolve_json_file_path(file_part)
            elif ":" in source:
                # Shortcut syntax: @lib-ref:LayerName
                file_part, shortcut = source.split(":", 1)
                from glovebox.cli.helpers.auto_profile import resolve_json_file_path

                file_path = resolve_json_file_path(file_part)

                # Load file to resolve shortcut
                if file_path is None:
                    raise ValueError(
                        f"Could not resolve library reference: {file_part}"
                    )
                import_data = json.loads(file_path.read_text())

                # Common shortcuts
                if shortcut == "behaviors":
                    return import_data.get("custom_defined_behaviors", "")
                elif shortcut == "meta":
                    return {
                        k: v
                        for k, v in import_data.items()
                        if k in ["title", "keyboard", "version", "creator", "notes"]
                    }
                elif shortcut in import_data.get("layer_names", []):
                    # Layer by name
                    idx = import_data["layer_names"].index(shortcut)
                    return import_data["layers"][idx]
                else:
                    raise ValueError(f"Unknown shortcut: {shortcut}")
            else:
                # Full library import: @lib-ref
                from glovebox.cli.helpers.auto_profile import resolve_json_file_path

                file_path = resolve_json_file_path(source)
                if file_path is None:
                    raise ValueError(f"Could not resolve library reference: {source}")
                return json.loads(file_path.read_text())
        elif "$." in source:
            # JSON path syntax: file.json$.path.to.field
            file_part, json_path = source.split("$.", 1)
            file_path = base_path.parent / file_part
        elif ":" in source:
            # Shortcut syntax: file.json:LayerName
            file_part, shortcut = source.split(":", 1)
            file_path = base_path.parent / file_part

            # Load file to resolve shortcut
            import_data = json.loads(file_path.read_text())

            # Common shortcuts
            if shortcut == "behaviors":
                return import_data.get("custom_defined_behaviors", "")
            elif shortcut == "meta":
                return {
                    k: v
                    for k, v in import_data.items()
                    if k in ["title", "keyboard", "version", "creator", "notes"]
                }
            elif shortcut in import_data.get("layer_names", []):
                # Layer by name
                idx = import_data["layer_names"].index(shortcut)
                return import_data["layers"][idx]
            else:
                raise ValueError(f"Unknown shortcut: {shortcut}")
        else:
            # Full file import
            file_path = base_path.parent / source
            return json.loads(file_path.read_text())

        # Handle JSON path if needed
        if "$." in source:
            if file_path is None:
                raise ValueError(f"Could not resolve file path for JSON path: {source}")
            import_data = json.loads(file_path.read_text())
            current = import_data
            for part in json_path.split("."):
                if "[" in part and "]" in part:
                    # Array index
                    key, idx = part.split("[")
                    idx = int(idx.rstrip("]"))
                    current = current[key][idx]
                else:
                    current = current[part]
            return current

        return import_data

    except Exception as e:
        raise ValueError(f"Import failed for '{source}': {e}") from e


# Tab completion functions
def complete_field_operation(ctx: typer.Context, incomplete: str) -> list[str]:
    """Custom completion for field operations with key=value syntax."""
    try:
        # If we have = already, don't complete further
        if "=" in incomplete:
            key_part = incomplete.split("=")[0]
            # Could add value suggestions here
            return [incomplete]

        # Otherwise use standard field completion
        from glovebox.cli.helpers.parameters import complete_field_paths

        fields = complete_field_paths(ctx, incomplete)
        # Add = to each field for convenience
        return [f"{field}=" for field in fields]
    except Exception:
        return []


def complete_layer_operation(ctx: typer.Context, incomplete: str) -> list[str]:
    """Completion for layer operations."""
    try:
        from glovebox.cli.helpers.parameters import complete_layer_names

        return complete_layer_names(ctx, incomplete)
    except Exception:
        return []


class LayoutEditCommand(BaseLayoutCommand):
    """Command class for layout editing operations with atomic transactions."""

    def execute(
        self,
        layout_file: JsonFileArgument = None,
        # Field operations
        get: list[str] | None = None,
        set: list[str] | None = None,
        unset: list[str] | None = None,
        merge: list[str] | None = None,
        append: list[str] | None = None,
        # Layer operations
        add_layer: list[str] | None = None,
        remove_layer: list[str] | None = None,
        move_layer: list[str] | None = None,
        copy_layer: list[str] | None = None,
        # Info operations
        list_layers: bool = False,
        list_usage: bool = False,
        # Output options
        output: Path | None = None,
        output_format: str = "text",
        force: bool = False,
        dry_run: bool = False,
    ) -> None:
        """Execute the layout edit command."""
        # Resolve JSON file path
        resolved_file = resolve_json_file_path(layout_file, "GLOVEBOX_JSON_FILE")
        if not resolved_file:
            self.console.print_error(
                "JSON file is required. Provide as argument or set GLOVEBOX_JSON_FILE environment variable."
            )
            raise typer.Exit(1)

        # Check if only read operations are requested
        has_writes = self._has_write_operations(
            set, unset, merge, append, add_layer, remove_layer, move_layer, copy_layer
        )

        if not has_writes:
            self._handle_read_operations(
                resolved_file, get, list_layers, list_usage, output_format
            )
        else:
            self._handle_write_operations(
                resolved_file,
                get,
                set,
                unset,
                merge,
                append,
                add_layer,
                remove_layer,
                move_layer,
                copy_layer,
                output,
                output_format,
                dry_run,
            )

    def _has_write_operations(
        self,
        set: list[str] | None,
        unset: list[str] | None,
        merge: list[str] | None,
        append: list[str] | None,
        add_layer: list[str] | None,
        remove_layer: list[str] | None,
        move_layer: list[str] | None,
        copy_layer: list[str] | None,
    ) -> bool:
        """Check if any write operations are specified."""
        return any(
            [set, unset, merge, append, add_layer, remove_layer, move_layer, copy_layer]
        )

    def _handle_read_operations(
        self,
        resolved_file: Path,
        get: list[str] | None,
        list_layers: bool,
        list_usage: bool,
        output_format: str,
    ) -> None:
        """Handle read-only operations."""
        try:
            file_adapter = create_file_adapter()
            with VariableResolutionContext(skip=True):
                layout_data = load_layout_file(
                    resolved_file,
                    file_adapter,
                    skip_variable_resolution=True,
                    skip_template_processing=True,
                )

            editor = LayoutEditor(layout_data)
            results = self._execute_read_operations(
                editor, get, list_layers, list_usage
            )

            # Use LayoutOutputFormatter for output
            from glovebox.cli.commands.layout.formatters import (
                create_layout_output_formatter,
            )

            formatter = create_layout_output_formatter()
            formatter.format_edit_result(results, output_format)

        except Exception as e:
            self.handle_service_error(e, "read layout")

    def _handle_write_operations(
        self,
        resolved_file: Path,
        get: list[str] | None,
        set: list[str] | None,
        unset: list[str] | None,
        merge: list[str] | None,
        append: list[str] | None,
        add_layer: list[str] | None,
        remove_layer: list[str] | None,
        move_layer: list[str] | None,
        copy_layer: list[str] | None,
        output: Path | None,
        output_format: str,
        dry_run: bool,
    ) -> None:
        """Handle write operations using composer."""
        try:
            # Collect operations
            field_operations, _ = self._collect_field_operations(
                get, set, unset, merge, append
            )
            layer_operations = self._collect_layer_operations(
                add_layer, remove_layer, move_layer, copy_layer
            )

            # Create composer and execute edit operation
            from glovebox.cli.commands.layout.composition import (
                create_layout_command_composer,
            )

            composer = create_layout_command_composer()

            composer.execute_edit_operation(
                layout_file=resolved_file,
                field_operations=field_operations,
                layer_operations=layer_operations,
                operation_name="edit layout",
                output_format=output_format,
                save=not dry_run,
                dry_run=dry_run,
                output_file=output,
            )

        except Exception as e:
            self.handle_service_error(e, "edit layout")

    def _collect_field_operations(
        self,
        get: list[str] | None,
        set: list[str] | None,
        unset: list[str] | None,
        merge: list[str] | None,
        append: list[str] | None,
    ) -> tuple[list[tuple[str, str, str | None]], dict[str, Any]]:
        """Parse field operations into standard format."""
        operations: list[tuple[str, str, str | None]] = []
        read_results: dict[str, Any] = {}

        # Handle read operations
        if get:
            parsed_fields = parse_comma_separated_fields(get)
            for field_path in parsed_fields:
                operations.append(("get", field_path, None))

        # Handle write operations
        if set:
            for op in set:
                if "=" not in op:
                    raise ValueError(f"Invalid set syntax: {op} (use key=value)")
                field_path, value_str = op.split("=", 1)
                operations.append(("set", field_path, value_str))

        if unset:
            for field_path in unset:
                operations.append(("unset", field_path, None))

        if merge:
            for op in merge:
                if "=" not in op:
                    raise ValueError(f"Invalid merge syntax: {op} (use key=value)")
                field_path, value_str = op.split("=", 1)
                operations.append(("merge", field_path, value_str))

        if append:
            for op in append:
                if "=" not in op:
                    raise ValueError(f"Invalid append syntax: {op} (use key=value)")
                field_path, value_str = op.split("=", 1)
                operations.append(("append", field_path, value_str))

        return operations, read_results

    def _collect_layer_operations(
        self,
        add_layer: list[str] | None,
        remove_layer: list[str] | None,
        move_layer: list[str] | None,
        copy_layer: list[str] | None,
    ) -> list[tuple[str, str, str | None]]:
        """Parse layer operations into standard format."""
        operations: list[tuple[str, str, str | None]] = []

        if add_layer:
            for layer_spec in add_layer:
                if "=from:" in layer_spec:
                    layer_name, source = layer_spec.split("=from:", 1)
                    operations.append(("add_layer_from", layer_name, source))
                else:
                    operations.append(("add_layer", layer_spec, None))

        if remove_layer:
            for layer_id in remove_layer:
                operations.append(("remove_layer", layer_id, None))

        if move_layer:
            for move_spec in move_layer:
                if ":" not in move_spec:
                    raise ValueError(
                        f"Invalid move syntax: {move_spec} (use name:position)"
                    )
                layer_name, position = move_spec.split(":", 1)
                operations.append(("move_layer", layer_name, position))

        if copy_layer:
            for copy_spec in copy_layer:
                if ":" not in copy_spec:
                    raise ValueError(
                        f"Invalid copy syntax: {copy_spec} (use source:target)"
                    )
                source, target = copy_spec.split(":", 1)
                operations.append(("copy_layer", source, target))

        return operations

    def _execute_read_operations(
        self,
        editor: "LayoutEditor",
        get: list[str] | None,
        list_layers: bool,
        list_usage: bool,
    ) -> dict[str, Any]:
        """Execute read-only operations and return results."""
        results = {}

        if get:
            parsed_fields = parse_comma_separated_fields(get)
            for field_path in parsed_fields:
                try:
                    value = editor.get_field(field_path)
                    results[f"get:{field_path}"] = value
                except Exception as e:
                    results[f"get:{field_path}"] = f"Error: {e}"

        if list_layers:
            layer_names = editor.get_layer_names()
            results["layers"] = layer_names

        if list_usage:
            usage = editor.get_variable_usage()
            results["variable_usage"] = usage

        return results


@handle_errors
@with_metrics("edit")
def edit(
    layout_file: JsonFileArgument = None,
    # Field operations
    get: Annotated[
        list[str] | None,
        typer.Option(
            "--get",
            help="Get field value(s) using JSON path notation",
            autocompletion=complete_field_paths,
        ),
    ] = None,
    set: Annotated[
        list[str] | None,
        typer.Option(
            "--set",
            help="Set field value using 'key=value' format",
            autocompletion=complete_field_operation,
        ),
    ] = None,
    unset: Annotated[
        list[str] | None,
        typer.Option(
            "--unset",
            help="Remove field or dictionary key",
            autocompletion=complete_field_paths,
        ),
    ] = None,
    merge: Annotated[
        list[str] | None,
        typer.Option(
            "--merge",
            help="Merge dictionary using 'key=value' or 'key=from:file.json'",
            autocompletion=complete_field_operation,
        ),
    ] = None,
    append: Annotated[
        list[str] | None,
        typer.Option(
            "--append",
            help="Append to array using 'key=value' format",
            autocompletion=complete_field_operation,
        ),
    ] = None,
    # Layer operations
    add_layer: Annotated[
        list[str] | None,
        typer.Option("--add-layer", help="Add new layer(s)"),
    ] = None,
    remove_layer: Annotated[
        list[str] | None,
        typer.Option(
            "--remove-layer",
            help="Remove layer(s) by name or index",
            autocompletion=complete_layer_operation,
        ),
    ] = None,
    move_layer: Annotated[
        list[str] | None,
        typer.Option(
            "--move-layer",
            help="Move layer using 'name:position' syntax",
        ),
    ] = None,
    copy_layer: Annotated[
        list[str] | None,
        typer.Option(
            "--copy-layer",
            help="Copy layer using 'source:target' syntax",
        ),
    ] = None,
    # Info operations
    list_layers: Annotated[
        bool, typer.Option("--list-layers", help="List all layers in the layout")
    ] = False,
    list_usage: Annotated[
        bool, typer.Option("--list-usage", help="Show where each variable is used")
    ] = False,
    # Output options
    output: Annotated[
        Path | None,
        typer.Option(
            "--output", "-o", help="Output file (default: overwrite original)"
        ),
    ] = None,
    output_format: OutputFormatOption = "text",
    force: Annotated[
        bool, typer.Option("--force", help="Overwrite existing files")
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be done without saving"),
    ] = False,
) -> None:
    """Edit layout with atomic operations.

    Accepts layout files, library references (@name or @uuid), or environment variable.
    All operations are performed in memory and saved only if all succeed.
    Use --dry-run to preview changes without saving.

    Examples:
        # Edit from library by name
        glovebox layout edit @my-layout --set title="Updated Layout"

        # Edit from library by UUID
        glovebox layout edit @12345678-1234-1234-1234-123456789abc --set version="2.0"

        # Get field values (multiple ways)
        glovebox layout edit layout.json --get title --get keyboard
        glovebox layout edit layout.json --get title,keyboard,version
        glovebox layout edit layout.json --get variables.tapMs,variables.holdMs

        # Set fields
        glovebox layout edit layout.json --set title="My Layout" --set version="2.0"

        # Import from other files
        glovebox layout edit layout.json --set variables=from:vars.json$.variables
        glovebox layout edit layout.json --merge variables=from:other.json:meta

        # Layer operations
        glovebox layout edit layout.json --add-layer Gaming --remove-layer 3
        glovebox layout edit layout.json --move-layer Symbol:0 --copy-layer Base:Backup

        # Preview without saving
        glovebox layout edit layout.json --set title="Test" --dry-run
    """
    # Delegate to command class
    command = LayoutEditCommand()
    command.execute(
        layout_file=layout_file,
        get=get,
        set=set,
        unset=unset,
        merge=merge,
        append=append,
        add_layer=add_layer,
        remove_layer=remove_layer,
        move_layer=move_layer,
        copy_layer=copy_layer,
        list_layers=list_layers,
        list_usage=list_usage,
        output=output,
        output_format=output_format,
        force=force,
        dry_run=dry_run,
    )

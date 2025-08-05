# # TODO: Enable after refactoring - progress functionality temporarily disabled
# # """Simple Rich-based compilation progress display."""
# #
# # from __future__ import annotations
# #
# # import logging
# # import time
# # from dataclasses import dataclass, field
# # from typing import TYPE_CHECKING
# #
# # from rich.console import Console
# # from rich.live import Live
# # from rich.panel import Panel
# # from rich.progress import (
# #     BarColumn,
# #     Progress,
# #     SpinnerColumn,
# #     TaskID,
# #     TaskProgressColumn,
# #     TextColumn,
# # )
# # from rich.table import Table
# # from rich.text import Text
# #
# # from glovebox.cli.helpers.theme import Colors, IconMode, Icons, format_status_message
# # from glovebox.core.file_operations import CompilationProgress
# #
# #
# # if TYPE_CHECKING:
# #     pass
# #
# # logger = logging.getLogger(__name__)
#
# #
# #
# # @dataclass
# # class ProgressConfig:
#     """Configuration for customizable progress display."""
#
#     operation_name: str = "Operation"
#     icon_mode: IconMode = IconMode.TEXT
#
#     @property
#     def title_processing(self) -> str:
#         """Get processing title with appropriate icon."""
#         return Icons.format_with_icon("PROCESSING", "Processing", self.icon_mode)
#
#     @property
#     def title_complete(self) -> str:
#         """Get completion title with appropriate icon."""
#         return Icons.format_with_icon("SUCCESS", "Operation Complete", self.icon_mode)
#
#     @property
#     def title_failed(self) -> str:
#         """Get failure title with appropriate icon."""
#         return Icons.format_with_icon("ERROR", "Operation Failed", self.icon_mode)
#
#     # Fully customizable task list - just task names in order
#     tasks: list[str] = field(
#         default_factory=lambda: [
#             "Cache Setup",
#             "Workspace Setup",
#             "Dependencies",
#             "Building Firmware",
#             "Post Processing",
#         ]
#     )
#
#
# class SimpleCompilationDisplay:
#     """Simple Rich-based compilation progress display with task status indicators."""
#
#     def __init__(
#         self,
#         console: Console | None = None,
#         config: ProgressConfig | None = None,
#         icon_mode: IconMode = IconMode.TEXT,
#     ) -> None:
#         """Initialize the simple compilation display.
#
#         Args:
#             console: Rich console for output. If None, creates a new one.
#             config: Progress configuration. If None, uses default compilation-focused config.
#         """
#         self.console = console or Console()
#         # If no config provided, create one with the icon_mode
#         if config is None:
#             config = ProgressConfig(icon_mode=icon_mode)
#         else:
#             # Update existing config's icon_mode
#             config.icon_mode = icon_mode
#         self.config = config
#         self.icon_mode = icon_mode
#         self._live: Live | None = None
#         self._progress: Progress | None = None
#         self._current_task_id: TaskID | None = None
#
#         # Simple task list with status tracking
#         self._tasks = [
#             {"name": task_name, "status": "pending"} for task_name in self.config.tasks
#         ]
#         self._current_task_index = -1
#
#         self._current_description = ""
#         self._current_percentage = 0.0  # Track current progress percentage
#         self._start_time = time.time()
#         self._is_complete = False
#         self._is_failed = False
#
#     def start(self) -> None:
#         """Start the live display."""
#         if self._live is not None:
#             return
#
#         self._progress = Progress(
#             SpinnerColumn(),
#             TextColumn("[progress.description]{task.description}"),
#             BarColumn(),
#             TaskProgressColumn(),
#             console=self.console,
#             transient=False,
#         )
#
#         self._live = Live(
#             self._generate_display(),
#             console=self.console,
#             refresh_per_second=10,
#             transient=False,
#         )
#         self._live.start()
#
#     def stop(self) -> None:
#         """Stop the live display."""
#         if self._live is not None:
#             self._live.stop()
#             self._live = None
#         self._progress = None
#
#     def start_task(
#         self, task_index: int, description: str = "", percentage: float = 0.0
#     ) -> None:
#         """Start a specific task by index."""
#         if 0 <= task_index < len(self._tasks):
#             # Mark previous tasks as completed
#             for i in range(task_index):
#                 if self._tasks[i]["status"] == "pending":
#                     self._tasks[i]["status"] = "completed"
#
#             # Mark current task as active
#             self._tasks[task_index]["status"] = "active"
#             self._current_task_index = task_index
#             self._current_description = description
#             self._current_percentage = percentage
#
#             # Update display
#             if self._live is not None:
#                 self._live.update(self._generate_display())
#
#     def start_task_by_name(
#         self, task_name: str, description: str = "", percentage: float = 0.0
#     ) -> None:
#         """Start a task by its name."""
#         for i, task in enumerate(self._tasks):
#             if task["name"] == task_name:
#                 self.start_task(i, description, percentage)
#                 return
#
#     def update_current_task(
#         self, description: str = "", percentage: float = 0.0
#     ) -> None:
#         """Update the current active task."""
#         if self._current_task_index >= 0:
#             self._current_description = description
#             self._current_percentage = percentage
#
#             # Update display
#             if self._live is not None:
#                 self._live.update(self._generate_display())
#
#     def complete_current_task(self) -> None:
#         """Mark the current task as completed."""
#         if self._current_task_index >= 0:
#             self._tasks[self._current_task_index]["status"] = "completed"
#             self._current_task_index = -1
#
#             # Update display
#             if self._live is not None:
#                 self._live.update(self._generate_display())
#
#     def fail_current_task(self) -> None:
#         """Mark the current task as failed."""
#         if self._current_task_index >= 0:
#             self._tasks[self._current_task_index]["status"] = "failed"
#             self._is_failed = True
#
#             # Update display
#             if self._live is not None:
#                 self._live.update(self._generate_display())
#
#     def complete_all(self) -> None:
#         """Mark all tasks as completed."""
#         for task in self._tasks:
#             if task["status"] in ("pending", "active"):
#                 task["status"] = "completed"
#         self._current_task_index = -1
#         self._is_complete = True
#
#         # Update display
#         if self._live is not None:
#             self._live.update(self._generate_display())
#
#     def fail_all(self) -> None:
#         """Mark the operation as failed."""
#         if self._current_task_index >= 0:
#             self._tasks[self._current_task_index]["status"] = "failed"
#         self._is_failed = True
#
#         # Update display
#         if self._live is not None:
#             self._live.update(self._generate_display())
#
#     def _generate_display(self) -> Panel:
#         """Generate the Rich display panel with visual progress bars.
#
#         Returns:
#             Rich Panel containing the progress display
#         """
#         # Create main content table
#         table = Table.grid(padding=(0, 1))
#         table.add_column(style=Colors.NORMAL, no_wrap=False, width=None)
#
#         # Get current active task info
#         active_task_name = "Processing"
#         active_percentage = self._current_percentage
#         status_info = self._current_description
#
#         # Find the currently active task
#         if self._current_task_index >= 0 and self._current_task_index < len(
#             self._tasks
#         ):
#             active_task_name = self._tasks[self._current_task_index]["name"]
#         elif self._is_complete:
#             active_task_name = "Complete"
#             active_percentage = 100.0
#         elif self._is_failed:
#             active_task_name = "Failed"
#             active_percentage = 0.0
#
#         # Create main progress display as a simple text line with inline progress bar
#         progress_text = Text()
#         progress_text.append(f"{active_task_name}... ", style=Colors.PRIMARY)
#
#         # Create inline progress bar using theme-aware characters
#         bar_width = 40
#         filled_width = int((active_percentage / 100.0) * bar_width)
#         empty_width = bar_width - filled_width
#
#         filled_char = Icons.get_icon("PROGRESS_FULL", self.icon_mode) or "█"
#         empty_char = Icons.get_icon("PROGRESS_EMPTY", self.icon_mode) or "░"
#         progress_bar = filled_char * filled_width + empty_char * empty_width
#         progress_text.append(progress_bar, style=Colors.PROGRESS_BAR)
#         progress_text.append(f" {active_percentage:>5.1f}%", style=Colors.HIGHLIGHT)
#
#         # Add main progress line
#         table.add_row(progress_text)
#
#         # Add status information if available
#         if status_info:
#             table.add_row("")  # Spacer
#
#             # Create status text with proper styling
#             status_text = Text()
#             status_text.append("Status: ", style=Colors.MUTED)
#
#             # Truncate long status info
#             display_status = status_info
#             if len(display_status) > 80:
#                 display_status = display_status[:77] + "..."
#
#             status_text.append(display_status, style=Colors.INFO)
#             table.add_row(status_text)
#
#         # Add overall progress summary
#         table.add_row("")  # Spacer
#
#         # Count completed vs total tasks
#         completed_tasks = sum(
#             1 for task in self._tasks if task["status"] == "completed"
#         )
#         total_tasks = len(self._tasks)
#
#         if total_tasks > 0:
#             overall_percentage = (completed_tasks / total_tasks) * 100
#
#             # Create simple overall progress line
#             overall_text = Text()
#             overall_text.append("Overall: ", style=Colors.MUTED)
#
#             # Create smaller inline progress bar for overall using theme-aware characters
#             overall_bar_width = 30
#             overall_filled_width = int((overall_percentage / 100.0) * overall_bar_width)
#             overall_empty_width = overall_bar_width - overall_filled_width
#
#             filled_char = Icons.get_icon("PROGRESS_FULL", self.icon_mode) or "█"
#             empty_char = Icons.get_icon("PROGRESS_EMPTY", self.icon_mode) or "░"
#             overall_progress_bar = (
#                 filled_char * overall_filled_width + empty_char * overall_empty_width
#             )
#             overall_text.append(overall_progress_bar, style=Colors.LOADING_TEXT)
#             overall_text.append(
#                 f" {overall_percentage:>5.1f}% ({completed_tasks}/{total_tasks} tasks)",
#                 style=Colors.MUTED,
#             )
#
#             table.add_row(overall_text)
#
#         # Add task checklist below
#         table.add_row("")  # Spacer
#
#         # Show task status list (compact format)
#         for task in self._tasks:
#             status_icon = self._get_status_icon(task["status"])
#             task_name = task["name"]
#
#             # Create task status line
#             task_line = Text()
#             task_line.append(f" {status_icon} ", style=Colors.NORMAL)
#
#             if task["status"] == "active":
#                 task_line.append(task_name, style=Colors.RUNNING)
#             elif task["status"] == "completed":
#                 task_line.append(task_name, style=Colors.COMPLETED)
#             elif task["status"] == "failed":
#                 task_line.append(task_name, style=Colors.FAILED)
#             else:
#                 task_line.append(task_name, style=Colors.MUTED)
#
#             table.add_row(task_line)
#
#         # Add elapsed time
#         elapsed = time.time() - self._start_time
#         elapsed_str = f"Elapsed: {elapsed:.1f}s"
#
#         # Determine title based on state - using config properties
#         if self._is_complete:
#             title = self.config.title_complete
#             border_style = Colors.SUCCESS
#         elif self._is_failed:
#             title = self.config.title_failed
#             border_style = Colors.ERROR
#         else:
#             title = self.config.title_processing
#             border_style = Colors.INFO
#
#         return Panel(
#             table,
#             title=title,
#             subtitle=elapsed_str,
#             border_style=border_style,
#         )
#
#     def print_log(self, message: str, level: str = "info") -> None:
#         """Print a log message through the console, above the progress display.
#
#         Args:
#             message: The log message to display
#             level: Log level (info, warning, error, debug)
#         """
#         # Style the message based on level using theme helpers
#         if level == "error":
#             styled_message = format_status_message(f"ERROR: {message}", "error")
#         elif level == "warning":
#             styled_message = format_status_message(f"WARNING: {message}", "warning")
#         elif level == "debug":
#             styled_message = f"[{Colors.MUTED}]DEBUG:[/] {message}"
#         else:
#             styled_message = message
#
#         # Print through the console so it appears above the live display
#         self.console.print(styled_message)
#
#     def _get_status_icon(self, status: str) -> str:
#         """Get the status icon for a task.
#
#         Args:
#             status: Task status (pending, active, completed, failed)
#
#         Returns:
#             Status icon string
#         """
#         icon_map = {
#             "pending": "BULLET",
#             "active": "RUNNING",
#             "completed": "SUCCESS",
#             "failed": "ERROR",
#         }
#         icon_name = icon_map.get(status, "BULLET")
#         return Icons.get_icon(icon_name, self.icon_mode)
#
#
# class SimpleProgressCoordinator:
#     """Simple progress coordinator with task-based interface."""
#
#     def __init__(self, display: SimpleCompilationDisplay) -> None:
#         """Initialize the coordinator.
#
#         Args:
#             display: The simple display to update
#         """
#         self.display = display
#         self.config = display.config  # Use the same config as the display
#
#         # Required protocol attributes
#         self.current_phase: str = "initialization"
#         self.docker_image_name: str = ""
#         self.compilation_strategy: str = ""
#
#         # Additional progress tracking attributes
#         self.total_repositories: int = 0
#         self.repositories_downloaded: int = 0
#         self.boards_completed: int = 0
#         self.total_boards: int = 0
#
#     def start_task_by_name(
#         self, task_name: str, description: str = "", percentage: float = 0.0
#     ) -> None:
#         """Start a task by its name.
#
#         Args:
#             task_name: Name of the task to start
#             description: Optional description for the task
#             percentage: Initial progress percentage (0-100)
#         """
#         logger.debug(
#             "Starting task: %s (description: %s, percentage: %.1f)",
#             task_name,
#             description,
#             percentage,
#         )
#         self.display.start_task_by_name(task_name, description, percentage)
#
#     def update_current_task(
#         self, description: str = "", percentage: float = 0.0
#     ) -> None:
#         """Update the current active task.
#
#         Args:
#             description: Updated description for the task
#             percentage: Updated progress percentage (0-100)
#         """
#         self.display.update_current_task(description, percentage)
#
#     def complete_current_task(self) -> None:
#         """Mark the current task as completed."""
#         logger.debug("Completing current task")
#         self.display.complete_current_task()
#
#     def fail_current_task(self) -> None:
#         """Mark the current task as failed."""
#         self.display.fail_current_task()
#
#     def complete_all_tasks(self) -> None:
#         """Mark all tasks as completed."""
#         logger.debug("Completing all tasks - transitioning to success state")
#         self.display.complete_all()
#
#     def fail_all_tasks(self) -> None:
#         """Mark the operation as failed."""
#         logger.debug("Failing all tasks - transitioning to error state")
#         self.display.fail_all()
#
#     def print_log(self, message: str, level: str = "info") -> None:
#         """Print a log message through the display console.
#
#         Args:
#             message: The log message to display
#             level: Log level (info, warning, error, debug)
#         """
#         self.display.print_log(message, level)
#
#     def transition_to_phase(self, phase: str, description: str = "") -> None:
#         """Transition to a new phase - maps to task-based system.
#
#         For backward compatibility, this maps common phase names to tasks.
#         If the phase matches a task name, it will start that task.
#
#         Args:
#             phase: Phase name (e.g., "cache_setup", "workspace_setup")
#             description: Description for the phase/task
#         """
#         # Update current phase for middleware compatibility
#         self.current_phase = phase
#
#         # Try to find a matching task name for this phase
#         phase_to_task_mapping = {
#             "cache": "Cache Setup",
#             "cache_setup": "Cache Setup",
#             "cache_restoration": "Cache Setup",
#             "workspace": "Workspace Setup",
#             "workspace_setup": "Workspace Setup",
#             "dependencies": "Dependencies",
#             "dependency_fetch": "Dependencies",
#             "building": "Building Firmware",
#             "post_processing": "Post Processing",
#             "finalizing": "Post Processing",
#         }
#
#         # Find matching task name
#         task_name = phase_to_task_mapping.get(phase.lower())
#         if task_name:
#             self.start_task_by_name(task_name, description)
#         else:
#             # If no mapping found, try to find a task with similar name
#             for task in self.config.tasks:
#                 if phase.lower() in task.lower() or task.lower() in phase.lower():
#                     self.start_task_by_name(task, description)
#                     return
#
#             # If still no match, just update current task with description
#             if description:
#                 self.update_current_task(description)
#
#     def set_enhanced_task_status(
#         self, task_name: str, status: str, description: str = ""
#     ) -> None:
#         """Set status for enhanced tasks - compatibility method.
#
#         This method provides backward compatibility for callers that expect
#         enhanced task status functionality. In the simplified system, this
#         maps to basic task operations.
#
#         Args:
#             task_name: Name of the enhanced task
#             status: Task status (pending, active, completed, failed)
#             description: Optional description for the task
#         """
#         if status == "active":
#             # Find the closest matching task name or use description
#             display_name = description or task_name.replace("_", " ").title()
#
#             # Try to find matching task in our config
#             matching_task = None
#             for task in self.config.tasks:
#                 if (
#                     task_name.lower() in task.lower()
#                     or task.lower() in task_name.lower()
#                 ):
#                     matching_task = task
#                     break
#
#             if matching_task:
#                 self.start_task_by_name(matching_task, description)
#             else:
#                 # Update current task with the description
#                 self.update_current_task(display_name)
#         elif status == "completed":
#             self.complete_current_task()
#         elif status == "failed":
#             self.fail_current_task()
#
#     def set_compilation_strategy(self, strategy: str, docker_image: str = "") -> None:
#         """Set compilation strategy metadata."""
#         self.compilation_strategy = strategy
#         self.docker_image_name = docker_image
#
#     def update_workspace_progress(
#         self,
#         files_copied: int = 0,
#         total_files: int = 0,
#         bytes_copied: int = 0,
#         total_bytes: int = 0,
#         current_file: str = "",
#         component: str = "",
#         transfer_speed_mb_s: float = 0.0,
#         eta_seconds: float = 0.0,
#     ) -> None:
#         """Update workspace setup progress.
#
#         Args:
#             files_copied: Number of files copied so far
#             total_files: Total number of files to copy
#             bytes_copied: Number of bytes copied so far
#             total_bytes: Total number of bytes to copy
#             current_file: Current file being copied
#             component: Current component being processed
#             transfer_speed_mb_s: Transfer speed in MB/s
#             eta_seconds: Estimated time to completion in seconds
#         """
#         if total_files > 0:
#             progress_percentage = (files_copied / total_files) * 100
#         elif total_bytes > 0:
#             progress_percentage = (bytes_copied / total_bytes) * 100
#         else:
#             progress_percentage = 0.0
#
#         # Create descriptive status message
#         if component and current_file:
#             status = f"Copying {component}: {current_file}"
#         elif component:
#             status = f"Processing {component} ({files_copied}/{total_files} files)"
#         elif current_file:
#             status = f"Copying: {current_file}"
#         else:
#             status = f"Copying files ({files_copied}/{total_files})"
#
#         # Add transfer speed and ETA if available
#         if transfer_speed_mb_s > 0:
#             status += f" @ {transfer_speed_mb_s:.1f} MB/s"
#         if eta_seconds > 0:
#             eta_minutes = eta_seconds / 60
#             if eta_minutes >= 1:
#                 status += f" (ETA: {eta_minutes:.1f}m)"
#             else:
#                 status += f" (ETA: {eta_seconds:.0f}s)"
#
#         self.update_current_task(status, progress_percentage)
#
#     def update_cache_progress(
#         self,
#         operation: str,
#         current: int = 0,
#         total: int = 100,
#         description: str = "",
#         status: str = "in_progress",
#     ) -> None:
#         """Update cache restoration progress."""
#         if total > 0:
#             progress_percentage = (current / total) * 100
#         else:
#             progress_percentage = 0.0
#
#         status_text = f"{operation}: {description}" if description else operation
#         self.update_current_task(status_text, progress_percentage)
#
#     def update_repository_progress(self, repository_name: str) -> None:
#         """Update repository download progress during west update."""
#         self.repositories_downloaded += 1
#
#         # Calculate download progress percentage
#         if self.total_repositories > 0:
#             percentage = (self.repositories_downloaded / self.total_repositories) * 100
#             logger.debug(
#                 "Repository progress: %d/%d (%.1f%%) - %s",
#                 self.repositories_downloaded,
#                 self.total_repositories,
#                 percentage,
#                 repository_name,
#             )
#         else:
#             percentage = 0.0
#
#         self.update_current_task(
#             f"Downloading repository: {repository_name}", percentage
#         )
#
#     def update_cache_extraction_progress(
#         self,
#         operation: str = "",
#         files_extracted: int = 0,
#         total_files: int = 0,
#         bytes_extracted: int = 0,
#         total_bytes: int = 0,
#         current_file: str = "",
#         archive_name: str = "",
#         extraction_speed_mb_s: float = 0.0,
#         eta_seconds: float = 0.0,
#     ) -> None:
#         """Update cache extraction progress.
#
#         Args:
#             operation: Type of operation being performed
#             files_extracted: Number of files extracted so far
#             total_files: Total number of files to extract
#             bytes_extracted: Number of bytes extracted so far
#             total_bytes: Total number of bytes to extract
#             current_file: Current file being extracted
#             archive_name: Name of the archive being extracted
#             extraction_speed_mb_s: Extraction speed in MB/s
#             eta_seconds: Estimated time to completion in seconds
#         """
#         if total_files > 0:
#             progress_percentage = (files_extracted / total_files) * 100
#         elif total_bytes > 0:
#             progress_percentage = (bytes_extracted / total_bytes) * 100
#         else:
#             progress_percentage = 0.0
#
#         # Create descriptive status message
#         if current_file and archive_name:
#             # Show just the filename if it's very long
#             display_file = (
#                 current_file.split("/")[-1] if "/" in current_file else current_file
#             )
#             if len(display_file) > 40:
#                 display_file = display_file[:37] + "..."
#             status = f"Extracting {archive_name}: {display_file}"
#         elif archive_name:
#             status = (
#                 f"Extracting {archive_name} ({files_extracted}/{total_files} files)"
#             )
#         else:
#             status = f"Extracting files ({files_extracted}/{total_files})"
#
#         # Add extraction speed and ETA if available
#         if extraction_speed_mb_s > 0:
#             status += f" @ {extraction_speed_mb_s:.1f} MB/s"
#         if eta_seconds > 0:
#             eta_minutes = eta_seconds / 60
#             if eta_minutes >= 1:
#                 status += f" (ETA: {eta_minutes:.1f}m)"
#             else:
#                 status += f" (ETA: {eta_seconds:.0f}s)"
#
#         self.update_current_task(status, progress_percentage)
#
#     def update_board_progress(
#         self,
#         board_name: str = "",
#         current_step: int = 0,
#         total_steps: int = 0,
#         completed: bool = False,
#     ) -> None:
#         """Update board compilation progress."""
#         if completed:
#             self.boards_completed += 1
#             logger.debug(
#                 "Board completed - boards_completed: %d/%d",
#                 self.boards_completed,
#                 self.total_boards,
#             )
#
#         # Update the current task with board progress
#         if board_name:
#             description = f"Building {board_name}"
#         elif current_step and total_steps:
#             description = f"Building [{current_step}/{total_steps}]"
#         else:
#             description = "Building firmware"
#
#         # Calculate overall percentage based on board completion AND step progress
#         if self.total_boards > 0:
#             # Calculate base percentage from completed boards
#             completed_percentage = (self.boards_completed / self.total_boards) * 100
#
#             # Factor in current board step progress if available
#             if current_step > 0 and total_steps > 0:
#                 # Each board represents (100 / total_boards) percent of the total
#                 board_weight = 100 / self.total_boards
#                 # Current board's step progress as a fraction of its weight
#                 current_board_progress = (current_step / total_steps) * board_weight
#                 percentage = completed_percentage + current_board_progress
#                 logger.debug(
#                     "Step progress: %d/%d (%.1f%%) in board %d/%d, total: %.1f%%",
#                     current_step,
#                     total_steps,
#                     current_board_progress,
#                     self.boards_completed + 1,
#                     self.total_boards,
#                     percentage,
#                 )
#             else:
#                 percentage = completed_percentage
#         else:
#             percentage = 0.0
#
#         self.update_current_task(description, percentage)
#
#     def complete_all_builds(self) -> None:
#         """Mark all builds as complete and transition to done phase."""
#         logger.debug(
#             "complete_all_builds called - boards_completed: %d/%d",
#             self.boards_completed,
#             self.total_boards,
#         )
#         self.complete_all_tasks()
#
#     def complete_build_success(
#         self, reason: str = "Build completed successfully"
#     ) -> None:
#         """Mark build as complete regardless of current phase (for cached builds)."""
#         logger.debug("complete_build_success called - reason: %s", reason)
#         self.complete_all_tasks()
#
#     def get_current_progress(self) -> CompilationProgress:
#         """Get the current unified progress state."""
#         return CompilationProgress(
#             repositories_downloaded=0,  # Not tracked in simple display
#             total_repositories=self.total_repositories,
#             current_repository="",
#             compilation_phase=self.current_phase,
#             bytes_downloaded=0,
#             total_bytes=0,
#             current_board="",
#             boards_completed=self.boards_completed,
#             total_boards=self.total_boards,
#             current_board_step=0,
#             total_board_steps=0,
#             cache_operation_progress=0,
#             cache_operation_total=100,
#             cache_operation_status="pending",
#             compilation_strategy=self.compilation_strategy,
#             docker_image_name=self.docker_image_name,
#         )
#
#     def update_export_progress(
#         self,
#         files_processed: int = 0,
#         total_files: int = 0,
#         current_file: str = "",
#         archive_format: str = "",
#         compression_level: int = 0,
#         speed_mb_s: float = 0.0,
#         eta_seconds: float = 0.0,
#     ) -> None:
#         """Update workspace export progress."""
#         if total_files > 0:
#             progress_percentage = (files_processed / total_files) * 100
#         else:
#             progress_percentage = 0.0
#
#         # Create descriptive status message
#         if current_file and archive_format:
#             status = f"Exporting {archive_format}: {current_file}"
#         elif archive_format:
#             status = (
#                 f"Exporting {archive_format} ({files_processed}/{total_files} files)"
#             )
#         else:
#             status = f"Exporting files ({files_processed}/{total_files})"
#
#         self.update_current_task(status, progress_percentage)
#
#     def update_cache_saving(self, operation: str = "", progress_info: str = "") -> None:
#         """Update cache saving progress."""
#         status = f"Saving cache: {operation}" if operation else "Saving cache"
#         if progress_info:
#             status += f" - {progress_info}"
#         self.update_current_task(status)
#
#     def update_docker_verification(
#         self, image_name: str, status: str = "verifying"
#     ) -> None:
#         """Update Docker image verification progress (MoErgo specific)."""
#         self.update_current_task(f"Docker: {status} {image_name}")
#
#     def update_nix_build_progress(
#         self, operation: str, status: str = "building"
#     ) -> None:
#         """Update Nix environment build progress (MoErgo specific)."""
#         self.update_current_task(f"Nix {status}: {operation}")
#
#
# def create_simple_compilation_display(
#     console: Console | None = None,
#     config: ProgressConfig | None = None,
#     icon_mode: IconMode = IconMode.TEXT,
# ) -> SimpleCompilationDisplay:
#     """Factory function to create a simple compilation display.
#
#     Args:
#         console: Rich console for output. If None, creates a new one.
#         config: Progress configuration. If None, uses default compilation-focused config.
#         icon_mode: Icon mode for symbols and progress indicators.
#
#     Returns:
#         SimpleCompilationDisplay instance
#     """
#     return SimpleCompilationDisplay(console, config, icon_mode)
#
#
# def create_simple_progress_coordinator(
#     display: SimpleCompilationDisplay,
# ) -> SimpleProgressCoordinator:
#     """Factory function to create a simple progress coordinator.
#
#     Args:
#         display: The simple display to update
#
#     Returns:
#         SimpleProgressCoordinator instance
#     """
#     return SimpleProgressCoordinator(display)

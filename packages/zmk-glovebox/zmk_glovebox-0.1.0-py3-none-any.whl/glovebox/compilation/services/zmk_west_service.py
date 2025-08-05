"""ZMK config with west compilation service."""

import logging
import shutil
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from glovebox.layout.models import LayoutData
    from glovebox.protocols.progress_context_protocol import ProgressContextProtocol
    from glovebox.protocols.progress_coordinator_protocol import (
        ProgressCoordinatorProtocol,
    )

from glovebox.adapters.compilation_progress_middleware import (
    create_compilation_progress_middleware,
)
from glovebox.adapters.docker_adapter import LoggerOutputMiddleware
from glovebox.compilation.cache.compilation_build_cache_service import (
    CompilationBuildCacheService,
)
from glovebox.compilation.cache.workspace_cache_service import (
    ZmkWorkspaceCacheService,
)
from glovebox.compilation.models import (
    CompilationConfigUnion,
    ZmkCompilationConfig,
)
from glovebox.compilation.models.build_matrix import BuildMatrix
from glovebox.compilation.protocols.compilation_protocols import (
    CompilationServiceProtocol,
)
from glovebox.compilation.services.workspace_setup_service import (
    WorkspaceSetupService,
    create_workspace_setup_service,
)
from glovebox.compilation.services.zmk_cache_service import (
    ZmkCacheService,
    create_zmk_cache_service,
)
from glovebox.config.user_config import UserConfig
from glovebox.core.cache.cache_manager import CacheManager
from glovebox.core.cache.models import CacheKey
from glovebox.core.file_operations import (
    CompilationProgressCallback,
    FileCopyService,
    create_copy_service,
)
from glovebox.firmware.models import (
    BuildResult,
    FirmwareOutputFiles,
    create_build_info_file,
)
from glovebox.models.docker import DockerUserContext
from glovebox.protocols import (
    DockerAdapterProtocol,
    FileAdapterProtocol,
    MetricsProtocol,
)
from glovebox.protocols.progress_coordinator_protocol import ProgressCoordinatorProtocol
from glovebox.utils.build_log_middleware import create_build_log_middleware
from glovebox.utils.stream_process import (
    DefaultOutputMiddleware,
    OutputMiddleware,
    create_chained_middleware,
)


if TYPE_CHECKING:
    from glovebox.config.profile import KeyboardProfile


class ZmkWestService(CompilationServiceProtocol):
    """ZMK config compilation service with workspace and build caching.

    This service uses the ZMK docker image to compile with the west framwork.

    Workspace folder are created in tmp folder for the time of the operation

    3 layers of caching are used implemented in ZmkCacheService:
        * Workspace: using the reposition name for key
        * Workspace repo+branch: using the repo+branch name for key
        * Build: Build output folder using repository, branch, hash of keymap and kconfig file.
    """

    def __init__(
        self,
        docker_adapter: DockerAdapterProtocol,
        user_config: UserConfig,
        file_adapter: FileAdapterProtocol,
        cache_manager: CacheManager,
        session_metrics: MetricsProtocol,
        workspace_setup_service: WorkspaceSetupService | None = None,
        cache_service: ZmkCacheService | None = None,
        copy_service: FileCopyService | None = None,
        default_progress_callback: "CompilationProgressCallback | None" = None,
    ) -> None:
        """Initialize with Docker adapter, user config, file adapter, cache services, and metrics."""
        self.docker_adapter = docker_adapter
        self.user_config = user_config
        self.file_adapter = file_adapter
        self.cache_manager = cache_manager
        self.session_metrics = session_metrics
        self.logger = logging.getLogger(__name__)
        self.copy_service = copy_service or create_copy_service(
            use_pipeline=True, max_workers=3
        )
        self.default_progress_callback = default_progress_callback

        # Progress coordinator for enhanced progress tracking
        self._external_progress_coordinator: ProgressCoordinatorProtocol | None = None

        # Initialize services
        self.workspace_setup_service = (
            workspace_setup_service
            or create_workspace_setup_service(
                file_adapter=file_adapter,
                session_metrics=session_metrics,
                copy_service=self.copy_service,
            )
        )

        self.cache_service = cache_service or create_zmk_cache_service(
            user_config=user_config,
            cache_manager=cache_manager,
            session_metrics=session_metrics,
        )

    def compile(
        self,
        keymap_file: Path,
        config_file: Path,
        output_dir: Path,
        config: CompilationConfigUnion,
        keyboard_profile: "KeyboardProfile",
        progress_callback: "CompilationProgressCallback | None" = None,
        json_file: Path | None = None,
    ) -> BuildResult:
        """Execute ZMK compilation."""
        self.logger.info("Starting ZMK config compilation")

        # Initialize compilation metrics if SessionMetrics available
        if self.session_metrics:
            compilation_operations = self.session_metrics.Counter(
                "compilation_operations_total",
                "Total compilation operations",
                ["keyboard_name", "firmware_version", "strategy"],
            )
            compilation_duration = self.session_metrics.Histogram(
                "compilation_duration_seconds", "Compilation operation duration"
            )

            compilation_operations.labels(
                keyboard_profile.keyboard_name,
                keyboard_profile.firmware_version or "unknown",
                "zmk_config",
            ).inc()

            with compilation_duration.time():
                return self._compile_internal(
                    keymap_file,
                    config_file,
                    output_dir,
                    config,
                    keyboard_profile,
                    progress_callback,
                    json_file,
                )
        else:
            return self._compile_internal(
                keymap_file,
                config_file,
                output_dir,
                config,
                keyboard_profile,
                progress_callback,
                json_file,
            )

    def _compile_internal(
        self,
        keymap_file: Path,
        config_file: Path,
        output_dir: Path,
        config: CompilationConfigUnion,
        keyboard_profile: "KeyboardProfile",
        progress_callback: CompilationProgressCallback | None = None,
        json_file: Path | None = None,
    ) -> BuildResult:
        """Execute ZMK compilation."""
        compilation_start_time = time.time()

        try:
            if not isinstance(config, ZmkCompilationConfig):
                return BuildResult(
                    success=False, errors=["Invalid config type for ZMK compilation"]
                )

            self.logger.info("%s@%s", config.repository, config.branch)

            # Setup progress context using compilation-specific factory
            from glovebox.cli.components import create_compilation_progress_manager

            # Extract board information for progress tracking
            board_info = self._extract_board_info_from_config(config)

            # Use provided progress_callback or fall back to default
            effective_progress_callback = (
                progress_callback or self.default_progress_callback
            )

            # Create progress manager with ZMK-specific checkpoints
            progress_manager = create_compilation_progress_manager(
                operation_name="ZMK West Compilation",
                base_checkpoints=[
                    "Cache Check",
                    "Workspace Setup",
                    "Dependencies Update",
                ],
                final_checkpoints=["Caching Results"],
                board_info=board_info,
                progress_callback=effective_progress_callback,
            )

            with progress_manager as progress_context:
                return self._execute_zmk_compilation_with_progress(
                    progress_context,
                    keymap_file,
                    config_file,
                    output_dir,
                    config,
                    keyboard_profile,
                    compilation_start_time,
                    json_file,
                )

        except Exception as e:
            exc_info = self.logger.isEnabledFor(logging.DEBUG)
            self.logger.error("Compilation failed: %s", e, exc_info=exc_info)
            return BuildResult(success=False, errors=[str(e)])

    def _execute_zmk_compilation_with_progress(
        self,
        progress_context: "ProgressContextProtocol",
        keymap_file: Path,
        config_file: Path,
        output_dir: Path,
        config: ZmkCompilationConfig,
        keyboard_profile: "KeyboardProfile",
        compilation_start_time: float,
        json_file: Path | None = None,
    ) -> BuildResult:
        """Execute ZMK compilation with progress tracking."""
        try:
            # Initialize cache metrics
            cache_operations = None
            cache_duration = None
            if self.session_metrics:
                cache_operations = self.session_metrics.Counter(
                    "build_cache_operations_total",
                    "Total build cache operations",
                    ["operation", "result"],
                )
                cache_duration = self.session_metrics.Histogram(
                    "build_cache_operation_duration_seconds",
                    "Build cache operation duration",
                )

            # Check for cached build result
            progress_context.start_checkpoint("Cache Check")
            progress_context.log("Checking for cached build result", "info")

            # Try to use cached build result first (most specific cache)
            if cache_duration:
                with cache_duration.time():
                    cached_build_path = self.cache_service.get_cached_build_result(
                        keymap_file, config_file, config
                    )
            else:
                cached_build_path = self.cache_service.get_cached_build_result(
                    keymap_file, config_file, config
                )

            if cached_build_path:
                if cache_operations:
                    cache_operations.labels("lookup", "hit").inc()

                progress_context.log(
                    "Found cached build - using cached artifacts", "info"
                )
                progress_context.complete_checkpoint("Cache Check")

                output_files = self._collect_files(cached_build_path, output_dir)

                result = BuildResult(
                    success=True,
                    output_files=output_files,
                )
                # Set unified success messages for cached builds
                result.set_success_messages("zmk_west", was_cached=True)
                return result

            if cache_operations:
                cache_operations.labels("lookup", "miss").inc()

            progress_context.log(
                "Cache miss - proceeding with fresh compilation", "info"
            )
            progress_context.complete_checkpoint("Cache Check")

            # Extract board information for progress tracking
            board_info = self._extract_board_info_from_config(config)
            progress_context.log(
                f"Building for {board_info['total_boards']} boards: {', '.join(board_info.get('board_names', []))}",
                "info",
            )

            # Setup workspace with progress
            progress_context.start_checkpoint("Workspace Setup")
            progress_context.log("Setting up ZMK workspace", "info")

            # Try to use cached workspace
            workspace_path, cache_used, cache_type = (
                self.workspace_setup_service.get_or_create_workspace(
                    keymap_file,
                    config_file,
                    config,
                    self.cache_service.get_cached_workspace,
                    None,
                )
            )
            if not workspace_path:
                self.logger.error("Workspace setup failed")
                return BuildResult(success=False, errors=["Workspace setup failed"])

            progress_context.complete_checkpoint("Workspace Setup")

            # Run compilation with individual board tracking
            self.logger.info(
                "Starting ZMK west compilation for %d boards",
                board_info["total_boards"],
            )

            if self.session_metrics:
                docker_operations = self.session_metrics.Counter(
                    "docker_operations_total",
                    "Total Docker operations",
                    ["operation", "result"],
                )
                docker_duration = self.session_metrics.Histogram(
                    "docker_operation_duration_seconds", "Docker operation duration"
                )
                with docker_duration.time():
                    compilation_success = self._run_compilation(
                        workspace_path,
                        config,
                        output_dir,
                        cache_used,
                        cache_type,
                        None,  # progress_callback - let compilation handle its own progress
                        board_info,
                        progress_context,
                    )
                if compilation_success:
                    docker_operations.labels("compilation", "success").inc()
                else:
                    docker_operations.labels("compilation", "failed").inc()
            else:
                compilation_success = self._run_compilation(
                    workspace_path,
                    config,
                    output_dir,
                    cache_used,
                    cache_type,
                    None,  # progress_callback - let compilation handle its own progress
                    board_info,
                    progress_context,
                )

            # Individual board checkpoints are completed within _run_compilation

            # Cache workspace dependencies if it was created fresh (not from cache)
            progress_context.start_checkpoint("Caching Results")

            if not cache_used:
                progress_context.log("Caching workspace for future builds", "info")
                self.cache_service.cache_workspace(
                    workspace_path,
                    config,
                )
            elif (
                cache_type == "repo_only" and self.cache_service.workspace_cache_service
            ):
                progress_context.log("Updating branch-specific cache", "info")
                # Update progress coordinator for workspace cache saving
                self.cache_service.cache_workspace_repo_branch_only(
                    workspace_path,
                    config,
                )

            # Always try to collect artifacts, even on build failure (for debugging)
            progress_context.log("Collecting build artifacts", "info")
            if self.session_metrics:
                artifact_duration = self.session_metrics.Histogram(
                    "artifact_collection_duration_seconds",
                    "Artifact collection duration",
                )
                with artifact_duration.time():
                    output_files = self._collect_files(workspace_path, output_dir)
            else:
                output_files = self._collect_files(workspace_path, output_dir)

            if not compilation_success:
                self.logger.error(
                    "Compilation failed, returning partial results for debugging"
                )
                return BuildResult(
                    success=False,
                    errors=["Compilation failed"],
                    output_files=output_files,  # Include partial artifacts for debugging
                )

            # Cache the successful build result
            progress_context.log("Caching build result for future use", "info")
            self.cache_service.cache_build_result(
                keymap_file,
                config_file,
                config,
                workspace_path,
            )

            progress_context.complete_checkpoint("Caching Results")

            # Create build-info.json in artifacts directory
            if output_files.artifacts_dir:
                try:
                    # Get git head hash from the workspace if available
                    head_hash = None
                    git_dir = workspace_path / "zmk" / ".git"
                    if git_dir.exists():
                        try:
                            head_file = git_dir / "HEAD"
                            if head_file.exists():
                                head_ref = head_file.read_text().strip()
                                if head_ref.startswith("ref: "):
                                    # It's a reference, resolve it
                                    ref_path = git_dir / head_ref[5:]
                                    if ref_path.exists():
                                        head_hash = ref_path.read_text().strip()
                                else:
                                    # It's a direct hash
                                    head_hash = head_ref
                        except Exception as e:
                            self.logger.debug("Failed to get git head hash: %s", e)

                    # Calculate compilation duration
                    compilation_duration = time.time() - compilation_start_time

                    create_build_info_file(
                        artifacts_dir=output_files.artifacts_dir,
                        keymap_file=keymap_file,
                        config_file=config_file,
                        json_file=json_file,
                        repository=config.repository,
                        branch=config.branch,
                        head_hash=head_hash,
                        build_mode="zmk_config",
                        uf2_files=output_files.uf2_files,
                        compilation_duration=compilation_duration,
                    )
                except Exception as e:
                    self.logger.warning("Failed to create build-info.json: %s", e)

            build_result = BuildResult(
                success=True,
                output_files=output_files,
            )
            # Set unified success messages for fresh builds
            build_result.set_success_messages("zmk_west", was_cached=False)

            # Record final compilation metrics
            if self.session_metrics:
                artifacts_generated = self.session_metrics.Gauge(
                    "artifacts_generated", "Number of artifacts generated"
                )
                firmware_size = self.session_metrics.Gauge(
                    "firmware_size_bytes", "Firmware file size in bytes"
                )

                artifacts_generated.set(len(output_files.uf2_files))
                # Calculate total firmware size from all UF2 files
                total_firmware_size = sum(
                    uf2_file.stat().st_size
                    for uf2_file in output_files.uf2_files
                    if uf2_file.exists()
                )
                firmware_size.set(total_firmware_size)

            self.logger.info("ZMK compilation completed successfully")
            return build_result

        except Exception as e:
            exc_info = self.logger.isEnabledFor(logging.DEBUG)
            self.logger.error("Compilation failed: %s", e, exc_info=exc_info)
            return BuildResult(success=False, errors=[str(e)])

    def compile_from_json(
        self,
        json_file: Path,
        output_dir: Path,
        config: CompilationConfigUnion,
        keyboard_profile: "KeyboardProfile",
        progress_callback: CompilationProgressCallback | None = None,
    ) -> BuildResult:
        """Execute compilation from JSON layout file.

        This method reads the JSON file and delegates to compile_from_data
        following the unified input/output patterns.
        """
        self.logger.info("Starting JSON to firmware compilation")

        try:
            # Load layout data directly from JSON file
            from glovebox.adapters import create_file_adapter
            from glovebox.layout.utils.json_operations import load_layout_file

            file_adapter = create_file_adapter()
            layout_data = load_layout_file(json_file, file_adapter)

            # Delegate to memory-first method
            return self.compile_from_data(
                layout_data=layout_data,
                output_dir=output_dir,
                config=config,
                keyboard_profile=keyboard_profile,
                progress_callback=progress_callback,
            )

        except Exception as e:
            exc_info = self.logger.isEnabledFor(logging.DEBUG)
            self.logger.error("JSON compilation failed: %s", e, exc_info=exc_info)
            return BuildResult(success=False, errors=[str(e)])

    def compile_from_data(
        self,
        layout_data: "LayoutData",
        output_dir: Path,
        config: CompilationConfigUnion,
        keyboard_profile: "KeyboardProfile",
        progress_callback: CompilationProgressCallback | None = None,
    ) -> BuildResult:
        """Execute compilation from layout data (memory-first pattern).

        This is the memory-first method that takes layout data as input
        and returns content in the result object, following the unified
        input/output patterns established in Phase 1/2 refactoring.

        Args:
            layout_data: Layout data object for compilation
            output_dir: Output directory for build artifacts
            config: Compilation configuration
            keyboard_profile: Keyboard profile for dynamic generation
            progress_callback: Optional callback for compilation progress updates

        Returns:
            BuildResult: Results of compilation with generated content
        """
        self.logger.info("Starting compilation from layout data")

        try:
            # Convert layout data to keymap and config content
            from glovebox.compilation.helpers import (
                convert_layout_data_to_keymap_content,
            )

            keymap_content, config_content, conversion_result = (
                convert_layout_data_to_keymap_content(
                    layout_data=layout_data,
                    keyboard_profile=keyboard_profile,
                    session_metrics=self.session_metrics,
                )
            )

            if not conversion_result.success:
                return conversion_result

            # Ensure content was generated successfully (type safety)
            assert keymap_content is not None, (
                "Keymap content should be generated on success"
            )
            assert config_content is not None, (
                "Config content should be generated on success"
            )

            # Create temporary files for ZMK West build process
            # ZMK West compilation requires actual files in a workspace
            import tempfile
            from pathlib import Path

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                keymap_file = temp_path / "keymap.keymap"
                config_file = temp_path / "config.conf"

                # Write content to temporary files
                keymap_file.write_text(keymap_content, encoding="utf-8")
                config_file.write_text(config_content, encoding="utf-8")

                # Execute compilation using the generated files
                return self.compile(
                    keymap_file=keymap_file,
                    config_file=config_file,
                    output_dir=output_dir,
                    config=config,
                    keyboard_profile=keyboard_profile,
                    progress_callback=progress_callback,
                    json_file=None,  # No original JSON file since we have data directly
                )

        except Exception as e:
            exc_info = self.logger.isEnabledFor(logging.DEBUG)
            self.logger.error("Compilation from data failed: %s", e, exc_info=exc_info)
            return BuildResult(success=False, errors=[str(e)])

    def validate_config(self, config: CompilationConfigUnion) -> bool:
        """Validate configuration."""
        return isinstance(config, ZmkCompilationConfig) and bool(config.image)

    def check_available(self) -> bool:
        """Check availability."""
        return self.docker_adapter is not None

    def _run_compilation(
        self,
        workspace_path: Path,
        config: ZmkCompilationConfig,
        output_dir: Path,
        cache_was_used: bool = False,
        cache_type: str | None = None,
        progress_callback: CompilationProgressCallback | None = None,
        board_info: dict[str, Any] | None = None,
        progress_context: "ProgressContextProtocol | None" = None,
    ) -> bool:
        """Run Docker compilation with intelligent west update logic."""
        try:
            # Check if Docker image exists, build if not
            if not self._ensure_docker_image(config):
                self.logger.error("Failed to ensure Docker image is available")
                return False

            # Generate proper build commands using build matrix
            build_commands = self._generate_build_commands(workspace_path, config)
            if not build_commands:
                return False

            # Extract board information for progress tracking
            if board_info is None:
                board_info = self._extract_board_info_from_config(config)

            board_names = board_info.get("board_names", [])
            total_boards = board_info.get("total_boards", len(build_commands))

            # Build base commands with conditional west initialization and update
            base_commands = ["cd /workspace"]

            # Check if workspace is already initialized (has .west/config)
            west_config_file = workspace_path / ".west" / "config"
            workspace_initialized = west_config_file.exists()

            if workspace_initialized:
                self.logger.info(
                    "Workspace already initialized (found .west/config), skipping west init"
                )
            else:
                self.logger.info("Initializing workspace with west init")
                base_commands.append("west init -l config")

            # Only run west update if needed based on cache usage and type
            # if not cache_was_used:
            base_commands.append("west update")
            # else:
            #     self.logger.info("Skipping west update for cached workspace")

            # Always run west zephyr-export to set up Zephyr environment variables
            base_commands.append("west zephyr-export")

            base_commands.append("west status")
            # base_commands.append("(cd modules/zmk && git rev-parse HEAD)")

            all_commands = base_commands + build_commands

            # Start dependencies update checkpoint if progress context available
            if progress_context:
                progress_context.start_checkpoint("Dependencies Update")

            # Use current user context to avoid permission issues
            user_context = DockerUserContext.detect_current_user()

            self.logger.info("Running Docker compilation")

            # Create progress middleware if progress coordinator is provided
            middlewares: list[OutputMiddleware[Any]] = []

            # Create build log middleware
            # Ensure we have a valid progress context for the middleware
            from glovebox.cli.components.noop_progress_context import (
                get_noop_progress_context,
            )

            effective_progress_context = progress_context or get_noop_progress_context()
            build_log_middleware = create_build_log_middleware(
                output_dir, effective_progress_context
            )

            # Add build log middleware first to capture all output
            middlewares.append(build_log_middleware)

            # Add board-specific progress tracking middleware if progress context available
            if progress_context and board_names:
                from glovebox.utils.stream_process import DefaultOutputMiddleware

                class BoardProgressMiddleware(DefaultOutputMiddleware):
                    """Middleware to track individual board build progress."""

                    def __init__(self) -> None:
                        super().__init__()
                        self.current_board_index = 0
                        self.boards_completed = 0
                        self.in_build_phase = False

                    def process_line(self, line: str, is_stderr: bool) -> None:
                        """Process Docker output line to track board progress."""
                        line_lower = line.lower()

                        # progress_context is guaranteed to be non-None since this middleware
                        # is only created when progress_context is not None
                        assert progress_context is not None

                        # Detect when west init/update/status commands complete
                        if "west init" in line_lower and "completed" in line_lower:
                            progress_context.complete_checkpoint("Dependencies Update")

                        # Detect when a west build command starts
                        if (
                            "west build" in line_lower
                            and "-b " in line_lower
                            and self.current_board_index < len(board_names)
                        ):
                            board_name = board_names[self.current_board_index]
                            checkpoint_name = f"Building {board_name}"
                            progress_context.start_checkpoint(checkpoint_name)
                            progress_context.log(
                                f"Starting build for {board_name}", "info"
                            )
                            self.in_build_phase = True

                        # Detect when a build completes successfully
                        if (
                            self.in_build_phase
                            and (
                                "completed successfully" in line_lower
                                or "build complete" in line_lower
                                or "firmware.uf2" in line_lower
                            )
                            and self.current_board_index < len(board_names)
                        ):
                            board_name = board_names[self.current_board_index]
                            checkpoint_name = f"Building {board_name}"
                            progress_context.complete_checkpoint(checkpoint_name)
                            progress_context.log(
                                f"Completed build for {board_name}", "info"
                            )
                            self.boards_completed += 1
                            self.current_board_index += 1
                            self.in_build_phase = False

                            # Update overall progress
                            progress_context.update_progress(
                                current=self.boards_completed,
                                total=total_boards,
                                status=f"Built {self.boards_completed}/{total_boards} boards",
                            )

                        # Detect build failures
                        if (
                            self.in_build_phase
                            and ("error:" in line_lower or "failed" in line_lower)
                            and self.current_board_index < len(board_names)
                        ):
                            board_name = board_names[self.current_board_index]
                            checkpoint_name = f"Building {board_name}"
                            progress_context.fail_checkpoint(checkpoint_name)
                            progress_context.log(
                                f"Build failed for {board_name}", "error"
                            )

                middlewares.append(BoardProgressMiddleware())

                # Create middleware that delegates to existing coordinator
                middleware = create_compilation_progress_middleware(
                    progress_context=progress_context,
                    progress_patterns=config.progress_patterns,
                    skip_west_update=cache_was_used,  # Skip west update if cache was used
                )

                middlewares.append(middleware)

            middlewares.append(LoggerOutputMiddleware(self.logger))

            chained = create_chained_middleware(middlewares)
            try:
                result: tuple[int, list[str], list[str]] = (
                    self.docker_adapter.run_container(
                        image=config.image,
                        volumes=[(str(workspace_path), "/workspace")],
                        environment={},  # {"JOBS": "4"},
                        progress_context=effective_progress_context,
                        command=["sh", "-c", "set -xeu; " + " && ".join(all_commands)],
                        middleware=chained,
                        user_context=user_context,
                    )
                )
                return_code, stdout, stderr = result

                if return_code != 0:
                    self.logger.error("Build failed with exit code %d", return_code)
                    return False

                self.logger.info("Build completed successfully")
                return True
            finally:
                # Always close the build log middleware
                build_log_middleware.close()
        except Exception as e:
            self.logger.error("Docker execution failed: %s", e)
            return False

    def _generate_build_commands(
        self, workspace_path: Path, config: ZmkCompilationConfig
    ) -> list[str]:
        """Generate west build commands from build matrix."""
        try:
            config_path = workspace_path / "config"
            app_relative_path = Path("zmk/app")

            build_yaml = workspace_path / "build.yaml"
            if not build_yaml.exists():
                self.logger.error("build.yaml not found")
                return []

            # Load and parse build matrix
            build_matrix = BuildMatrix.from_yaml(build_yaml)

            build_commands: list[str] = []

            for target in build_matrix.targets:
                build_dir = f"{target.artifact_name}"

                # Build west command
                cmd_parts = [
                    "west build",
                    f"-s {app_relative_path}",
                    f"-b {target.board}",
                    f"-d {build_dir}",
                    "--",
                ]

                # Add CMake arguments
                cmake_args = [f"-DZMK_CONFIG={config_path}"]
                if target.shield:
                    cmake_args.append(f"-DSHIELD={target.shield}")
                if target.cmake_args:
                    cmake_args.extend(target.cmake_args)
                if target.snippet:
                    cmake_args.append(f"-DZMK_EXTRA_MODULES={target.snippet}")

                cmd_parts.extend(cmake_args)
                build_commands.append(" ".join(cmd_parts))

            self.logger.info("Generated %d build commands", len(build_commands))
            return build_commands

        except Exception as e:
            self.logger.error("Failed to generate build commands: %s", e)
            return []

    def _extract_board_info_from_config(
        self, config: ZmkCompilationConfig
    ) -> dict[str, Any]:
        """Extract board information from ZmkCompilationConfig for early progress tracking."""
        try:
            # Extract board names from build matrix in config
            if config.build_matrix and config.build_matrix.targets:
                board_names = [target.board for target in config.build_matrix.targets]
                total_boards = len(board_names)

                self.logger.info(
                    "Detected %d boards from config: %s",
                    total_boards,
                    ", ".join(board_names),
                )

                return {
                    "total_boards": total_boards,
                    "board_names": board_names,
                }
            else:
                # Fallback to default single board
                self.logger.info(
                    "No build matrix in config, using default single board"
                )
                return {"total_boards": 1, "board_names": []}

        except Exception as e:
            self.logger.error("Error extracting board info from config: %s", e)
            return {"total_boards": 1, "board_names": []}

    def _collect_files(
        self, workspace_path: Path, output_dir: Path
    ) -> FirmwareOutputFiles:
        """Collect firmware files from build directories determined by build matrix."""
        output_dir.mkdir(parents=True, exist_ok=True)
        uf2_files: list[Path] = []
        artifacts_dir = None
        collected_items = []

        try:
            # Use build matrix resolver to determine expected build directories
            build_yaml = workspace_path / "build.yaml"
            if not build_yaml.exists():
                self.logger.error(
                    "build.yaml not found, cannot determine build directories"
                )
                return FirmwareOutputFiles(
                    output_dir=output_dir, uf2_files=[], artifacts_dir=None
                )

            build_matrix = BuildMatrix.from_yaml(build_yaml)

            # Look for build directories based on build matrix targets and copy artifacts
            for target in build_matrix.targets:
                build_dir_name = target.artifact_name
                build_path = workspace_path / build_dir_name
                if not build_path.is_dir():
                    self.logger.warning(
                        "Expected build directory not found: %s", build_path
                    )
                    continue

                try:
                    cur_build_out = output_dir / build_dir_name
                    cur_build_out.mkdir(parents=True, exist_ok=True)

                    if artifacts_dir is None:
                        artifacts_dir = output_dir

                    # Copy firmware files and other artifacts
                    build_collected = self._copy_build_artifacts(
                        build_path, cur_build_out, build_dir_name
                    )
                    collected_items.extend(build_collected)

                except Exception as e:
                    self.logger.warning(
                        "Failed to copy build directory %s: %s", build_path, e
                    )

            # After copying all artifacts, find UF2 files at the base of output directory
            for uf2_file in output_dir.glob("*.uf2"):
                uf2_files.append(uf2_file)
                filename_lower = uf2_file.name.lower()
                if "lh" in filename_lower or "lf" in filename_lower:
                    self.logger.debug("Found left hand UF2: %s", uf2_file)
                elif "rh" in filename_lower:
                    self.logger.debug("Found right hand UF2: %s", uf2_file)
                else:
                    self.logger.debug("Found UF2 file: %s", uf2_file)

        except Exception as e:
            self.logger.error(
                "Failed to resolve build matrix for artifact collection: %s", e
            )

        if collected_items:
            self.logger.info("Collected %d ZMK artifacts", len(collected_items))
        else:
            self.logger.warning("No build artifacts found in workspace")

        return FirmwareOutputFiles(
            output_dir=output_dir,
            uf2_files=uf2_files,
            artifacts_dir=artifacts_dir,
        )

    def _copy_build_artifacts(
        self, build_path: Path, cur_build_out: Path, build_dir_name: str
    ) -> list[str]:
        """Copy artifacts from a single build directory."""
        collected_items = []

        # Define file mappings: [source_path_from_zephyr, destination_filename]
        file_mappings = [
            # Firmware files
            ["zmk.uf2", "zmk.uf2"],
            ["zmk.hex", "zmk.hex"],
            ["zmk.bin", "zmk.bin"],
            ["zmk.elf", "zmk.elf"],
            # Configuration and debug files
            [".config", "zmk.kconfig"],
            ["zephyr.dts", "zmk.dts"],
            ["zephyr.dts.pre", "zmk.dts.pre"],
            ["include/generated/devicetree_generated.h", "devicetree_generated.h"],
        ]

        for src_path, dst_filename in file_mappings:
            src_file = build_path / "zephyr" / src_path
            dst_file = cur_build_out / dst_filename

            if src_file.exists():
                try:
                    shutil.copy2(src_file, dst_file)
                    collected_items.append(f"{build_dir_name}/{dst_filename}")
                except Exception as e:
                    self.logger.warning(
                        "Failed to copy %s to %s: %s", src_file, dst_file, e
                    )

        # Copy UF2 to base output directory with build directory name
        uf2_source = build_path / "zephyr" / "zmk.uf2"
        if uf2_source.exists():
            base_uf2 = cur_build_out.parent / f"{build_dir_name}.uf2"
            try:
                shutil.copy2(uf2_source, base_uf2)
                collected_items.append(f"{build_dir_name}.uf2")
            except Exception as e:
                self.logger.warning("Failed to copy UF2 to base: %s", e)

        return collected_items

    def _ensure_docker_image(self, config: ZmkCompilationConfig) -> bool:
        """Ensure Docker image exists, pull if not found."""
        try:
            # Parse image name and tag
            image_parts = config.image.split(":")
            image_name = image_parts[0]
            image_tag = image_parts[1] if len(image_parts) > 1 else "latest"

            # Check cache for recent image verification
            image_cache_key = CacheKey.from_parts("docker_image", image_name, image_tag)
            if self.cache_manager:
                cached_verification = self.cache_manager.get(image_cache_key)

                if cached_verification:
                    return True

            # Check if image exists
            if self.docker_adapter.image_exists(image_name, image_tag):
                # Cache verification for 1 hour to avoid repeated checks
                if self.cache_manager:
                    self.cache_manager.set(image_cache_key, True, ttl=3600)  # 1 hour
                return True

            self.logger.info("Docker image not found, pulling: %s", config.image)

            # Pull the image using the new pull_image method with middleware to show progress
            from glovebox.cli.components.noop_progress_context import (
                get_noop_progress_context,
            )

            middleware = DefaultOutputMiddleware()
            noop_progress_context = get_noop_progress_context()
            result: tuple[int, list[str], list[str]] = self.docker_adapter.pull_image(
                image_name=image_name,
                progress_context=noop_progress_context,
                image_tag=image_tag,
                middleware=middleware,
            )

            if result[0] == 0:
                self.logger.info("Successfully pulled Docker image: %s", config.image)
                # Cache successful pull for 1 hour
                if self.cache_manager:
                    self.cache_manager.set(image_cache_key, True, ttl=3600)  # 1 hour
                return True
            else:
                self.logger.error(
                    "Failed to pull Docker image: %s (exit code: %d)",
                    config.image,
                    result[0],
                )
                return False

        except Exception as e:
            self.logger.error("Error ensuring Docker image: %s", e)
            return False


def create_zmk_west_service(
    docker_adapter: DockerAdapterProtocol,
    user_config: UserConfig,
    file_adapter: FileAdapterProtocol,
    cache_manager: CacheManager,
    session_metrics: MetricsProtocol,
    workspace_cache_service: ZmkWorkspaceCacheService | None = None,
    build_cache_service: CompilationBuildCacheService | None = None,
    default_progress_callback: "CompilationProgressCallback | None" = None,
) -> ZmkWestService:
    """Create ZMK West service with dual cache management and metrics.

    Args:
        docker_adapter: Docker adapter for container operations
        user_config: User configuration with cache settings
        file_adapter: File adapter for file operations
        cache_manager: Optional cache manager instance for both cache services
        workspace_cache_service: Optional workspace cache service
        build_cache_service: Optional build cache service
        session_metrics: Optional session metrics for tracking operations
        default_progress_callback: Optional default progress callback for compilation tracking

    Returns:
        Configured ZmkWestService instance
    """
    return ZmkWestService(
        docker_adapter=docker_adapter,
        user_config=user_config,
        file_adapter=file_adapter,
        cache_manager=cache_manager,
        session_metrics=session_metrics,
        default_progress_callback=default_progress_callback,
    )

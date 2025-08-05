"""Tests for MoergoNixService compilation service."""

import logging
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from glovebox.compilation.models import MoergoCompilationConfig, ZmkCompilationConfig
from glovebox.compilation.services.moergo_nix_service import (
    MoergoNixService,
    create_moergo_nix_service,
)
from glovebox.core.cache import create_default_cache
from glovebox.core.metrics.session_metrics import SessionMetrics
from glovebox.firmware.models import BuildResult, FirmwareOutputFiles
from glovebox.layout.models.results import LayoutResult
from glovebox.models.docker_path import DockerPath
from glovebox.protocols import DockerAdapterProtocol, FileAdapterProtocol


pytestmark = [pytest.mark.docker, pytest.mark.integration]


@pytest.fixture
def mock_docker_adapter():
    """Create a mock Docker adapter for testing."""
    adapter = Mock(spec=DockerAdapterProtocol)
    adapter.run_container.return_value = (0, [], [])  # success by default
    adapter.image_exists.return_value = True
    adapter.build_image.return_value = (0, [], [])
    return adapter


@pytest.fixture
def mock_file_adapter():
    """Create a mock file adapter for testing."""
    adapter = Mock(spec=FileAdapterProtocol)
    adapter.check_exists.return_value = True
    adapter.read_text.return_value = "mock content"
    adapter.write_text.return_value = None
    return adapter


@pytest.fixture
def mock_session_metrics():
    """Create a mock session metrics for testing."""
    cache_manager = create_default_cache(tag="test")
    return SessionMetrics(cache_manager=cache_manager, session_uuid="test-session")


@pytest.fixture
def successful_layout_result(temp_files):
    """Create a successful LayoutResult for testing."""
    return LayoutResult(
        success=True,
        messages=["Layout generation successful"],
        keymap_path=temp_files["keymap"],
        conf_path=temp_files["config"],
        json_path=temp_files["json"],
        profile_name="test-profile",
        layer_count=4,
    )


@pytest.fixture
def failing_layout_result():
    """Create a failing LayoutResult for testing."""
    return LayoutResult(
        success=False,
        errors=["Layout generation failed", "Invalid JSON format"],
        messages=[],
        keymap_path=None,
        conf_path=None,
        json_path=None,
        profile_name=None,
        layer_count=None,
    )


@pytest.fixture
def moergo_service(mock_docker_adapter, mock_file_adapter, mock_session_metrics):
    """Create a MoergoNixService with mocked dependencies."""
    return MoergoNixService(
        docker_adapter=mock_docker_adapter,
        file_adapter=mock_file_adapter,
        session_metrics=mock_session_metrics,
    )


@pytest.fixture
def mock_keyboard_profile():
    """Create a mock keyboard profile for testing."""
    profile = Mock()
    profile.load_toolchain_file.return_value = "nix toolchain content"
    profile.get_keyboard_directory.return_value = Path("/fake/keyboard/dir")
    return profile


@pytest.fixture
def mock_layout_service(successful_layout_result):
    """Create a mock layout service for testing."""
    service = Mock()
    service.compile.return_value = successful_layout_result
    return service


@pytest.fixture
def sample_moergo_config():
    """Create a sample MoergoCompilationConfig for testing."""
    return MoergoCompilationConfig(
        image_="test-moergo-image",
        repository="moergo-sc/zmk",
        branch="v25.05",
    )


@pytest.fixture
def sample_zmk_config():
    """Create a sample ZmkCompilationConfig for testing."""
    return ZmkCompilationConfig(
        image_="zmkfirmware/zmk-build-arm:stable",
        repository="zmkfirmware/zmk",
        branch="main",
    )


@pytest.fixture
def temp_files(tmp_path):
    """Create temporary test files."""
    keymap_file = tmp_path / "test.keymap"
    config_file = tmp_path / "test.conf"
    json_file = tmp_path / "test.json"
    output_dir = tmp_path / "output"

    keymap_file.write_text("test keymap content")
    config_file.write_text("test config content")
    json_file.write_text('{"keyboard": "glove80", "title": "Test Layout"}')
    output_dir.mkdir()

    return {
        "keymap": keymap_file,
        "config": config_file,
        "json": json_file,
        "output_dir": output_dir,
    }


class TestMoergoNixServiceInit:
    """Test MoergoNixService initialization."""

    def test_service_creation(self, moergo_service):
        """Test service can be created with docker adapter."""
        assert moergo_service.docker_adapter is not None
        assert moergo_service.file_adapter is not None
        assert isinstance(moergo_service.logger, logging.Logger)

    def test_create_moergo_nix_service_factory(
        self, mock_docker_adapter, mock_file_adapter, mock_session_metrics
    ):
        """Test factory function creates service correctly."""
        service = create_moergo_nix_service(
            mock_docker_adapter, mock_file_adapter, mock_session_metrics
        )

        assert isinstance(service, MoergoNixService)
        assert service.docker_adapter is mock_docker_adapter


class TestMoergoNixServiceBasicMethods:
    """Test basic service methods."""

    def test_validate_config_valid_moergo(self, moergo_service, sample_moergo_config):
        """Test config validation with valid MoergoCompilationConfig."""
        service = moergo_service

        result = service.validate_config(sample_moergo_config)

        assert result is True

    def test_validate_config_invalid_type(self, moergo_service, sample_zmk_config):
        """Test config validation with wrong config type."""
        service = moergo_service

        result = service.validate_config(sample_zmk_config)

        assert result is False

    def test_validate_config_no_image(self, moergo_service):
        """Test config validation with empty image."""
        service = moergo_service
        config = MoergoCompilationConfig(image_="")

        result = service.validate_config(config)

        assert result is False

    def test_check_available_with_adapter(self, moergo_service):
        """Test availability check with valid adapter."""
        service = moergo_service

        result = service.check_available()

        assert result is True

    def test_check_available_no_adapter(self):
        """Test availability check with None adapter."""
        from glovebox.compilation.services.moergo_nix_service import MoergoNixService

        service = MoergoNixService(
            docker_adapter=None,  # type: ignore[arg-type]
            file_adapter=None,  # type: ignore[arg-type]
            session_metrics=Mock(),
        )

        result = service.check_available()

        assert result is False


class TestMoergoNixServiceCompile:
    """Test main compile method."""

    @patch("tempfile.mkdtemp")
    @patch("shutil.copy2")
    def test_compile_success(
        self,
        mock_copy,
        mock_mkdtemp,
        moergo_service,
        mock_keyboard_profile,
        sample_moergo_config,
        temp_files,
    ):
        """Test successful compilation."""
        # Setup mocks
        mock_mkdtemp.return_value = "/tmp/workspace"
        service = moergo_service

        # Mock workspace setup and compilation
        with (
            patch.object(service, "_setup_workspace") as mock_setup,
            patch.object(service, "_run_compilation") as mock_run,
            patch.object(service, "_collect_files") as mock_collect,
        ):
            workspace_path = DockerPath(
                host_path=Path("/tmp/workspace"),
                container_path="/workspace",
            )
            mock_setup.return_value = workspace_path
            mock_run.return_value = True
            mock_collect.return_value = FirmwareOutputFiles(
                output_dir=temp_files["output_dir"],
                uf2_files=[temp_files["output_dir"] / "test.uf2"],
            )

            result = service.compile(
                keymap_file=temp_files["keymap"],
                config_file=temp_files["config"],
                output_dir=temp_files["output_dir"],
                config=sample_moergo_config,
                keyboard_profile=mock_keyboard_profile,
            )

            assert result.success is True
            assert len(result.messages) > 0
            assert "Generated 1 firmware file" in result.messages[0]

    def test_compile_invalid_config_type(
        self,
        moergo_service,
        mock_docker_adapter,
        mock_keyboard_profile,
        sample_zmk_config,
        temp_files,
    ):
        """Test compilation with invalid config type."""
        service = moergo_service

        result = service.compile(
            keymap_file=temp_files["keymap"],
            config_file=temp_files["config"],
            output_dir=temp_files["output_dir"],
            config=sample_zmk_config,
            keyboard_profile=mock_keyboard_profile,
        )

        assert result.success is False
        assert "Invalid config type for Moergo compilation" in result.errors

    @patch("tempfile.mkdtemp")
    def test_compile_workspace_setup_failure(
        self,
        mock_mkdtemp,
        moergo_service,
        mock_docker_adapter,
        mock_keyboard_profile,
        sample_moergo_config,
        temp_files,
    ):
        """Test compilation when workspace setup fails."""
        mock_mkdtemp.return_value = "/tmp/workspace"
        service = moergo_service

        with patch.object(service, "_setup_workspace") as mock_setup:
            mock_setup.return_value = None

            result = service.compile(
                keymap_file=temp_files["keymap"],
                config_file=temp_files["config"],
                output_dir=temp_files["output_dir"],
                config=sample_moergo_config,
                keyboard_profile=mock_keyboard_profile,
            )

            assert result.success is False
            assert "Workspace setup failed" in result.errors

    @patch("tempfile.mkdtemp")
    def test_compile_compilation_failure_with_artifacts(
        self,
        mock_mkdtemp,
        moergo_service,
        mock_docker_adapter,
        mock_keyboard_profile,
        sample_moergo_config,
        temp_files,
    ):
        """Test compilation failure but with artifact collection."""
        mock_mkdtemp.return_value = "/tmp/workspace"
        service = moergo_service

        with (
            patch.object(service, "_setup_workspace") as mock_setup,
            patch.object(service, "_run_compilation") as mock_run,
            patch.object(service, "_collect_files") as mock_collect,
        ):
            workspace_path = DockerPath(
                host_path=Path("/tmp/workspace"),
                container_path="/workspace",
            )
            mock_setup.return_value = workspace_path
            mock_run.return_value = False  # Compilation fails
            mock_collect.return_value = FirmwareOutputFiles(
                output_dir=temp_files["output_dir"],
                uf2_files=[],  # No firmware files
                artifacts_dir=temp_files["output_dir"],  # But has partial artifacts
            )

            result = service.compile(
                keymap_file=temp_files["keymap"],
                config_file=temp_files["config"],
                output_dir=temp_files["output_dir"],
                config=sample_moergo_config,
                keyboard_profile=mock_keyboard_profile,
            )

            assert result.success is False
            assert "Compilation failed" in result.errors
            assert result.output_files is not None  # Partial artifacts included

    def test_compile_exception_handling(
        self,
        moergo_service,
        mock_docker_adapter,
        mock_keyboard_profile,
        sample_moergo_config,
        temp_files,
    ):
        """Test exception handling in compile method."""
        service = moergo_service

        with patch.object(service, "_setup_workspace") as mock_setup:
            mock_setup.side_effect = Exception("Setup error")

            result = service.compile(
                keymap_file=temp_files["keymap"],
                config_file=temp_files["config"],
                output_dir=temp_files["output_dir"],
                config=sample_moergo_config,
                keyboard_profile=mock_keyboard_profile,
            )

            assert result.success is False
            assert "Setup error" in result.errors[0]


class TestMoergoNixServiceCompileFromData:
    """Test memory-first compile_from_data method."""

    @patch("glovebox.compilation.helpers.convert_layout_data_to_keymap_content")
    def test_compile_from_data_success(
        self,
        mock_convert_layout,
        moergo_service,
        mock_docker_adapter,
        mock_keyboard_profile,
        sample_moergo_config,
        temp_files,
    ):
        """Test successful compilation from layout data dictionary."""
        # Mock the conversion helper to return successful content
        mock_convert_layout.return_value = (
            "mock keymap content",
            "mock config content",
            BuildResult(success=True, messages=["Conversion successful"]),
        )

        service = moergo_service

        # Mock the underlying compile_from_content method
        with patch.object(service, "compile_from_content") as mock_compile:
            expected_result = BuildResult(
                success=True, messages=["Compilation success"]
            )
            mock_compile.return_value = expected_result

            # Test memory-first API - takes dict instead of file path
            layout_data = {
                "keyboard": "glove80",
                "layout": "test_layout",
                "layers": [{"name": "base", "bindings": ["&kp A"]}],
            }

            result = service.compile_from_data(
                layout_data=layout_data,
                output_dir=temp_files["output_dir"],
                config=sample_moergo_config,
                keyboard_profile=mock_keyboard_profile,
            )

            assert result.success is True
            assert len(result.messages) > 0

            # Verify helper was called with layout data
            mock_convert_layout.assert_called_once()
            call_args = mock_convert_layout.call_args
            assert call_args[1]["layout_data"] == layout_data

            # Verify compile_from_content was called with generated content
            mock_compile.assert_called_once()
            compile_call_args = mock_compile.call_args
            assert compile_call_args[1]["keymap_content"] == "mock keymap content"
            assert compile_call_args[1]["config_content"] == "mock config content"

    @patch("glovebox.compilation.helpers.convert_layout_data_to_keymap_content")
    def test_compile_from_data_layout_generation_failure(
        self,
        mock_convert_layout,
        moergo_service,
        mock_docker_adapter,
        mock_keyboard_profile,
        sample_moergo_config,
        temp_files,
    ):
        """Test compilation when layout data conversion fails."""
        # Mock the conversion helper to return failure
        mock_convert_layout.return_value = (
            None,
            None,
            BuildResult(
                success=False,
                errors=["Layout generation failed", "Invalid data format"],
            ),
        )

        service = moergo_service

        layout_data = {"invalid": "layout_data"}

        result = service.compile_from_data(
            layout_data=layout_data,
            output_dir=temp_files["output_dir"],
            config=sample_moergo_config,
            keyboard_profile=mock_keyboard_profile,
        )

        assert result.success is False
        assert "Layout generation failed" in result.errors

    def test_compile_from_data_validation_error(
        self,
        moergo_service,
        mock_docker_adapter,
        mock_keyboard_profile,
        sample_moergo_config,
        temp_files,
    ):
        """Test compilation with invalid layout data structure."""
        service = moergo_service

        # Test with completely invalid data structure
        invalid_data = "not a dictionary"

        result = service.compile_from_data(
            layout_data=invalid_data,
            output_dir=temp_files["output_dir"],
            config=sample_moergo_config,
            keyboard_profile=mock_keyboard_profile,
        )

        assert result.success is False
        assert len(result.errors) > 0

    @patch("glovebox.compilation.helpers.convert_layout_data_to_keymap_content")
    def test_compile_from_data_partial_content_generation(
        self,
        mock_convert_layout,
        moergo_service,
        mock_docker_adapter,
        mock_keyboard_profile,
        sample_moergo_config,
        temp_files,
    ):
        """Test compilation when content generation returns partial content."""
        # Mock the conversion helper to return only partial content
        mock_convert_layout.return_value = (
            "keymap content",
            None,  # Missing config content
            BuildResult(
                success=False,
                errors=["Failed to generate complete content from data"],
            ),
        )

        service = moergo_service

        layout_data = {
            "keyboard": "glove80",
            "layout": "test_layout",
            "layers": [],  # Empty layers
        }

        result = service.compile_from_data(
            layout_data=layout_data,
            output_dir=temp_files["output_dir"],
            config=sample_moergo_config,
            keyboard_profile=mock_keyboard_profile,
        )

        assert result.success is False
        assert "Failed to generate complete content from data" in result.errors

    @patch("glovebox.compilation.helpers.convert_layout_data_to_keymap_content")
    def test_compile_from_data_exception_handling(
        self,
        mock_convert_layout,
        moergo_service,
        mock_docker_adapter,
        mock_keyboard_profile,
        sample_moergo_config,
        temp_files,
    ):
        """Test exception handling in compile_from_data method."""
        service = moergo_service

        # Mock the helper to raise an exception
        mock_convert_layout.side_effect = Exception("Layout service error")

        layout_data = {"keyboard": "glove80", "layout": "test", "layers": []}

        result = service.compile_from_data(
            layout_data=layout_data,
            output_dir=temp_files["output_dir"],
            config=sample_moergo_config,
            keyboard_profile=mock_keyboard_profile,
        )

        assert result.success is False
        assert "Layout service error" in result.errors[0]


class TestMoergoNixServiceSetupWorkspace:
    """Test _setup_workspace method."""

    def test_setup_workspace_success(
        self,
        moergo_service,
        mock_docker_adapter,
        mock_keyboard_profile,
        temp_files,
        tmp_path,
    ):
        """Test successful workspace setup."""
        service = moergo_service

        # Use real temporary directory for this test
        with patch("tempfile.mkdtemp") as mock_mkdtemp:
            workspace_dir = tmp_path / "test_workspace"
            mock_mkdtemp.return_value = str(workspace_dir)

            workspace_path = service._setup_workspace(
                temp_files["keymap"], temp_files["config"], mock_keyboard_profile
            )

            assert workspace_path is not None
            assert workspace_path.host_path == workspace_dir
            assert workspace_path.container_path == "/workspace"

            # Verify config directory was created
            config_dir = workspace_dir / "config"
            assert config_dir.exists()

            # Verify files were copied with correct names
            assert (config_dir / "glove80.keymap").exists()
            assert (config_dir / "glove80.conf").exists()
            assert (config_dir / "default.nix").exists()

            # Verify default.nix was loaded and written
            mock_keyboard_profile.load_toolchain_file.assert_called_once_with(
                "default.nix"
            )

    @patch("tempfile.mkdtemp")
    def test_setup_workspace_missing_default_nix(
        self,
        mock_mkdtemp,
        moergo_service,
        mock_docker_adapter,
        temp_files,
    ):
        """Test workspace setup when default.nix is missing."""
        mock_mkdtemp.return_value = "/tmp/test_workspace"

        # Create keyboard profile that can't load default.nix
        failing_profile = Mock()
        failing_profile.load_toolchain_file.return_value = None

        service = moergo_service

        workspace_path = service._setup_workspace(
            temp_files["keymap"], temp_files["config"], failing_profile
        )

        assert workspace_path is None

    @patch("tempfile.mkdtemp")
    @patch("shutil.copy2")
    def test_setup_workspace_copy_failure(
        self,
        mock_copy,
        mock_mkdtemp,
        moergo_service,
        mock_docker_adapter,
        mock_keyboard_profile,
        temp_files,
    ):
        """Test workspace setup when file copy fails."""
        mock_mkdtemp.return_value = "/tmp/test_workspace"
        mock_copy.side_effect = Exception("Copy failed")

        service = moergo_service

        workspace_path = service._setup_workspace(
            temp_files["keymap"], temp_files["config"], mock_keyboard_profile
        )

        assert workspace_path is None

    @patch("tempfile.mkdtemp")
    def test_setup_workspace_mkdtemp_failure(
        self,
        mock_mkdtemp,
        moergo_service,
        mock_docker_adapter,
        mock_keyboard_profile,
        temp_files,
    ):
        """Test workspace setup when temporary directory creation fails."""
        mock_mkdtemp.side_effect = Exception("Cannot create temp dir")

        service = moergo_service

        workspace_path = service._setup_workspace(
            temp_files["keymap"], temp_files["config"], mock_keyboard_profile
        )

        assert workspace_path is None


class TestMoergoNixServiceRunCompilation:
    """Test _run_compilation method."""

    def test_run_compilation_success(
        self,
        moergo_service,
        mock_docker_adapter,
        sample_moergo_config,
        tmp_path,
    ):
        """Test successful compilation run."""
        service = moergo_service
        workspace_path = DockerPath(
            host_path=Path("/tmp/workspace"),
            container_path="/workspace",
        )

        with (
            patch.object(service, "_ensure_docker_image") as mock_ensure,
            patch(
                "glovebox.models.docker.DockerUserContext.detect_current_user"
            ) as mock_detect_user,
        ):
            mock_ensure.return_value = True
            mock_user = Mock()
            mock_user.uid = 1000
            mock_user.gid = 1000
            mock_user.enable_user_mapping = False
            mock_detect_user.return_value = mock_user

            result = service._run_compilation(
                workspace_path, sample_moergo_config, tmp_path / "output"
            )

            assert result is True

            # Verify docker adapter was called with correct parameters
            mock_docker_adapter.run_container.assert_called_once()
            call_args = mock_docker_adapter.run_container.call_args
            assert call_args.kwargs["image"] == sample_moergo_config.image
            assert call_args.kwargs["command"] == ["build.sh"]
            assert "PUID" in call_args.kwargs["environment"]
            assert "REPO" in call_args.kwargs["environment"]
            assert "BRANCH" in call_args.kwargs["environment"]

    def test_run_compilation_image_ensure_failure(
        self,
        moergo_service,
        mock_docker_adapter,
        sample_moergo_config,
        tmp_path,
    ):
        """Test compilation when Docker image ensure fails."""
        service = moergo_service
        workspace_path = DockerPath(
            host_path=Path("/tmp/workspace"),
            container_path="/workspace",
        )

        with patch.object(service, "_ensure_docker_image") as mock_ensure:
            mock_ensure.return_value = False

            result = service._run_compilation(
                workspace_path, sample_moergo_config, tmp_path / "output"
            )

            assert result is False

    def test_run_compilation_container_failure(
        self,
        moergo_service,
        mock_docker_adapter,
        sample_moergo_config,
        tmp_path,
    ):
        """Test compilation when container execution fails."""
        mock_docker_adapter.run_container.return_value = (1, [], ["Build error"])

        service = moergo_service
        workspace_path = DockerPath(
            host_path=Path("/tmp/workspace"),
            container_path="/workspace",
        )

        with (
            patch.object(service, "_ensure_docker_image") as mock_ensure,
            patch(
                "glovebox.models.docker.DockerUserContext.detect_current_user"
            ) as mock_detect_user,
        ):
            mock_ensure.return_value = True
            mock_user = Mock()
            mock_user.uid = 1000
            mock_user.gid = 1000
            mock_detect_user.return_value = mock_user

            result = service._run_compilation(
                workspace_path, sample_moergo_config, tmp_path / "output"
            )

            assert result is False

    def test_run_compilation_exception_handling(
        self,
        moergo_service,
        mock_docker_adapter,
        sample_moergo_config,
        tmp_path,
    ):
        """Test compilation exception handling."""
        service = moergo_service
        workspace_path = DockerPath(
            host_path=Path("/tmp/workspace"),
            container_path="/workspace",
        )

        with patch.object(service, "_ensure_docker_image") as mock_ensure:
            mock_ensure.side_effect = Exception("Docker error")

            result = service._run_compilation(
                workspace_path, sample_moergo_config, tmp_path / "output"
            )

            assert result is False


class TestMoergoNixServiceCollectFiles:
    """Test _collect_files method."""

    def test_collect_files_with_artifacts_directory(
        self,
        moergo_service,
        mock_docker_adapter,
        tmp_path,
    ):
        """Test file collection when artifacts directory exists."""
        service = moergo_service

        # Create workspace with artifacts
        workspace_path = tmp_path / "workspace"
        artifacts_dir = workspace_path / "artifacts"
        artifacts_dir.mkdir(parents=True)

        # Create some test artifacts
        firmware_file = artifacts_dir / "glove80.uf2"
        log_file = artifacts_dir / "build.log"
        sub_dir = artifacts_dir / "sub"
        sub_dir.mkdir()
        sub_file = sub_dir / "test.txt"

        firmware_file.write_text("firmware content")
        log_file.write_text("build log")
        sub_file.write_text("sub file content")

        output_dir = tmp_path / "output"

        result = service._collect_files(workspace_path, output_dir)

        assert result.output_dir == output_dir
        assert output_dir / "glove80.uf2" in result.uf2_files
        assert result.artifacts_dir == output_dir

        # Verify files were copied
        assert (output_dir / "glove80.uf2").exists()
        assert (output_dir / "build.log").exists()
        assert (output_dir / "sub" / "test.txt").exists()

    def test_collect_files_without_artifacts_directory(
        self,
        moergo_service,
        mock_docker_adapter,
        tmp_path,
    ):
        """Test file collection when no artifacts directory exists."""
        service = moergo_service

        # Create workspace without artifacts directory
        workspace_path = tmp_path / "workspace"
        workspace_path.mkdir()

        # Create some partial files in workspace
        partial_file = workspace_path / "partial.uf2"
        log_file = workspace_path / "debug.log"
        partial_file.write_text("partial firmware")
        log_file.write_text("debug log")

        output_dir = tmp_path / "output"

        result = service._collect_files(workspace_path, output_dir)

        assert result.output_dir == output_dir
        assert len(result.uf2_files) == 1  # Found the partial UF2 file
        assert result.artifacts_dir is None

        # Verify partial files were copied
        assert (output_dir / "partial.uf2").exists()
        assert (output_dir / "debug.log").exists()

    def test_collect_files_copy_error_handling(
        self,
        moergo_service,
        mock_docker_adapter,
        tmp_path,
    ):
        """Test file collection with copy errors."""
        service = moergo_service

        # Create workspace with artifacts
        workspace_path = tmp_path / "workspace"
        artifacts_dir = workspace_path / "artifacts"
        artifacts_dir.mkdir(parents=True)

        # Create test artifacts
        firmware_file = artifacts_dir / "glove80.uf2"
        firmware_file.write_text("firmware content")

        output_dir = tmp_path / "output"

        # Mock shutil.copy2 to fail for one file
        with patch("shutil.copy2") as mock_copy:
            mock_copy.side_effect = Exception("Copy failed")

            result = service._collect_files(workspace_path, output_dir)

            # Should still return a result despite copy failures
            assert result.output_dir == output_dir
            assert len(result.uf2_files) == 0  # No firmware files due to copy failure

    def test_collect_files_existing_output_file_replacement(
        self,
        moergo_service,
        mock_docker_adapter,
        tmp_path,
    ):
        """Test file collection replaces existing output files."""
        service = moergo_service

        # Create workspace with artifacts
        workspace_path = tmp_path / "workspace"
        artifacts_dir = workspace_path / "artifacts"
        artifacts_dir.mkdir(parents=True)

        firmware_file = artifacts_dir / "glove80.uf2"
        firmware_file.write_text("new firmware")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create existing file in output
        existing_file = output_dir / "glove80.uf2"
        existing_file.write_text("old firmware")

        result = service._collect_files(workspace_path, output_dir)

        # Verify file was replaced
        assert existing_file in result.uf2_files
        assert existing_file.read_text() == "new firmware"


class TestMoergoNixServiceEnsureDockerImage:
    """Test _ensure_docker_image method."""

    def test_ensure_docker_image_already_exists(
        self,
        moergo_service,
        mock_docker_adapter,
        sample_moergo_config,
    ):
        """Test when Docker image already exists."""
        mock_docker_adapter.image_exists.return_value = True

        service = moergo_service

        with patch.object(service, "_get_versioned_image_name") as mock_get_versioned:
            mock_get_versioned.return_value = ("test-image", "v1.0.0")

            result = service._ensure_docker_image(sample_moergo_config)

            assert result is True
            assert sample_moergo_config.image == "test-image:v1.0.0"
            mock_docker_adapter.image_exists.assert_called_once_with(
                "test-image", "v1.0.0"
            )

    def test_ensure_docker_image_build_success(
        self,
        moergo_service,
        mock_docker_adapter,
        sample_moergo_config,
        tmp_path,
    ):
        """Test successful Docker image build."""
        mock_docker_adapter.image_exists.return_value = False
        mock_docker_adapter.build_image.return_value = (0, [], [])

        # Create actual directory structure for test
        keyboard_dir = tmp_path / "keyboard"
        toolchain_dir = keyboard_dir / "toolchain"
        toolchain_dir.mkdir(parents=True)

        service = moergo_service

        with (
            patch.object(service, "_get_versioned_image_name") as mock_get_versioned,
            patch.object(
                service, "_get_keyboard_profile_for_dockerfile"
            ) as mock_get_profile,
        ):
            mock_get_versioned.return_value = ("test-image", "v1.0.0")
            mock_profile = Mock()
            mock_profile.get_keyboard_directory.return_value = keyboard_dir
            mock_get_profile.return_value = mock_profile

            result = service._ensure_docker_image(sample_moergo_config)

            assert result is True
            assert sample_moergo_config.image == "test-image:v1.0.0"
            mock_docker_adapter.build_image.assert_called_once()

    def test_ensure_docker_image_build_failure(
        self,
        moergo_service,
        mock_docker_adapter,
        sample_moergo_config,
    ):
        """Test Docker image build failure."""
        mock_docker_adapter.image_exists.return_value = False
        mock_docker_adapter.build_image.return_value = (1, [], ["Build failed"])

        service = moergo_service

        with (
            patch.object(service, "_get_versioned_image_name") as mock_get_versioned,
            patch.object(
                service, "_get_keyboard_profile_for_dockerfile"
            ) as mock_get_profile,
        ):
            mock_get_versioned.return_value = ("test-image", "v1.0.0")
            mock_profile = Mock()
            mock_profile.get_keyboard_directory.return_value = Path(
                "/fake/keyboard/dir"
            )
            mock_get_profile.return_value = mock_profile

            result = service._ensure_docker_image(sample_moergo_config)

            assert result is False

    def test_ensure_docker_image_no_keyboard_profile(
        self,
        moergo_service,
        mock_docker_adapter,
        sample_moergo_config,
    ):
        """Test when keyboard profile cannot be obtained."""
        mock_docker_adapter.image_exists.return_value = False

        service = moergo_service

        with (
            patch.object(service, "_get_versioned_image_name") as mock_get_versioned,
            patch.object(
                service, "_get_keyboard_profile_for_dockerfile"
            ) as mock_get_profile,
        ):
            mock_get_versioned.return_value = ("test-image", "v1.0.0")
            mock_get_profile.return_value = None

            result = service._ensure_docker_image(sample_moergo_config)

            assert result is False

    def test_ensure_docker_image_no_keyboard_directory(
        self,
        moergo_service,
        mock_docker_adapter,
        sample_moergo_config,
    ):
        """Test when keyboard directory cannot be found."""
        mock_docker_adapter.image_exists.return_value = False

        service = moergo_service

        with (
            patch.object(service, "_get_versioned_image_name") as mock_get_versioned,
            patch.object(
                service, "_get_keyboard_profile_for_dockerfile"
            ) as mock_get_profile,
        ):
            mock_get_versioned.return_value = ("test-image", "v1.0.0")
            mock_profile = Mock()
            mock_profile.get_keyboard_directory.return_value = None
            mock_get_profile.return_value = mock_profile

            result = service._ensure_docker_image(sample_moergo_config)

            assert result is False

    def test_ensure_docker_image_exception_handling(
        self,
        moergo_service,
        mock_docker_adapter,
        sample_moergo_config,
    ):
        """Test exception handling in image ensure."""
        service = moergo_service

        with patch.object(service, "_get_versioned_image_name") as mock_get_versioned:
            mock_get_versioned.side_effect = Exception("Version error")

            result = service._ensure_docker_image(sample_moergo_config)

            assert result is False


class TestMoergoNixServiceGetVersionedImageName:
    """Test _get_versioned_image_name method."""

    def test_get_versioned_image_name_with_version(
        self,
        moergo_service,
        mock_docker_adapter,
        sample_moergo_config,
    ):
        """Test versioned image name generation with available version."""
        service = moergo_service

        with patch("glovebox._version.__version__", "1.2.3"):
            image_name, tag = service._get_versioned_image_name(sample_moergo_config)

            assert image_name == "test-moergo-image"
            assert tag == "1.2.3"

    def test_get_versioned_image_name_with_complex_version(
        self,
        moergo_service,
        mock_docker_adapter,
        sample_moergo_config,
    ):
        """Test versioned image name with complex version string."""
        service = moergo_service

        with patch("glovebox._version.__version__", "1.2.3+dev.20241201/feature"):
            image_name, tag = service._get_versioned_image_name(sample_moergo_config)

            assert image_name == "test-moergo-image"
            assert tag == "1.2.3-dev.20241201-feature"  # + and / replaced

    def test_get_versioned_image_name_import_error(
        self,
        moergo_service,
        mock_docker_adapter,
        sample_moergo_config,
    ):
        """Test versioned image name when version import fails."""
        service = moergo_service

        with patch("builtins.__import__") as mock_import:
            mock_import.side_effect = ImportError("No version module")

            image_name, tag = service._get_versioned_image_name(sample_moergo_config)

            assert image_name == "test-moergo-image"
            assert tag == "latest"

    def test_get_versioned_image_name_with_existing_tag(
        self,
        moergo_service,
        mock_docker_adapter,
    ):
        """Test versioned image name strips existing tag."""
        config = MoergoCompilationConfig(image_="test-image:old-tag")
        service = moergo_service

        with patch("glovebox._version.__version__", "2.0.0"):
            image_name, tag = service._get_versioned_image_name(config)

            assert image_name == "test-image"  # Tag removed
            assert tag == "2.0.0"


class TestMoergoNixServiceGetKeyboardProfileForDockerfile:
    """Test _get_keyboard_profile_for_dockerfile method."""

    @patch("glovebox.config.keyboard_profile.create_keyboard_profile")
    def test_get_keyboard_profile_success(
        self,
        mock_create_profile,
        moergo_service,
        mock_docker_adapter,
    ):
        """Test successful keyboard profile creation."""
        service = moergo_service

        mock_profile = Mock()
        mock_create_profile.return_value = mock_profile

        result = service._get_keyboard_profile_for_dockerfile()

        assert result is mock_profile
        mock_create_profile.assert_called_once_with("glove80")

    @patch("glovebox.config.keyboard_profile.create_keyboard_profile")
    def test_get_keyboard_profile_exception(
        self,
        mock_create_profile,
        moergo_service,
        mock_docker_adapter,
    ):
        """Test keyboard profile creation with exception."""
        service = moergo_service

        mock_create_profile.side_effect = Exception("Profile creation failed")

        result = service._get_keyboard_profile_for_dockerfile()

        assert result is None


class TestMoergoNixServiceIntegration:
    """Integration tests for complete workflows."""

    @patch("tempfile.TemporaryDirectory")
    @patch("glovebox.layout.create_layout_service")
    @pytest.mark.skip(reason="Deprecated test using old file-based layout service API")
    def test_complete_json_to_firmware_workflow(
        self,
        mock_create_layout_service,
        mock_temp_dir,
        moergo_service,
        mock_docker_adapter,
        mock_keyboard_profile,
        sample_moergo_config,
        temp_files,
        mock_layout_service,
        tmp_path,
    ):
        """Test complete JSON to firmware workflow."""
        # Setup mocks for successful compilation
        json_workspace = tmp_path / "json_workspace"
        json_workspace.mkdir()
        mock_temp_dir.return_value.__enter__.return_value = str(json_workspace)

        # Create actual generated files that the layout service returns
        generated_keymap = json_workspace / "layout.keymap"
        generated_config = json_workspace / "layout.conf"
        generated_keymap.write_text("generated keymap content")
        generated_config.write_text("generated config content")

        # Update mock layout service to return actual file paths
        layout_result = Mock()
        layout_result.success = True
        layout_result.errors = []
        layout_result.get_output_files.return_value = {
            "keymap": str(generated_keymap),
            "conf": str(generated_config),
        }
        mock_layout_service.compile.return_value = layout_result
        mock_create_layout_service.return_value = mock_layout_service

        service = moergo_service

        # Mock all the compilation steps
        with (
            patch.object(service, "_ensure_docker_image") as mock_ensure,
            patch(
                "glovebox.models.docker.DockerUserContext.detect_current_user"
            ) as mock_detect_user,
            patch("tempfile.mkdtemp") as mock_mkdtemp,
        ):
            mock_ensure.return_value = True
            mock_user = Mock()
            mock_user.uid = 1000
            mock_user.gid = 1000
            mock_detect_user.return_value = mock_user

            # Use real workspace directory
            workspace_path = tmp_path / "workspace"
            mock_mkdtemp.return_value = str(workspace_path)

            # Create artifacts in workspace for collection
            artifacts_dir = workspace_path / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            firmware_file = artifacts_dir / "glove80.uf2"
            firmware_file.write_text("test firmware")

            result = service.compile_from_json(
                json_file=temp_files["json"],
                output_dir=temp_files["output_dir"],
                config=sample_moergo_config,
                keyboard_profile=mock_keyboard_profile,
            )

            assert result.success is True

            # Verify the full workflow was executed
            mock_layout_service.compile.assert_called_once()
            mock_docker_adapter.run_container.assert_called_once()

    def test_error_recovery_workflow(
        self,
        moergo_service,
        mock_docker_adapter,
        mock_keyboard_profile,
        sample_moergo_config,
        temp_files,
    ):
        """Test error recovery and partial artifact collection."""
        service = moergo_service

        # Setup failing compilation but with partial artifacts
        with (
            patch.object(service, "_setup_workspace") as mock_setup,
            patch.object(service, "_run_compilation") as mock_run,
            patch.object(service, "_collect_files") as mock_collect,
        ):
            workspace_path = DockerPath(
                host_path=Path("/tmp/workspace"),
                container_path="/workspace",
            )
            mock_setup.return_value = workspace_path
            mock_run.return_value = False  # Compilation fails

            # But partial artifacts are collected for debugging
            mock_collect.return_value = FirmwareOutputFiles(
                output_dir=temp_files["output_dir"],
                uf2_files=[],
                artifacts_dir=None,
            )

            result = service.compile(
                keymap_file=temp_files["keymap"],
                config_file=temp_files["config"],
                output_dir=temp_files["output_dir"],
                config=sample_moergo_config,
                keyboard_profile=mock_keyboard_profile,
            )

            # Should fail but include partial artifacts
            assert result.success is False
            assert "Compilation failed" in result.errors
            assert result.output_files is not None  # Partial artifacts for debugging

"""ZMK compilation caching system.

This module implements a modern caching strategy for ZMK firmware compilation
using base dependencies caching for shared components and comprehensive
workspace cache management with rich metadata.

The caching system reduces compilation time by reusing shared dependencies
across multiple builds and provides enhanced cache operations.
"""

from typing import TYPE_CHECKING, Any

from glovebox.core.cache import create_cache_from_user_config
from glovebox.core.cache.cache_manager import CacheManager

from .compilation_build_cache_service import CompilationBuildCacheService
from .models import WorkspaceCacheMetadata, WorkspaceCacheResult
from .workspace_cache_service import ZmkWorkspaceCacheService


if TYPE_CHECKING:
    from glovebox.config.user_config import UserConfig


def create_zmk_workspace_cache_service(
    user_config: "UserConfig",
    cache_manager: CacheManager | None = None,
    session_metrics: Any = None,
) -> ZmkWorkspaceCacheService:
    """Factory function for ZMK workspace cache service.

    Args:
        user_config: User configuration instance
        cache_manager: Optional cache manager (will create if not provided)
        session_metrics: Optional SessionMetrics instance for metrics integration

    Returns:
        ZmkWorkspaceCacheService instance
    """
    if cache_manager is None:
        cache_manager = create_cache_from_user_config(
            user_config._config, tag="compilation", session_metrics=session_metrics
        )

    return ZmkWorkspaceCacheService(user_config, cache_manager, session_metrics)


def create_compilation_build_cache_service(
    user_config: "UserConfig",
    cache_manager: CacheManager | None = None,
    session_metrics: Any = None,
) -> CompilationBuildCacheService:
    """Factory function for compilation build cache service.

    Args:
        user_config: User configuration instance
        cache_manager: Optional cache manager (will create if not provided)
        session_metrics: Optional SessionMetrics instance for metrics integration

    Returns:
        CompilationBuildCacheService instance
    """
    if cache_manager is None:
        cache_manager = create_cache_from_user_config(
            user_config._config, tag="compilation", session_metrics=session_metrics
        )

    return CompilationBuildCacheService(user_config, cache_manager)


def create_compilation_cache_service(
    user_config: "UserConfig", session_metrics: Any = None
) -> tuple[CacheManager, ZmkWorkspaceCacheService, CompilationBuildCacheService]:
    """Factory function for compilation cache service with shared coordination.

    This function follows the established factory function pattern from CLAUDE.md
    and provides unified cache management for the compilation domain with both
    workspace and build cache services.

    Args:
        user_config: User configuration instance
        session_metrics: Optional SessionMetrics instance for metrics integration

    Returns:
        Tuple of (cache_manager, workspace_cache_service, build_cache_service) using shared coordination
    """
    # Use shared cache coordination for compilation domain
    cache_manager = create_cache_from_user_config(
        user_config._config, tag="compilation", session_metrics=session_metrics
    )

    # Create both cache services with shared cache
    workspace_service = create_zmk_workspace_cache_service(
        user_config, cache_manager, session_metrics
    )
    build_service = create_compilation_build_cache_service(
        user_config, cache_manager, session_metrics
    )

    return cache_manager, workspace_service, build_service


__all__ = [
    "WorkspaceCacheMetadata",
    "WorkspaceCacheResult",
    "ZmkWorkspaceCacheService",
    "CompilationBuildCacheService",
    "create_zmk_workspace_cache_service",
    "create_compilation_build_cache_service",
    "create_compilation_cache_service",
]

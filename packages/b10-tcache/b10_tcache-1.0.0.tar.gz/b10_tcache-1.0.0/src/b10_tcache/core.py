"""
TODO(SRAY):
One thing I'm not sure about is:
1) what happens if b10fs is down? Will this implementation still work. Need to check...
"""

import os
import logging
import tempfile
import shutil
import uuid
from pathlib import Path

from .environment import get_cache_filename
from .archive import create_archive, extract_archive, ArchiveError


# Configuration
TORCH_CACHE_DIR = os.getenv("TORCH_CACHE_DIR", "/tmp/torchinductor_root")
B10FS_CACHE_DIR = os.getenv("B10FS_CACHE_DIR", "/cache/model/compile_cache")
LOCAL_WORK_DIR = os.getenv("LOCAL_WORK_DIR", "/app")
MAX_CACHE_SIZE_MB = int(os.getenv("MAX_CACHE_SIZE_MB", "1024"))

logger = logging.getLogger(__name__)


class CacheError(Exception):
    """Base cache operation error."""
    pass


def load_compile_cache() -> bool:
    """Load cache from b10fs using lock-free pattern."""
    b10fs_dir = Path(B10FS_CACHE_DIR)
    torch_dir = Path(TORCH_CACHE_DIR)
    work_dir = Path(LOCAL_WORK_DIR)

    try:
        cache_filename = get_cache_filename()
        cache_file = b10fs_dir / f"{cache_filename}.latest.tar.gz"

        if not cache_file.exists():
            return False

        # Skip if already loaded
        if torch_dir.exists() and any(torch_dir.iterdir()):
            return True

        # Create temp local copy
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', dir=work_dir, delete=False) as f:
            temp_path = Path(f.name)

        try:
            shutil.copy2(cache_file, temp_path)
            extract_archive(temp_path, torch_dir)
            return True
        finally:
            temp_path.unlink(missing_ok=True)

    except Exception as e:
        logger.debug(f"Load failed: {e}")
        return False


"""
What about the case in @b10-tcache/ where a single pod finishes an inference request,
and then the client calls save_compile_cache. And while we are creating the local archive,
another inference call on the same pod is kicked off, which then modifies the torch cache.
How would this be handled? Maybe just accept that the cache will be recompiled/overwritten?
Otherwise you'd need application level coordination to ensure that the cache is not modified
while we are creating the archive, but this doesn't really seem like a good idea in terms of adoption.
"""

def save_compile_cache() -> bool:
    """Save cache using the journal pattern."""
    b10fs_dir = Path(B10FS_CACHE_DIR)
    torch_dir = Path(TORCH_CACHE_DIR)
    work_dir = Path(LOCAL_WORK_DIR)

    try:
        # Check if anything to save
        if not torch_dir.exists() or not any(torch_dir.iterdir()):
            return False

        cache_filename = get_cache_filename()
        final_file = b10fs_dir / f"{cache_filename}.latest.tar.gz"

        # micahel's pattern
        # FIXME(SR): I think there's a race here, if the rename succeeeds, the finally block will try to delete the temp file.
        # Actually I think the missing_ok=True handles this case, but need to double check.
        temp_file = b10fs_dir / f"{cache_filename}.incomplete.{uuid.uuid4()}.tar.gz"

        with tempfile.NamedTemporaryFile(suffix='.tar.gz', dir=work_dir, delete=False) as f:
            local_temp = Path(f.name)

        try:
            # Create archive locally
            create_archive(torch_dir, local_temp, MAX_CACHE_SIZE_MB)

            # Copy to b10fs (parallel copies allowed)
            b10fs_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(local_temp, temp_file)

            # Atomic rename
            temp_file.rename(final_file)

            return True

        finally:
            local_temp.unlink(missing_ok=True)
            temp_file.unlink(missing_ok=True)  # Cleanup if rename failed

    except Exception as e:
        logger.debug(f"Save failed: {e}")
        return False


def clear_local_cache() -> bool:
    """Clear local torch cache."""
    torch_dir = Path(TORCH_CACHE_DIR)

    try:
        if not torch_dir.exists():
            return True

        shutil.rmtree(torch_dir)
        return True

    except Exception as e:
        logger.debug(f"Clear failed: {e}")
        return False

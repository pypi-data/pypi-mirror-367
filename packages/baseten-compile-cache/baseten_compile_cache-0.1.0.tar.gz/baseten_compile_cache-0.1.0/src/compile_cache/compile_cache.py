from __future__ import annotations
import os
import logging
import time

TORCH_CACHE_DIR = "/tmp/torchinductor_root"
B10FS_CACHE_DIR = "/cache/model/compile_cache"
LOCAL_DIR = "/app"

logger = logging.getLogger(__name__)

def bash_command(command: str) -> None:
    """
    Execute a bash command and log the output.
    """
    logger.info(f"Executing command: {command}")
    result = os.system(command)
    if result != 0:
        raise RuntimeError(f"Command failed with exit code {result}: {command}")

def load_compile_cache() -> bool:
    """
    Load the compile cache from b10fs.
    Returns True if the cache was successfully loaded, False otherwise.
    """

    try:
        if not os.path.exists(f"{B10FS_CACHE_DIR}/cache.tar.gz"):
            logger.info(f"Compile cache was not found in {B10FS_CACHE_DIR}.")
            return False

        start_time = time.time()
        logger.info(f"Loading compile cache from b10fs at {B10FS_CACHE_DIR}/cache.tar.gz...")
        bash_command(f"cp {B10FS_CACHE_DIR}/cache.tar.gz {LOCAL_DIR}/")
        logger.info(f"Load took {time.time() - start_time:.2f} seconds.")

        start_time = time.time()
        logger.info(f"Extracting compile cache to {TORCH_CACHE_DIR}...")
        bash_command(f"tar -xzf {LOCAL_DIR}/cache.tar.gz -C /")
        logger.info(f"Extraction took {time.time() - start_time:.2f} seconds.")

        return True
    
    except Exception as e:
        logger.error(f"Failed to load compile cache: {e}")
        return False

def save_compile_cache() -> bool:
    """
    Save the compile cache for this model to b10fs.
    Returns True if the cache was successfully saved, False otherwise.
    """

    try:
        logger.info(f"Saving compile cache to b10fs...")

        start_time = time.time()
        logger.info(f"Compress and archiving cache from {TORCH_CACHE_DIR} to {LOCAL_DIR}/cache.tar.gz...")
        bash_command(f"tar -czf {LOCAL_DIR}/cache.tar.gz {TORCH_CACHE_DIR}")
        logger.info(f"Compression and archiving took {time.time() - start_time:.2f} seconds.")

        start_time = time.time()
        logger.info(f"Copying cache to b10fs at {B10FS_CACHE_DIR}/cache.tar.gz...")
        bash_command(f"cp {LOCAL_DIR}/cache.tar.gz {B10FS_CACHE_DIR}/cache.tar.gz")
        logger.info(f"Copy took {time.time() - start_time:.2f} seconds.")

        return True
    
    except Exception as e:
        logger.error(f"Failed to save compile cache: {e}")
        return False
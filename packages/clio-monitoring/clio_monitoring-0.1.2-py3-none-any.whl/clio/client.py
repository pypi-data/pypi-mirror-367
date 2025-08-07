"""Main Clio client for Playwright integration"""

import asyncio
import httpx
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import json
import os
import tempfile
import shutil
import atexit
import threading
from weakref import WeakKeyDictionary

from .config import Config
from .uploader import Uploader
from .utils import mask_sensitive_data, mask_dict
from .logger import get_logger, configure_logging
from .exceptions import (
    ClioError,
    ClioAuthError,
    ClioUploadError,
    ClioRateLimitError
)

logger = get_logger("client")


class ClioMonitor:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.clio.dev",
        retry_attempts: int = 3,
        raise_on_error: bool = False,
        verify_ssl: bool = True,
        debug: bool = False
    ):
        # Configure logging level based on debug flag
        configure_logging(debug)
        
        self.config = Config(
            api_key=api_key,
            base_url=base_url,
            retry_attempts=retry_attempts,
            raise_on_error=raise_on_error,
            verify_ssl=verify_ssl,
            debug=debug
        )
        self.uploader = Uploader(self.config)
        # Use WeakKeyDictionary to auto-cleanup when context is garbage collected
        self._active_runs = WeakKeyDictionary()
        self._lock = threading.Lock()
        self._temp_files = set()
        
        # Register cleanup on exit
        atexit.register(self._cleanup_temp_files)
    
    def _cleanup_temp_files(self):
        """Clean up temporary trace files on exit"""
        for file_path in self._temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")
    
    async def start_run(
        self,
        context,
        automation_name: str,
        success_criteria: Optional[str] = None,
        playwright_instructions: Optional[str] = None
    ):
        """Start monitoring a Playwright automation run"""
        try:
            # Create run via API
            async with httpx.AsyncClient(
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            ) as client:
                response = await client.post(
                    f"{self.config.base_url}/api/sdk/runs/create",
                    headers=self.config.headers,
                    json={
                        "automation_name": automation_name,
                        "success_criteria": success_criteria,
                        "playwright_instructions": playwright_instructions
                    }
                )
                
                if response.status_code == 429:
                    raise ClioRateLimitError("Monthly rate limit exceeded")
                elif response.status_code == 401:
                    raise ClioAuthError("Invalid API key")
                elif response.status_code != 200:
                    error_msg = mask_sensitive_data(response.text)
                    raise ClioError(f"Failed to create run: {error_msg}")
                
                run_data = response.json()
                run_id = run_data["id"]
            
            # Get upload URLs
            async with httpx.AsyncClient(
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            ) as client:
                response = await client.get(
                    f"{self.config.base_url}/api/sdk/runs/{run_id}/upload-urls",
                    headers=self.config.headers
                )
                
                if response.status_code != 200:
                    error_msg = mask_sensitive_data(response.text)
                    raise ClioError(f"Failed to get upload URLs: {error_msg}")
                
                upload_data = response.json()
            
            # Enable tracing if not already enabled
            logger.info(f"🔍 Enabling trace capture for run {run_id}")
            await context.tracing.start(screenshots=True, snapshots=True, sources=True)
            
            # Get video directory from context options
            video_dir = None
            logger.info(f"🔍 Checking context for video directory...")
            logger.info(f"🔍 Context has _impl_obj: {hasattr(context, '_impl_obj')}")
            if hasattr(context, '_impl_obj'):
                logger.info(f"🔍 _impl_obj has _options: {hasattr(context._impl_obj, '_options')}")
                if hasattr(context._impl_obj, '_options'):
                    options = context._impl_obj._options
                    logger.info(f"🔍 Context options: {options}")
                    # Extract video directory from recordVideo.dir
                    record_video = options.get('recordVideo', {})
                    if isinstance(record_video, dict) and 'dir' in record_video:
                        video_dir = str(record_video['dir'])
                        logger.info(f"🔍 Found video directory: {video_dir}")
                    else:
                        logger.info(f"🔍 No video directory found in recordVideo: {record_video}")
            
            # Store run info with thread safety
            with self._lock:
                # Check if context already has a monitor
                if hasattr(context, '_clio_monitor_patched'):
                    logger.warning("Context already has a Clio monitor attached, skipping")
                    return
                
                self._active_runs[context] = {
                    "run_id": run_id,
                    "video_upload_url": upload_data["video_upload_url"],
                    "trace_upload_url": upload_data["trace_upload_url"],
                    "video_s3_key": upload_data["video_s3_key"],
                    "trace_s3_key": upload_data["trace_s3_key"],
                    "video_dir": video_dir,  # Store the video directory path
                    "trace_enabled": True  # Track that we enabled tracing
                }
                
                # Mark context as patched
                context._clio_monitor_patched = True
            
            # Set up context close handler
            original_close = context.close
            
            async def close_with_upload():
                logger.info(f"🚀 close_with_upload called for context")
                upload_attempted = False
                trace_path = None
                try:
                    # Stop tracing and save trace file before closing context
                    with self._lock:
                        run_info = self._active_runs.get(context)
                    
                    if run_info and run_info.get("trace_enabled"):
                        try:
                            logger.info(f"📊 Stopping trace and saving trace file...")
                            # Use temp directory for trace files
                            trace_dir = tempfile.gettempdir()
                            trace_path = os.path.join(trace_dir, f"clio_trace_{run_info['run_id']}.zip")
                            await context.tracing.stop(path=trace_path)
                            logger.info(f"📊 Trace saved to {mask_sensitive_data(trace_path)}")
                            
                            # Store trace path for upload and cleanup
                            with self._lock:
                                if context in self._active_runs:
                                    self._active_runs[context]["trace_path"] = trace_path
                                self._temp_files.add(trace_path)
                        except Exception as trace_error:
                            logger.warning(f"⚠️ Failed to save trace: {mask_sensitive_data(str(trace_error))}")
                            
                    # Try to call original close first, but don't fail if it's already closed
                    logger.info(f"📝 Calling original context.close()")
                    try:
                        await original_close()
                        logger.info(f"✅ Original context.close() completed")
                    except Exception as close_error:
                        logger.warning(f"⚠️ Original context.close() failed (context may already be closed): {close_error}")
                    
                    # Always attempt upload regardless of close success
                    logger.info(f"📤 Starting upload handler...")
                    await self._handle_upload(context)
                    upload_attempted = True
                    logger.info(f"✅ Upload handler completed")
                    
                except Exception as e:
                    logger.error(f"❌ Error in close_with_upload: {mask_sensitive_data(str(e))}", exc_info=False)
                    # Always attempt upload even if there was an error
                    if not upload_attempted:
                        try:
                            logger.info(f"📤 Attempting upload despite error...")
                            await self._handle_upload(context)
                            logger.info(f"✅ Upload completed despite error")
                        except Exception as upload_error:
                            logger.error(f"❌ Upload also failed: {mask_sensitive_data(str(upload_error))}")
                    
                    if self.config.raise_on_error:
                        raise
                finally:
                    # Clean up resources
                    logger.info(f"🧹 Cleaning up context")
                    with self._lock:
                        if context in self._active_runs:
                            run_info = self._active_runs.get(context, {})
                            # Clean up trace file if upload succeeded
                            trace_path = run_info.get("trace_path")
                            if trace_path and os.path.exists(trace_path):
                                try:
                                    os.remove(trace_path)
                                    self._temp_files.discard(trace_path)
                                    logger.debug(f"Cleaned up trace file: {mask_sensitive_data(trace_path)}")
                                except Exception as e:
                                    logger.warning(f"Failed to cleanup trace: {e}")
                            
                            del self._active_runs[context]
            
            context.close = close_with_upload
            
            logger.info(f"Started monitoring run {mask_sensitive_data(run_id)} for {automation_name}")
            
        except Exception as e:
            logger.error(f"Failed to start run: {mask_sensitive_data(str(e))}")
            # Clean up on failure
            with self._lock:
                if context in self._active_runs:
                    del self._active_runs[context]
                if hasattr(context, '_clio_monitor_patched'):
                    delattr(context, '_clio_monitor_patched')
            if self.config.raise_on_error:
                raise
    
    async def _handle_upload(self, context):
        """Handle uploading video and trace files after context closes"""
        logger.info(f"🚀 _handle_upload called for context")
        
        with self._lock:
            run_info = self._active_runs.get(context)
        
        if not run_info:
            logger.warning(f"⚠️ Context not found in active runs")
            return
        
        try:
            # Find video file using stored video directory
            video_path = None
            video_dir = run_info.get("video_dir")
            logger.info(f"🎥 Video directory: {video_dir}")
            if video_dir:
                video_dir_path = Path(video_dir)
                if video_dir_path.exists():
                    # Find the most recent video file
                    video_files = list(video_dir_path.glob("*.webm")) + list(video_dir_path.glob("*.mp4"))
                    logger.info(f"🎥 Found video files: {video_files}")
                    if video_files:
                        video_path = max(video_files, key=lambda p: p.stat().st_mtime)
                        logger.info(f"🎥 Selected video: {video_path}")
            
            # Find trace file (use stored trace path if available)
            trace_path = None
            stored_trace_path = run_info.get("trace_path")
            if stored_trace_path:
                trace_path = Path(stored_trace_path)
                logger.info(f"📊 Using stored trace file: {trace_path}")
            elif hasattr(context, '_impl_obj') and hasattr(context._impl_obj, '_trace_path'):
                trace_path = Path(context._impl_obj._trace_path)
                logger.info(f"📊 Using context trace file: {trace_path}")
            
            # Upload files
            logger.info(f"📤 Video upload URL: {run_info['video_upload_url'][:50]}...")
            logger.info(f"📤 Trace upload URL: {run_info['trace_upload_url'][:50]}...")
            
            video_success, trace_success = await self.uploader.upload_files(
                video_path=video_path,
                trace_path=trace_path,
                video_url=run_info["video_upload_url"],
                trace_url=run_info["trace_upload_url"]
            )
            
            logger.info(f"📤 Upload results - Video: {video_success}, Trace: {trace_success}")
            
            # Mark upload as complete
            if video_success or trace_success:
                async with httpx.AsyncClient(
                    timeout=self.config.timeout,
                    verify=self.config.verify_ssl
                ) as client:
                    response = await client.post(
                        f"{self.config.base_url}/api/sdk/runs/{run_info['run_id']}/complete",
                        headers=self.config.headers,
                        json={
                            "video_s3_key": run_info["video_s3_key"] if video_success else None,
                            "trace_s3_key": run_info["trace_s3_key"] if trace_success else None
                        }
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"Successfully uploaded files for run {mask_sensitive_data(run_info['run_id'])}")
                    else:
                        error_msg = mask_sensitive_data(response.text)
                        logger.error(f"Failed to mark upload complete: {error_msg}")
            
        except Exception as e:
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"Failed to handle upload: {error_msg}")
            if self.config.raise_on_error:
                raise ClioUploadError(f"Upload failed: {error_msg}")
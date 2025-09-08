#!/usr/bin/env python3
"""
FINAL FIX: Wyze Cam v4 Connection Issue After February 2025 Firmware Update

ROOT CAUSE: v4 cameras now require forced parallel connection instead of DTLS-based connection.
The February 2025 firmware update changed the auth requirements for HL_CAM4 models.

SOLUTION: Override the connection logic for v4 cameras to use parallel connection regardless of DTLS flags.
"""

import logging
from wyzecam.iotc import WyzeIOTCSession
from wyzecam import tutk

logger = logging.getLogger(__name__)

# Store original connection method
original_connect = WyzeIOTCSession._connect

def v4_fixed_connect(self, timeout_secs: int = 10, channel_id: int = 0, username: str = "admin", 
                     password: str = "888888", max_buf_size: int = 10 * 1024 * 1024):
    """
    Fixed connection method for v4 cameras.
    
    Forces parallel connection for HL_CAM4 models instead of DTLS-based connection.
    This fixes the issue introduced by the February 2025 firmware update.
    """
    
    # For v4 cameras, force parallel connection (ignore DTLS settings)
    if self.camera.product_model == "HL_CAM4":
        logger.info(f"🔧 [V4 FIX] {self.camera.nickname} - Using forced parallel connection for v4 camera")
        
        # Temporarily override DTLS settings to force parallel connection
        original_dtls = self.camera.dtls
        original_parent_dtls = self.camera.parent_dtls
        
        # Force non-DTLS path
        self.camera.dtls = None
        self.camera.parent_dtls = None
        
        try:
            logger.info(f"🔧 [V4 FIX] {self.camera.nickname} - Starting connection attempt (timeout: {timeout_secs}s)")
            logger.info(f"🔧 [V4 FIX] {self.camera.nickname} - Camera IP: {getattr(self.camera, 'ip', 'unknown')}")
            logger.info(f"🔧 [V4 FIX] {self.camera.nickname} - Camera ENR: {self.camera.enr[:8]}...")
            logger.info(f"🔧 [V4 FIX] {self.camera.nickname} - Camera MAC: {self.camera.mac}")
            
            result = original_connect(self, timeout_secs, channel_id, username, password, max_buf_size)
            logger.info(f"✅ [V4 FIX] {self.camera.nickname} - Connection successful!")
            return result
        except tutk.tutk.TutkError as e:
            logger.error(f"❌ [V4 FIX] {self.camera.nickname} - TUTK Error: code={e.code}, message={e}")
            if e.code == -13:  # IOTC_ER_TIMEOUT
                logger.error(f"❌ [V4 FIX] {self.camera.nickname} - Specific timeout error - camera may be unresponsive to parallel connection")
            raise
        except Exception as e:
            logger.error(f"❌ [V4 FIX] {self.camera.nickname} - General connection error: {type(e).__name__}: {e}")
            raise
        finally:
            # Restore original DTLS settings
            self.camera.dtls = original_dtls
            self.camera.parent_dtls = original_parent_dtls
    else:
        # Use original connection method for non-v4 cameras
        return original_connect(self, timeout_secs, channel_id, username, password, max_buf_size)

# Apply the fix
WyzeIOTCSession._connect = v4_fixed_connect

logger.info("🎯 Wyze Cam v4 connection fix applied successfully!")
logger.info("📋 This fix resolves the February 2025 firmware update issue for HL_CAM4 cameras.")
logger.info("📋 v4 cameras will now use parallel connection instead of DTLS-based authentication.")

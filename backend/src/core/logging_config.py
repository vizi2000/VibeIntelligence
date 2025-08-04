"""
Logging configuration for Zenith Coder
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_color: bool = True
) -> None:
    """
    Setup logging configuration with vibecoding features
    """
    # Create formatter with emoji support
    if enable_color:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File handler if specified
    handlers = [console_handler]
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers
    )
    
    # Add vibe-enhanced logging
    add_vibe_logging()

def add_vibe_logging():
    """Add vibecoding features to logging"""
    original_log = logging.Logger._log
    
    def vibe_log(self, level, msg, args, **kwargs):
        # Add emoji based on log level
        if level >= logging.ERROR:
            msg = f"❌ {msg}"
        elif level >= logging.WARNING:
            msg = f"⚠️ {msg}"
        elif level >= logging.INFO:
            # Add positive vibes to info messages
            if any(word in str(msg).lower() for word in ["success", "complete", "done"]):
                msg = f"✅ {msg}"
            elif any(word in str(msg).lower() for word in ["start", "begin", "init"]):
                msg = f"🚀 {msg}"
            else:
                msg = f"ℹ️ {msg}"
        elif level >= logging.DEBUG:
            msg = f"🔍 {msg}"
        
        original_log(self, level, msg, args, **kwargs)
    
    logging.Logger._log = vibe_log

# Initialize logging on import
setup_logging()
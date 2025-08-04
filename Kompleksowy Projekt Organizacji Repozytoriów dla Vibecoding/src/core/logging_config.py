"""
Zenith Coder Logging Configuration
Following Directive 6: Documentation & Directive 19: Well-Being
Includes vibe-aware logging with sentiment tracking
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import json
from pythonjsonlogger import jsonlogger

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


class VibeAwareFormatter(jsonlogger.JsonFormatter):
    """
    Custom formatter that adds vibe metrics to logs (v4.0)
    Tracks developer mood and flow state through log patterns
    """
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add vibe analysis (Directive 19)
        log_record['vibe_score'] = self._analyze_vibe(record.getMessage())
        
        # Add eco impact (Directive 17)
        log_record['eco_impact'] = 'low'  # All logs are low impact
        
        # Track error patterns for well-being
        if record.levelname in ['ERROR', 'CRITICAL']:
            log_record['needs_break'] = self._check_burnout_pattern(record)
    
    def _analyze_vibe(self, message: str) -> int:
        """Analyze log message sentiment (1-10 scale)"""
        # Simple sentiment analysis - in production, use HuggingFace model
        positive_words = ['success', 'completed', 'ready', 'initialized', 'healthy']
        negative_words = ['error', 'failed', 'exception', 'timeout', 'crashed']
        
        message_lower = message.lower()
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        # Calculate vibe score (5 is neutral)
        vibe_score = 5 + positive_count - negative_count
        return max(1, min(10, vibe_score))
    
    def _check_burnout_pattern(self, record: logging.LogRecord) -> bool:
        """Check if error patterns indicate developer needs a break"""
        # In production, track error frequency over time
        # For now, suggest break after critical errors
        return record.levelname == 'CRITICAL'


def setup_logging(log_level: str = "INFO") -> None:
    """
    Setup comprehensive logging with vibe awareness
    Following Directive 11: Continuous monitoring
    """
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_formatter = VibeAwareFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    
    # Console handler with color support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    
    # File handler for structured logs
    file_handler = logging.FileHandler(
        LOGS_DIR / f"zenith_{datetime.now().strftime('%Y%m%d')}.json"
    )
    file_handler.setFormatter(file_formatter)
    
    # Vibe-specific handler for flow state tracking
    vibe_handler = logging.FileHandler(LOGS_DIR / "vibe_metrics.json")
    vibe_handler.setFormatter(file_formatter)
    vibe_handler.setLevel(logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Add vibe handler to specific loggers
    vibe_logger = logging.getLogger("zenith.vibe")
    vibe_logger.addHandler(vibe_handler)
    
    # Log startup with positive vibe
    logger = logging.getLogger(__name__)
    logger.info("🚀 Zenith Coder logging initialized - Let's create something amazing!")
    
    # Set third-party log levels to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_vibe_logger() -> logging.Logger:
    """Get logger specifically for vibe metrics"""
    return logging.getLogger("zenith.vibe")


def log_flow_state(user_id: str, flow_score: int, activity: str) -> None:
    """Log user flow state for well-being tracking (Directive 19)"""
    vibe_logger = get_vibe_logger()
    vibe_logger.info(
        "Flow state update",
        extra={
            "user_id": user_id,
            "flow_score": flow_score,
            "activity": activity,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    # Celebrate high flow states
    if flow_score >= 80:
        vibe_logger.info(f"🎯 {user_id} achieved flow state! Keep vibing!")


def log_eco_metric(component: str, energy_score: float, optimization: str = None) -> None:
    """Log eco-metrics for sustainability tracking (Directive 17)"""
    logger = logging.getLogger("zenith.eco")
    logger.info(
        "Eco metric recorded",
        extra={
            "component": component,
            "energy_score": energy_score,
            "optimization": optimization,
            "carbon_saved": energy_score * 0.001  # Simplified calculation
        }
    )
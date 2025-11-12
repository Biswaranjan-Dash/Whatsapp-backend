import logging
import json
from typing import Any, Dict
import sys


class PHIRedactor:
    """Helper to redact PHI fields from logs"""
    
    REDACTED_FIELDS = {"phone", "email", "first_name", "last_name"}
    
    @classmethod
    def redact(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive fields from dictionary"""
        if not isinstance(data, dict):
            return data
        
        redacted = data.copy()
        for key in cls.REDACTED_FIELDS:
            if key in redacted:
                redacted[key] = "***REDACTED***"
        
        return redacted


class StructuredLogger:
    """Structured JSON logger"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(handler)
    
    def _log(self, level: str, message: str, **kwargs):
        log_data = {
            "level": level,
            "message": message,
            **kwargs
        }
        self.logger.log(
            getattr(logging, level.upper()),
            json.dumps(log_data)
        )
    
    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log("ERROR", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log("DEBUG", message, **kwargs)


def get_logger(name: str) -> StructuredLogger:
    from app.core.config import get_settings
    settings = get_settings()
    return StructuredLogger(name, settings.LOG_LEVEL)

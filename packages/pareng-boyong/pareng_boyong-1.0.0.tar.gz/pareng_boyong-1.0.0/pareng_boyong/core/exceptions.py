"""
Exception classes for Pareng Boyong AI Agent.

This module defines custom exceptions used throughout the Pareng Boyong system
with Filipino cultural context where appropriate.
"""

from typing import Optional, Dict, Any, List


class ParengBoyongError(Exception):
    """
    Base exception class for all Pareng Boyong related errors.
    
    This is the parent class for all custom exceptions in the system.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class ConfigurationError(ParengBoyongError):
    """
    Raised when there are configuration-related issues.
    
    Examples:
    - Missing API keys
    - Invalid configuration values
    - File permission issues
    - Environment setup problems
    """
    
    def __init__(self, message: str, missing_keys: Optional[List[str]] = None, invalid_values: Optional[Dict[str, Any]] = None):
        details = {}
        if missing_keys:
            details["missing_keys"] = missing_keys
        if invalid_values:
            details["invalid_values"] = invalid_values
        
        super().__init__(message, details)
        self.missing_keys = missing_keys or []
        self.invalid_values = invalid_values or {}
    
    def get_filipino_message(self) -> str:
        """Get culturally appropriate Filipino error message."""
        if self.missing_keys:
            return f"Pasensya na po, kulang pa ang API keys: {', '.join(self.missing_keys)}. Kailangan po natin 'yan para sa mga serbisyo."
        if self.invalid_values:
            return "May mali po sa configuration. I-check po natin ang mga settings."
        return f"May problema po sa setup: {self.message}"


class ToolError(ParengBoyongError):
    """
    Raised when there are tool execution errors.
    
    Examples:
    - API failures
    - Tool not available
    - Resource limitations
    - Cost budget exceeded
    """
    
    def __init__(self, message: str, tool_name: Optional[str] = None, cost_exceeded: bool = False, service_unavailable: bool = False):
        details = {
            "tool_name": tool_name,
            "cost_exceeded": cost_exceeded,
            "service_unavailable": service_unavailable
        }
        
        super().__init__(message, details)
        self.tool_name = tool_name
        self.cost_exceeded = cost_exceeded
        self.service_unavailable = service_unavailable
    
    def get_filipino_message(self) -> str:
        """Get culturally appropriate Filipino error message."""
        if self.cost_exceeded:
            return f"Pasensya na po, naubos na ang budget para sa araw na ito. Subukan po natin bukas o gumamit ng FREE na serbisyo."
        if self.service_unavailable:
            return f"Hindi po available ang {self.tool_name} ngayon. Subukan po natin ang iba pang options."
        if self.tool_name:
            return f"May problema po sa {self.tool_name}: {self.message}"
        return f"Hindi po naging successful ang operation: {self.message}"


class APIError(ParengBoyongError):
    """
    Raised when external API calls fail.
    
    Examples:
    - Network timeouts
    - Authentication failures
    - Rate limiting
    - Service outages
    """
    
    def __init__(self, message: str, api_name: str, status_code: Optional[int] = None, rate_limited: bool = False):
        details = {
            "api_name": api_name,
            "status_code": status_code,
            "rate_limited": rate_limited
        }
        
        super().__init__(message, details)
        self.api_name = api_name
        self.status_code = status_code
        self.rate_limited = rate_limited
    
    def get_filipino_message(self) -> str:
        """Get culturally appropriate Filipino error message."""
        if self.rate_limited:
            return f"Sobrang dami po ng requests sa {self.api_name}. Maghintay po tayo ng konti bago subukan ulit."
        if self.status_code == 401:
            return f"Mali po ang API key para sa {self.api_name}. I-check po natin ang credentials."
        if self.status_code == 429:
            return f"Naubos na po ang quota sa {self.api_name} ngayong araw. Subukan po natin bukas."
        return f"May problema po sa connection sa {self.api_name}: {self.message}"


class CostLimitError(ParengBoyongError):
    """
    Raised when cost limits are exceeded.
    
    This exception is thrown when operations would exceed the daily or session
    cost budgets to protect users from unexpected charges.
    """
    
    def __init__(self, message: str, current_cost: float, limit: float, suggested_alternatives: Optional[List[str]] = None):
        details = {
            "current_cost": current_cost,
            "limit": limit,
            "suggested_alternatives": suggested_alternatives or []
        }
        
        super().__init__(message, details)
        self.current_cost = current_cost
        self.limit = limit
        self.suggested_alternatives = suggested_alternatives or []
    
    def get_filipino_message(self) -> str:
        """Get culturally appropriate Filipino error message."""
        message = f"Pasensya na po, naabot na natin ang cost limit (${self.current_cost:.3f} / ${self.limit:.3f})."
        
        if self.suggested_alternatives:
            message += f" Subukan po natin ang mga FREE na options: {', '.join(self.suggested_alternatives)}"
        else:
            message += " Gumamit po tayo ng mga FREE na serbisyo o i-increase ang budget."
        
        return message


class CulturalContextError(ParengBoyongError):
    """
    Raised when there are issues with Filipino cultural context processing.
    
    Examples:
    - Language processing failures
    - Cultural context mismatches
    - Localization issues
    """
    
    def __init__(self, message: str, context_type: Optional[str] = None, language_issue: bool = False):
        details = {
            "context_type": context_type,
            "language_issue": language_issue
        }
        
        super().__init__(message, details)
        self.context_type = context_type
        self.language_issue = language_issue
    
    def get_filipino_message(self) -> str:
        """Get culturally appropriate Filipino error message."""
        if self.language_issue:
            return "Pasensya na po, may problema sa pag-intindi ng wika. Subukan po ninyo sa English o mas simple na Filipino."
        return f"May problema po sa cultural context: {self.message}"


class SystemHealthError(ParengBoyongError):
    """
    Raised when system health checks fail.
    
    Examples:
    - High memory usage
    - CPU overload
    - Disk space issues
    - Service unavailability
    """
    
    def __init__(self, message: str, resource_type: Optional[str] = None, usage_percent: Optional[float] = None):
        details = {
            "resource_type": resource_type,
            "usage_percent": usage_percent
        }
        
        super().__init__(message, details)
        self.resource_type = resource_type
        self.usage_percent = usage_percent
    
    def get_filipino_message(self) -> str:
        """Get culturally appropriate Filipino error message."""
        if self.resource_type == "memory" and self.usage_percent:
            return f"Mataas po ang memory usage ({self.usage_percent:.1f}%). Maghintay po tayo o i-restart ang system."
        if self.resource_type == "cpu" and self.usage_percent:
            return f"Busy po ang CPU ({self.usage_percent:.1f}%). Mag-antay po tayo ng konti."
        return f"May problema po sa system health: {self.message}"


# Utility functions for exception handling

def handle_filipino_error(error: Exception, cultural_mode: bool = True) -> str:
    """
    Convert any exception to a Filipino-friendly error message.
    
    Args:
        error: The exception to handle
        cultural_mode: Whether to use Filipino cultural context
        
    Returns:
        Culturally appropriate error message
    """
    if isinstance(error, ParengBoyongError) and cultural_mode:
        if hasattr(error, 'get_filipino_message'):
            return error.get_filipino_message()
    
    # Generic Filipino error message
    if cultural_mode:
        return f"Pasensya na po, may nangyaring problema: {str(error)}"
    else:
        return str(error)


def create_error_response(error: Exception, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.
    
    Args:
        error: The exception that occurred
        session_id: Optional session identifier
        
    Returns:
        Standardized error response dictionary
    """
    response = {
        "success": False,
        "error": str(error),
        "error_type": error.__class__.__name__,
        "timestamp": str(ParengBoyongError)  # This should be datetime but keeping simple
    }
    
    if session_id:
        response["session_id"] = session_id
    
    if isinstance(error, ParengBoyongError):
        response.update(error.to_dict())
        response["filipino_message"] = error.get_filipino_message() if hasattr(error, 'get_filipino_message') else None
    
    return response
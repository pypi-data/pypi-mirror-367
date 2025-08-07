"""Custom exception classes for test automation."""
# Custom exception classes for test automation
from typing import Any

class E2eActionError(Exception):
    """Exception raised when a test action fails."""
    
    def __init__(self, message: str, action: str = None, selector: str = None):
        super().__init__(message)
        self.action = action
        self.selector = selector
        
    def __str__(self):
        """Return string representation with action and selector details."""
        base_msg = super().__str__()
        if self.action and self.selector:
            return f"{base_msg} (Action: {self.action}, Selector: {self.selector})"
        elif self.action:
            return f"{base_msg} (Action: {self.action})"
        elif self.selector:
            return f"{base_msg} (Selector: {self.selector})"
        return base_msg


class ElementNotFoundError(E2eActionError):
    """Exception raised when an element cannot be found."""
    
    def __init__(self, selector: str, timeout: int = None):
        message = f"Element not found: {selector}"
        if timeout:
            message += f" (timeout: {timeout}ms)"
        super().__init__(message, selector=selector)


class TimeoutError(E2eActionError):
    """Exception raised when an action times out."""
    
    def __init__(self, action: str, timeout: int):
        message = f"Action timed out after {timeout}ms: {action}"
        super().__init__(message, action=action)


class NavigationError(E2eActionError):
    """Exception raised when page navigation fails."""
    
    def __init__(self, url: str, reason: str = None):
        message = f"Navigation failed to: {url}"
        if reason:
            message += f" - {reason}"
        super().__init__(message)


class AssertionError(E2eActionError):
    """Exception raised when a test assertion fails."""
    
    def __init__(self, assertion: str, expected: Any, actual: Any):
        message = f"Assertion failed: {assertion} (expected: {expected}, actual: {actual})"
        super().__init__(message) 
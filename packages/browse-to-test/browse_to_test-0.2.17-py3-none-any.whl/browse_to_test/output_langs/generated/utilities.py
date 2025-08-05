"""Utility functions for test automation."""
# Utility functions for test automation
import sys
import asyncio
from typing import Any, Dict, List
from playwright.async_api import Page
from .exceptions import E2eActionError, ElementNotFoundError

def log_step(step: str, details: str = ""):
    """Log a test step with optional details."""
    print(f"🔸 {step}", file=sys.stderr)
    if details:
        print(f"   {details}", file=sys.stderr)


def log_error(error: str, details: str = ""):
    """Log an error with optional details.""" 
    print(f"❌ {error}", file=sys.stderr)
    if details:
        print(f"   {details}", file=sys.stderr)


def log_success(message: str):
    """Log a success message."""
    print(f"✅ {message}", file=sys.stderr)


def log_warning(message: str):
    """Log a warning message."""
    print(f"⚠️ {message}", file=sys.stderr)


def log_debug(message: str):
    """Log debug information."""
    print(f"🔧 {message}", file=sys.stderr)


def replace_sensitive_data(text: str, sensitive_map: Dict[str, Any]) -> str:
    """Replace sensitive data placeholders in text."""
    if not isinstance(text, str):
        return text
    for placeholder, value in sensitive_map.items():
        replacement_value = str(value) if value is not None else ''
        text = text.replace(f'<secret>{placeholder}</secret>', replacement_value)
    return text


def mask_sensitive_data(data: Any, sensitive_keys: List[str] = None) -> Any:
    """Mask sensitive data in test data."""
    if sensitive_keys is None:
        sensitive_keys = ['password', 'token', 'key', 'secret', 'credential']
    
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if any(sensitive_key.lower() in key.lower() for sensitive_key in sensitive_keys):
                masked[key] = '***MASKED***'
            else:
                masked[key] = mask_sensitive_data(value, sensitive_keys)
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item, sensitive_keys) for item in data]
    else:
        return data


def generate_test_data(template: Dict[str, Any], **overrides) -> Dict[str, Any]:
    """Generate test data from template with overrides."""
    test_data = template.copy()
    test_data.update(overrides)
    return test_data


def wait_with_retry(action_func, max_retries: int = 3, delay_ms: int = 1000, *args, **kwargs):
    """Execute an action with retry logic."""
    for attempt in range(max_retries):
        try:
            return action_func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            log_warning(f"Attempt {attempt + 1} failed, retrying in {delay_ms}ms: {e}")
            if asyncio.iscoroutinefunction(action_func):
                import asyncio
                asyncio.sleep(delay_ms / 1000)
            else:
                import time
                time.sleep(delay_ms / 1000)


def format_selector(selector: str) -> str:
    """Format selector for logging and error messages."""
    if len(selector) > 50:
        return f"{selector[:47]}..."
    return selector


def get_element_description(tag: str = None, text: str = None, attributes: Dict[str, str] = None) -> str:
    """Generate a human-readable element description."""
    parts = []
    if tag:
        parts.append(f"<{tag}>")
    if text:
        short_text = text[:30] + "..." if len(text) > 30 else text
        parts.append(f'text="{short_text}"')
    if attributes:
        for key, value in list(attributes.items())[:2]:  # Limit to first 2 attributes
            parts.append(f'{key}="{value}"')
    return " ".join(parts) if parts else "unknown element" 

# Playwright-specific utilities

async def safe_playwright_action(page: Page, action_func, *args, step_info: str = '', **kwargs):
    """Execute a Playwright action with error handling."""
    try:
        log_step(f"Executing action: {action_func.__name__}", step_info)
        return await action_func(*args, **kwargs)
    except Exception as e:
        error_msg = f"Playwright action failed ({action_func.__name__}): {e}"
        log_error(error_msg, step_info)
        raise E2eActionError(error_msg) from e

async def try_locate_and_act_playwright(page: Page, selector: str, action_type: str, 
                                      text: str = None, step_info: str = '', timeout: int = 10000):
    """Locate element and perform action with fallback selectors."""
    log_step(f"Attempting {action_type} using selector: {format_selector(selector)}", step_info)
    
    try:
        locator = page.locator(selector).first
        
        if action_type == 'click':
            await locator.click(timeout=timeout)
            log_success(f"Successfully clicked element: {format_selector(selector)}")
        elif action_type == 'fill' and text is not None:
            await locator.fill(text, timeout=timeout)
            log_success(f"Successfully filled element: {format_selector(selector)}")
        elif action_type == 'select' and text is not None:
            await locator.select_option(value=text, timeout=timeout)
            log_success(f"Successfully selected option: {text}")
        else:
            raise ValueError(f'Unknown action type: {action_type}')
            
    except Exception as e:
        error_msg = f"Failed to {action_type} element {format_selector(selector)}: {e}"
        log_error(error_msg, step_info)
        raise ElementNotFoundError(selector) from e

async def assert_element_visible_playwright(page: Page, selector: str, timeout: int = 10000):
    """Assert that an element is visible on the page."""
    try:
        log_step(f"Asserting element is visible: {format_selector(selector)}")
        element = page.locator(selector).first
        await element.wait_for(state="visible", timeout=timeout)
        log_success(f"Element is visible: {format_selector(selector)}")
    except Exception as e:
        error_msg = f"Element not visible: {format_selector(selector)} - {e}"
        log_error(error_msg)
        raise ElementNotFoundError(selector, timeout) from e

async def wait_for_page_load_playwright(page: Page, timeout: int = 30000):
    """Wait for page to fully load."""
    try:
        log_step("Waiting for page load")
        await page.wait_for_load_state("networkidle", timeout=timeout)
        log_success("Page loaded successfully")
    except Exception as e:
        error_msg = f"Page load timeout: {e}"
        log_error(error_msg)
        raise TimeoutError("page_load", timeout) from e

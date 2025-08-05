"""
Utility functions for GwaniCLI including logging setup and error handling.
"""

import logging
import sys
import traceback
from pathlib import Path
from typing import Optional


def setup_logging(verbose: bool = False, log_file: Optional[str] = None):
    """
    Set up logging configuration for the application.

    Args:
        verbose: Enable verbose (DEBUG) logging
        log_file: Optional log file path
    """
    # Determine log level
    log_level = logging.DEBUG if verbose else logging.INFO

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(logging.DEBUG)  # Always DEBUG for file
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        except Exception as e:
            logging.warning(f"Failed to set up file logging: {e}")

    # Set specific logger levels to reduce noise
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

    if verbose:
        logging.info("Verbose logging enabled")


def handle_error(message: str, exit_code: int = 1, show_traceback: bool = False):
    """
    Handle and display error messages consistently with user-friendly formatting.

    Args:
        message: Error message to display
        exit_code: Exit code for the application (0 means don't exit)
        show_traceback: Whether to show the full traceback
    """
    logger = logging.getLogger(__name__)

    # Convert technical error to user-friendly message
    friendly_message = make_error_user_friendly(message)

    # Log the original technical error
    logger.error(message)

    # Show traceback if requested (only in debug/verbose mode)
    if show_traceback:
        logger.debug("Traceback:", exc_info=True)

    # Print user-friendly message to stderr
    print(f"❌ {friendly_message}", file=sys.stderr)

    # Provide helpful suggestions if applicable
    suggestion = get_error_suggestion(message)
    if suggestion:
        print(f"💡 {suggestion}", file=sys.stderr)

    # Exit if requested
    if exit_code != 0:
        sys.exit(exit_code)


def make_error_user_friendly(error_message: str) -> str:
    """
    Convert technical error messages to user-friendly ones.

    Args:
        error_message: Original technical error message

    Returns:
        User-friendly error message
    """
    error_lower = error_message.lower()

    # Network/connection errors
    if 'connection error' in error_lower or 'connectionerror' in error_lower:
        return "Unable to connect to the internet. Please check your network connection."

    if 'timeout' in error_lower or 'timed out' in error_lower:
        return "The request took too long to complete. Please try again."

    if 'dns' in error_lower or 'name resolution' in error_lower:
        return "Cannot reach the Quran API server. Please check your internet connection."

    # API errors
    if 'api error' in error_lower:
        if 'not found' in error_lower or '404' in error_message:
            return "The requested verse or surah was not found. Please check your input."
        elif 'forbidden' in error_lower or '403' in error_message:
            return "Access to the Quran API was denied. Please try again later."
        elif 'rate limit' in error_lower or '429' in error_message:
            return "Too many requests to the API. Please wait a moment and try again."
        elif '500' in error_message or 'internal server' in error_lower:
            return "The Quran API is temporarily unavailable. Please try again later."
        else:
            return "Unable to fetch verse data from the Quran API. Please try again."

    # Configuration errors
    if 'config' in error_lower:
        return "There was a problem with your configuration. Please check your settings."

    # Cache errors
    if 'cache' in error_lower:
        return "There was a problem with the local cache. It will be recreated automatically."

    # Translation errors
    if 'translation' in error_lower and ('not found' in error_lower or 'unknown' in error_lower):
        return "The requested translation is not available. Try using 'en.sahih' or 'en.pickthall'."

    # Surah/Ayah validation errors
    if 'surah' in error_lower and ('invalid' in error_lower or 'must be between' in error_lower):
        return "Invalid surah number. Please use a number between 1 and 114."

    if 'ayah' in error_lower and ('invalid' in error_lower or 'must be between' in error_lower):
        return "Invalid ayah number for this surah. Please check the surah's ayah count."

    # Permission errors
    if 'permission denied' in error_lower or 'access denied' in error_lower:
        return "Permission denied. Please check file permissions or run with appropriate privileges."

    # File system errors
    if 'no such file' in error_lower or 'file not found' in error_lower:
        return "Required file not found. The application may need to be reinstalled."

    # Import/dependency errors
    if 'no module named' in error_lower or 'import' in error_lower:
        return "Missing required dependencies. Please run 'pip install -r requirements.txt'."

    # JSON/parsing errors
    if 'json' in error_lower and ('decode' in error_lower or 'parse' in error_lower):
        return "Received invalid data from the API. Please try again."

    # Generic fallback - clean up the message
    # Remove common technical prefixes
    clean_message = error_message
    prefixes_to_remove = [
        'ApiError: ',
        'Exception: ',
        'Error: ',
        'RuntimeError: ',
        'ValueError: ',
        'TypeError: ',
    ]

    for prefix in prefixes_to_remove:
        if clean_message.startswith(prefix):
            clean_message = clean_message[len(prefix):]
            break

    # Capitalize first letter and ensure proper punctuation
    if clean_message:
        clean_message = clean_message[0].upper() + clean_message[1:]
        if not clean_message.endswith('.'):
            clean_message += '.'

    return clean_message or "An unexpected error occurred. Please try again."


def get_error_suggestion(error_message: str) -> str:
    """
    Get helpful suggestions based on the error type.

    Args:
        error_message: Original error message

    Returns:
        Helpful suggestion or empty string
    """
    error_lower = error_message.lower()

    if 'connection' in error_lower or 'network' in error_lower:
        return "Try checking your internet connection or using a different network."

    if 'not found' in error_lower and 'surah' in error_lower:
        return "Use 'gwani surah --help' to see valid surah formats."

    if 'translation' in error_lower:
        return "Use 'gwani config get translation' to see your current translation setting."

    if 'api' in error_lower and ('error' in error_lower or 'timeout' in error_lower):
        return "The issue might be temporary. Try again in a few moments."

    if 'cache' in error_lower:
        return "You can try clearing the cache with 'rm -rf ~/.config/gwanicli/cache.db'."

    if 'permission' in error_lower:
        return "Make sure you have write permissions to the configuration directory."

    return ""


def format_exception(exc: Exception, include_traceback: bool = False) -> str:
    """
    Format an exception for display.

    Args:
        exc: Exception instance
        include_traceback: Whether to include full traceback

    Returns:
        Formatted exception string
    """
    if include_traceback:
        return ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    else:
        return f"{type(exc).__name__}: {str(exc)}"


def validate_surah_number(surah: str) -> bool:
    """
    Validate that a surah identifier is valid.

    Args:
        surah: Surah number or name

    Returns:
        True if valid, False otherwise
    """
    try:
        surah_num = int(surah)
        return 1 <= surah_num <= 114
    except ValueError:
        # TODO: Add surah name validation
        return len(surah.strip()) > 0


def validate_ayah_number(ayah: int, surah: Optional[int] = None) -> bool:
    """
    Validate that an ayah number is valid.

    Args:
        ayah: Ayah number
        surah: Surah number (for more specific validation)

    Returns:
        True if valid, False otherwise
    """
    if ayah < 1:
        return False

    # TODO: Add specific validation based on surah length
    # For now, just check reasonable upper bound
    return ayah <= 286  # Longest surah is Al-Baqarah with 286 ayahs


def create_user_dirs():
    """Create necessary user directories if they don't exist."""
    try:
        # Config directory
        config_dir = Path.home() / '.config' / 'gwanicli'
        config_dir.mkdir(parents=True, exist_ok=True)

        # Cache directory
        cache_dir = Path.home() / '.cache' / 'gwanicli'
        cache_dir.mkdir(parents=True, exist_ok=True)

        logging.debug("Created user directories")

    except OSError as e:
        logging.warning(f"Failed to create user directories: {e}")


def get_user_config_dir() -> Path:
    """Get the user configuration directory path."""
    return Path.home() / '.config' / 'gwanicli'


def get_user_cache_dir() -> Path:
    """Get the user cache directory path."""
    return Path.home() / '.cache' / 'gwanicli'


def is_valid_translation_format(translation: str) -> bool:
    """
    Validate translation format string.

    Args:
        translation: Translation identifier (e.g., 'en.pickthall')

    Returns:
        True if format appears valid, False otherwise
    """
    if not translation or not isinstance(translation, str):
        return False

    # Basic format validation (language.translator)
    parts = translation.split('.')
    return len(parts) >= 2 and all(part.strip() for part in parts)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string for safe use as a filename.

    Args:
        filename: Raw filename string

    Returns:
        Sanitized filename string
    """
    import re

    # Replace invalid characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(' .')

    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]

    return sanitized or 'unnamed'


class GwaniError(Exception):
    """Base exception class for GwaniCLI-specific errors."""
    pass


class ConfigError(GwaniError):
    """Exception raised for configuration-related errors."""
    pass


class CacheError(GwaniError):
    """Exception raised for cache-related errors."""
    pass


class ValidationError(GwaniError):
    """Exception raised for validation errors."""
    pass


def retry_operation(func, max_retries: int = 3, delay: float = 1.0):
    """
    Retry an operation with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds

    Returns:
        Result of the function call

    Raises:
        The last exception if all retries fail
    """
    import time

    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e

            if attempt < max_retries:
                wait_time = delay * (2 ** attempt)  # Exponential backoff
                logging.debug(
                    f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                logging.error(f"All {max_retries + 1} attempts failed")

    # If we get here, all retries failed
    raise last_exception


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum allowed length
        suffix: Suffix to add when truncating

    Returns:
        Truncated text string
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix

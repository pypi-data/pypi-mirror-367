# agentik/utils.py

"""
Utility functions for logging, retries, performance tracking, and optional token counting.
"""

import time
import functools
import logging
from typing import Callable, Any, Optional

from colorama import init, Fore, Style

# Initialize colorama to support colored logging in terminal
init(autoreset=True)


# ---------------------- Logger ----------------------

def get_logger(name: str = "agentik") -> logging.Logger:
    """
    Create and return a formatted logger with color-coded output.

    Args:
        name (str): Logger name (default is "agentik").

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f"{Fore.CYAN}[%(asctime)s]{Style.RESET_ALL} %(levelname)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


# ---------------------- Retry Decorator ----------------------

def retry(
    retries: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator that retries a function on failure.

    Args:
        retries (int): Number of attempts before raising the exception.
        delay (float): Delay in seconds between retries.
        exceptions (tuple): Exception types to catch.

    Returns:
        Callable: Wrapped function with retry logic.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts == retries:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator


# ---------------------- Time Tracker ----------------------

def track_time(func: Callable) -> Callable:
    """
    Decorator to measure and log the execution time of a function.

    Args:
        func (Callable): Function to wrap.

    Returns:
        Callable: Wrapped function with timing output.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{Fore.GREEN}[Time]{Style.RESET_ALL} {func.__name__} took {duration:.2f}s")
        return result
    return wrapper


# ---------------------- Token Counter ----------------------

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> Optional[int]:
    """
    Count the number of tokens in a given text using the tiktoken library.

    Args:
        text (str): Input string to tokenize.
        model (str): LLM model to determine encoding scheme.

    Returns:
        Optional[int]: Token count or None if tiktoken is not installed.
    """
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except ImportError:
        return None

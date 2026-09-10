"""Resilient Rate Limit and Retry Handler with Exponential Backoff and Full Jitter."""

import asyncio
import logging
import random
import time
from functools import wraps
from typing import Callable, TypeVar, Any, Optional

logger = logging.getLogger("RetryHandler")

T = TypeVar("T")


class RetryConfig:
    def __init__(
        self,
        max_retries: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 32.0,
        exponential_factor: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_factor = exponential_factor
        self.jitter = jitter

    def compute_delay(self, attempt: int, retry_after: Optional[float] = None) -> float:
        """Compute backoff with optional decorrelated/full jitter or Retry-After header."""
        if retry_after is not None and retry_after > 0:
            return retry_after

        # Exponential backoff: base * factor^(attempt)
        calculated = self.base_delay * (self.exponential_factor ** attempt)
        capped = min(self.max_delay, calculated)

        if self.jitter:
            # Full jitter: random between 0 and capped
            return random.uniform(self.base_delay, capped)
        return capped


def async_retry_with_backoff(config: Optional[RetryConfig] = None):
    """Decorator for asynchronous functions handling 429 and transient errors."""
    cfg = config or RetryConfig()

    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(cfg.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc
                    err_msg = str(exc).lower()

                    is_rate_limit = "429" in err_msg or "too many requests" in err_msg or "resource_exhausted" in err_msg
                    is_transient = "503" in err_msg or "502" in err_msg or "timeout" in err_msg or "connection" in err_msg

                    if attempt == cfg.max_retries or (not is_rate_limit and not is_transient):
                        logger.error(f"Execution failed on attempt {attempt+1}/{cfg.max_retries}: {exc}")
                        raise exc

                    # Parse retry-after if available in exception
                    retry_after = getattr(exc, "retry_after", None)
                    sleep_time = cfg.compute_delay(attempt, retry_after)
                    logger.warning(
                        f"Rate limit / transient error encountered: {exc}. "
                        f"Retrying in {sleep_time:.2f}s (Attempt {attempt+1}/{cfg.max_retries})..."
                    )
                    await asyncio.sleep(sleep_time)

            raise last_exception
        return wrapper
    return decorator


def sync_retry_with_backoff(config: Optional[RetryConfig] = None):
    """Decorator for synchronous functions handling 429 and transient errors."""
    cfg = config or RetryConfig()

    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(cfg.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc
                    err_msg = str(exc).lower()

                    is_rate_limit = "429" in err_msg or "too many requests" in err_msg or "resource_exhausted" in err_msg
                    is_transient = "503" in err_msg or "502" in err_msg or "timeout" in err_msg or "connection" in err_msg

                    if attempt == cfg.max_retries or (not is_rate_limit and not is_transient):
                        logger.error(f"Execution failed on attempt {attempt+1}/{cfg.max_retries}: {exc}")
                        raise exc

                    retry_after = getattr(exc, "retry_after", None)
                    sleep_time = cfg.compute_delay(attempt, retry_after)
                    logger.warning(
                        f"Rate limit / transient error encountered: {exc}. "
                        f"Retrying in {sleep_time:.2f}s (Attempt {attempt+1}/{cfg.max_retries})..."
                    )
                    time.sleep(sleep_time)

            raise last_exception
        return wrapper
    return decorator

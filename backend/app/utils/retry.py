import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar


T = TypeVar("T")


class RetryableError(Exception):
    """Raised when a service failure should be retried."""


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    *,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_multiplier: float = 2.0,
    retry_exceptions: tuple[type[BaseException], ...] = (RetryableError,),
) -> T:
    """Run an async operation with exponential backoff.

    max_retries=3 means up to 4 total attempts: 1 initial attempt and 3 retries.
    """

    delay = initial_delay
    last_error: BaseException | None = None

    for attempt in range(max_retries + 1):
        try:
            return await operation()
        except retry_exceptions as error:
            last_error = error
            if attempt == max_retries:
                break
            await asyncio.sleep(delay)
            delay *= backoff_multiplier

    raise last_error or RetryableError("Operation failed after retries")

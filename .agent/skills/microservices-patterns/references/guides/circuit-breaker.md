# Circuit Breaker Pattern

Extracted from [SKILL.md](../SKILL.md)

## Overview

The Circuit Breaker pattern prevents cascade failures in distributed systems by detecting failures and encapsulating logic for preventing a failure from constantly recurring during maintenance, temporary external system failure, or unexpected system difficulties.

## States

- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Failing fast, requests are rejected
- **HALF_OPEN**: Testing if the service has recovered

## Implementation

```python
from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker for service calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        self.opened_at = None

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker."""

        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.opened_at = datetime.now()

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.opened_at = datetime.now()

    def _should_attempt_reset(self) -> bool:
        """Check if enough time passed to try again."""
        return (
            datetime.now() - self.opened_at
            > timedelta(seconds=self.recovery_timeout)
        )

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass
```

## Usage

```python
# Create circuit breaker with custom settings
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

async def call_payment_service(payment_data: dict):
    return await breaker.call(
        payment_client.process_payment,
        payment_data
    )
```

## Configuration Guidelines

| Parameter | Default | Description |
|-----------|---------|-------------|
| `failure_threshold` | 5 | Number of failures before opening circuit |
| `recovery_timeout` | 30 | Seconds to wait before trying again |
| `success_threshold` | 2 | Successful calls in HALF_OPEN to close circuit |

## Best Practices

1. **Tune thresholds based on service SLAs** - Critical services may need lower thresholds
2. **Use different breakers for different services** - Don't share state across unrelated services
3. **Monitor circuit state** - Alert when circuits open frequently
4. **Implement fallbacks** - Return cached data or default values when circuit is open
5. **Log state transitions** - Track when circuits open/close for debugging

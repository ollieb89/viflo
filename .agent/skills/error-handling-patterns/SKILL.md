---
name: error-handling-patterns
description: Master error handling patterns across languages including exceptions, Result types, error propagation, and graceful degradation to build resilient applications. Use when implementing error handling, designing APIs, or improving application reliability.
triggers:
  - Implementing error handling
  - Designing error-resilient APIs
  - Improving application reliability
  - Implementing retry and circuit breaker patterns
  - Handling async or concurrent errors
  - Building fault-tolerant distributed systems
---

# Error Handling Patterns

Build resilient applications with robust error handling strategies that gracefully handle failures and provide excellent debugging experiences.

## When to Use This Skill

- Implementing error handling in new features
- Designing error-resilient APIs
- Debugging production issues
- Improving application reliability
- Creating better error messages for users and developers
- Implementing retry and circuit breaker patterns
- Handling async/concurrent errors
- Building fault-tolerant distributed systems

## Core Concepts

### 1. Error Handling Philosophies

**Exceptions vs Result Types:**

| Approach         | Description                                   | Best For                                     |
| ---------------- | --------------------------------------------- | -------------------------------------------- |
| **Exceptions**   | Traditional try-catch, disrupts control flow  | Unexpected errors, exceptional conditions    |
| **Result Types** | Explicit success/failure, functional approach | Expected errors, validation failures         |
| **Error Codes**  | C-style, requires discipline                  | Low-level systems, performance-critical code |
| **Option/Maybe** | For nullable values                           | Handling missing values without exceptions   |

**When to Use Each:**

- **Exceptions**: Unexpected errors, exceptional conditions
- **Result Types**: Expected errors, validation failures
- **Panics/Crashes**: Unrecoverable errors, programming bugs

### 2. Error Categories

**Recoverable Errors:**

- Network timeouts
- Missing files
- Invalid user input
- API rate limits

**Unrecoverable Errors:**

- Out of memory
- Stack overflow
- Programming bugs (null pointer, etc.)

## Language Comparison

| Language       | Primary Pattern           | Key Features                                     |
| -------------- | ------------------------- | ------------------------------------------------ |
| **Python**     | Exceptions                | Custom hierarchies, context managers, decorators |
| **TypeScript** | Exceptions + Result types | Custom error classes, discriminated unions       |
| **Rust**       | Result + Option types     | `?` operator, explicit error handling            |
| **Go**         | Explicit error returns    | Sentinel errors, error wrapping/unwrapping       |

📚 **Detailed implementations**: See [references/guides/language-specific.md](references/guides/language-specific.md)

## Universal Patterns

### Key Patterns Overview

| Pattern                  | Purpose                            | Use Case                                |
| ------------------------ | ---------------------------------- | --------------------------------------- |
| **Circuit Breaker**      | Prevent cascading failures         | External API calls, distributed systems |
| **Error Aggregation**    | Collect multiple validation errors | Form validation, batch processing       |
| **Graceful Degradation** | Provide fallback functionality     | Cache failures, optional features       |
| **Retry with Backoff**   | Handle transient failures          | Network requests, rate-limited APIs     |

📚 **Full examples**: See [references/examples/retry-logic.md](references/examples/retry-logic.md)

## Best Practices

1. **Fail Fast**: Validate input early, fail quickly
2. **Preserve Context**: Include stack traces, metadata, timestamps
3. **Meaningful Messages**: Explain what happened and how to fix it
4. **Log Appropriately**: Error = log, expected failure = don't spam logs
5. **Handle at Right Level**: Catch where you can meaningfully handle
6. **Clean Up Resources**: Use try-finally, context managers, defer
7. **Don't Swallow Errors**: Log or re-throw, don't silently ignore
8. **Type-Safe Errors**: Use typed errors when possible

### Example: Good Error Handling

```python
def process_order(order_id: str) -> Order:
    """Process order with comprehensive error handling."""
    try:
        # Validate input
        if not order_id:
            raise ValidationError("Order ID is required")

        # Fetch order
        order = db.get_order(order_id)
        if not order:
            raise NotFoundError("Order", order_id)

        # Process payment
        try:
            payment_result = payment_service.charge(order.total)
        except PaymentServiceError as e:
            # Log and wrap external service error
            logger.error(f"Payment failed for order {order_id}: {e}")
            raise ExternalServiceError(
                f"Payment processing failed",
                service="payment_service",
                details={"order_id": order_id, "amount": order.total}
            ) from e

        # Update order
        order.status = "completed"
        order.payment_id = payment_result.id
        db.save(order)

        return order

    except ApplicationError:
        # Re-raise known application errors
        raise
    except Exception as e:
        # Log unexpected errors
        logger.exception(f"Unexpected error processing order {order_id}")
        raise ApplicationError(
            "Order processing failed",
            code="INTERNAL_ERROR"
        ) from e
```

## Common Pitfalls

| Pitfall                     | Why It's Bad                           | Solution                       |
| --------------------------- | -------------------------------------- | ------------------------------ |
| **Catching Too Broadly**    | `except Exception` hides bugs          | Catch specific exceptions      |
| **Empty Catch Blocks**      | Silently swallowing errors             | Always log or re-throw         |
| **Logging and Re-throwing** | Creates duplicate log entries          | Do one or the other            |
| **Not Cleaning Up**         | Forgetting to close files, connections | Use context managers           |
| **Poor Error Messages**     | "Error occurred" is not helpful        | Explain what and how to fix    |
| **Returning Error Codes**   | Easy to ignore, no stack trace         | Use exceptions or Result types |
| **Ignoring Async Errors**   | Unhandled promise rejections           | Always attach catch handlers   |

## Resources

### Guides

- [references/guides/language-specific.md](references/guides/language-specific.md) - Detailed Python, TypeScript, Rust, Go implementations

### Examples

- [references/examples/retry-logic.md](references/examples/retry-logic.md) - Circuit breaker, retry logic, graceful degradation patterns

### Additional References

- **references/exception-hierarchy-design.md**: Designing error class hierarchies
- **references/error-recovery-strategies.md**: Recovery patterns for different scenarios
- **references/async-error-handling.md**: Handling errors in concurrent code

### Assets

- **assets/error-handling-checklist.md**: Review checklist for error handling
- **assets/error-message-guide.md**: Writing helpful error messages

### Scripts

- **scripts/error-analyzer.py**: Analyze error patterns in logs

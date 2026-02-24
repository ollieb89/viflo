# Microservices Patterns — Best Practices & Common Pitfalls

> Part of [microservices-patterns](../SKILL.md) skill.

## Best Practices

1. **Service Boundaries**: Align with business capabilities
2. **Database Per Service**: No shared databases
3. **API Contracts**: Versioned, backward compatible
4. **Async When Possible**: Events over direct calls
5. **Circuit Breakers**: Fail fast on service failures
6. **Distributed Tracing**: Track requests across services
7. **Service Registry**: Dynamic service discovery
8. **Health Checks**: Liveness and readiness probes

## Common Pitfalls

- **Distributed Monolith**: Tightly coupled services
- **Chatty Services**: Too many inter-service calls
- **Shared Databases**: Tight coupling through data
- **No Circuit Breakers**: Cascade failures
- **Synchronous Everything**: Tight coupling, poor resilience
- **Premature Microservices**: Starting with microservices
- **Ignoring Network Failures**: Assuming reliable network
- **No Compensation Logic**: Can't undo failed transactions

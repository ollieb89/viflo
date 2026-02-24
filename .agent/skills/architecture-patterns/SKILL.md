---
name: architecture-patterns
description: Implement proven backend architecture patterns including Clean Architecture, Hexagonal Architecture, and Domain-Driven Design. Use when architecting complex backend systems or refactoring existing applications for better maintainability.
triggers:
  - Designing new backend systems
  - Refactoring monolithic applications
  - Implementing Clean Architecture
  - Applying Domain-Driven Design
  - Creating testable codebases
  - Planning microservices decomposition
---

# Architecture Patterns

Master proven backend architecture patterns including Clean Architecture, Hexagonal Architecture, and Domain-Driven Design to build maintainable, testable, and scalable systems.

## When to Use This Skill

- Designing new backend systems from scratch
- Refactoring monolithic applications for better maintainability
- Establishing architecture standards for your team
- Migrating from tightly coupled to loosely coupled architectures
- Implementing domain-driven design principles
- Creating testable and mockable codebases
- Planning microservices decomposition

## Core Concepts

### 1. Clean Architecture (Uncle Bob)

**Layers (dependency flows inward):**

- **Entities**: Core business models
- **Use Cases**: Application business rules
- **Interface Adapters**: Controllers, presenters, gateways
- **Frameworks & Drivers**: UI, database, external services

**Key Principles:**

- Dependencies point inward
- Inner layers know nothing about outer layers
- Business logic independent of frameworks
- Testable without UI, database, or external services

### 2. Hexagonal Architecture (Ports and Adapters)

**Components:**

- **Domain Core**: Business logic
- **Ports**: Interfaces defining interactions
- **Adapters**: Implementations of ports (database, REST, message queue)

**Benefits:**

- Swap implementations easily (mock for testing)
- Technology-agnostic core
- Clear separation of concerns

### 3. Domain-Driven Design (DDD)

**Strategic Patterns:**

- **Bounded Contexts**: Separate models for different domains
- **Context Mapping**: How contexts relate
- **Ubiquitous Language**: Shared terminology

**Tactical Patterns:**

- **Entities**: Objects with identity
- **Value Objects**: Immutable objects defined by attributes
- **Aggregates**: Consistency boundaries
- **Repositories**: Data access abstraction
- **Domain Events**: Things that happened

## Pattern Comparison

| Pattern                | Focus              | Best For                                   | Complexity |
| ---------------------- | ------------------ | ------------------------------------------ | ---------- |
| Clean Architecture     | Layer dependencies | Enterprise apps, long-term maintainability | Medium     |
| Hexagonal Architecture | Ports & adapters   | Testing, swapping implementations          | Medium     |
| DDD                    | Domain modeling    | Complex business logic                     | High       |

## When to Use Which Pattern

### Use Clean Architecture when:

- Building enterprise applications with long lifecycles
- Multiple UI interfaces (web, mobile, CLI) share the same backend
- Framework independence is critical

### Use Hexagonal Architecture when:

- Frequent swapping of external services (payment gateways, email providers)
- Heavy emphasis on testing with mocks
- Microservices with clear external boundaries

### Use DDD when:

- Domain complexity is high
- Business rules are central to the application
- Domain experts collaborate closely with developers

## Implementation Guides

Detailed implementation examples are available in:

- **[references/guides/pattern-deep-dives.md](references/guides/pattern-deep-dives.md)** - Complete code examples for Clean, Hexagonal, and DDD patterns

Quick directory structure overview for Clean Architecture:

```
app/
├── domain/           # Entities & business rules
│   ├── entities/
│   ├── value_objects/
│   └── interfaces/
├── use_cases/        # Application business rules
├── adapters/         # Interface implementations
└── infrastructure/   # Framework & external concerns
```

## Resources

- **references/clean-architecture-guide.md**: Detailed layer breakdown
- **references/hexagonal-architecture-guide.md**: Ports and adapters patterns
- **references/ddd-tactical-patterns.md**: Entities, value objects, aggregates
- **references/guides/pattern-deep-dives.md**: Complete implementation examples
- **assets/clean-architecture-template/**: Complete project structure
- **assets/ddd-examples/**: Domain modeling examples

## Best Practices

1. **Dependency Rule**: Dependencies always point inward
2. **Interface Segregation**: Small, focused interfaces
3. **Business Logic in Domain**: Keep frameworks out of core
4. **Test Independence**: Core testable without infrastructure
5. **Bounded Contexts**: Clear domain boundaries
6. **Ubiquitous Language**: Consistent terminology
7. **Thin Controllers**: Delegate to use cases
8. **Rich Domain Models**: Behavior with data

## Common Pitfalls

- **Anemic Domain**: Entities with only data, no behavior
- **Framework Coupling**: Business logic depends on frameworks
- **Fat Controllers**: Business logic in controllers
- **Repository Leakage**: Exposing ORM objects
- **Missing Abstractions**: Concrete dependencies in core
- **Over-Engineering**: Clean architecture for simple CRUD

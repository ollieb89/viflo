# Test Data Management

> Strategies for managing test data in E2E tests

## Principles

1. **Isolation**: Each test creates its own data
2. **Cleanup**: Remove data after test completion
3. **API First**: Use API for setup, not UI
4. **Deterministic**: Same inputs produce same outputs

## API Seeding Pattern

```typescript
// fixtures/test-data.ts
export async function createUser(request: APIRequestContext, user: Partial<User> = {}) {
  const response = await request.post('/api/users', {
    data: {
      email: `test-${Date.now()}@example.com`,
      name: 'Test User',
      ...user
    }
  });
  return response.json();
}

export async function deleteUser(request: APIRequestContext, id: string) {
  await request.delete(`/api/users/${id}`);
}

// Usage in test
test('should edit user', async ({ page, request }) => {
  // Setup
  const user = await createUser(request, { name: 'John Doe' });
  
  // Test
  await page.goto(`/users/${user.id}/edit`);
  await page.fill('[data-testid="name"]', 'Jane Doe');
  await page.click('[data-testid="save"]');
  
  // Verify
  await expect(page.locator('[data-testid="user-name"]')).toHaveText('Jane Doe');
  
  // Cleanup
  await deleteUser(request, user.id);
});
```

## Factory Pattern

```typescript
// factories/user.factory.ts
export class UserFactory {
  private static counter = 0;
  
  static create(overrides: Partial<User> = {}): User {
    this.counter++;
    return {
      id: `user-${this.counter}`,
      email: `test-${this.counter}@example.com`,
      name: `Test User ${this.counter}`,
      role: 'user',
      ...overrides
    };
  }
  
  static createMany(count: number, overrides: Partial<User> = {}): User[] {
    return Array.from({ length: count }, () => this.create(overrides));
  }
}

// Usage
const user = UserFactory.create({ role: 'admin' });
const users = UserFactory.createMany(5);
```

## Database Seeding (Test DB)

```typescript
// setup/global-setup.ts
import { FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  // Connect to test database
  const db = await connectTestDatabase();
  
  // Seed reference data
  await db.seed('roles', [
    { id: 1, name: 'admin' },
    { id: 2, name: 'user' }
  ]);
  
  // Create test users
  await db.seed('users', [
    { email: 'admin@test.com', role_id: 1 },
    { email: 'user@test.com', role_id: 2 }
  ]);
}

export default globalSetup;
```

## Fixtures for Reusable Data

```typescript
// fixtures/test-data.ts
import { test as base } from '@playwright/test';

export const test = base.extend<{
  testUser: User;
  testProduct: Product;
}>({
  testUser: async ({ request }, use) => {
    const user = await createUser(request);
    await use(user);
    await deleteUser(request, user.id);
  },
  
  testProduct: async ({ request }, use) => {
    const product = await createProduct(request);
    await use(product);
    await deleteProduct(request, product.id);
  }
});

// Usage
test('should add to cart', async ({ page, testProduct }) => {
  await page.goto(`/products/${testProduct.id}`);
  await page.click('[data-testid="add-to-cart"]');
  // ...
});
```

## Environment-Specific Data

```typescript
// config/test-data.config.ts
const environments = {
  development: {
    apiUrl: 'http://localhost:8000',
    testUser: { email: 'dev@example.com', password: 'dev' }
  },
  staging: {
    apiUrl: 'https://staging-api.example.com',
    testUser: { email: 'staging@example.com', password: process.env.STAGING_PASSWORD! }
  }
};

export const testData = environments[process.env.TEST_ENV || 'development'];
```

## Cleanup Strategies

### 1. API Cleanup (Recommended)

```typescript
test.afterEach(async ({ request }) => {
  // Delete all test data created during test
  for (const id of createdIds) {
    await request.delete(`/api/items/${id}`);
  }
});
```

### 2. Database Transaction Rollback

```typescript
// For tests with direct DB access
test('should create item', async ({ db }) => {
  await db.transaction(async (trx) => {
    // All operations in this block will be rolled back
    const item = await trx.insert('items', { name: 'Test' });
    // ... test assertions
  });
});
```

### 3. Scheduled Cleanup

```typescript
// Global teardown
async function globalTeardown() {
  const db = await connectTestDatabase();
  
  // Delete test data older than 24 hours
  await db.query(`
    DELETE FROM users 
    WHERE email LIKE 'test-%@example.com' 
    AND created_at < NOW() - INTERVAL '24 hours'
  `);
}
```

## Test Data Builder

```typescript
// builders/item.builder.ts
export class ItemBuilder {
  private item: Partial<Item> = {};
  
  withName(name: string): this {
    this.item.name = name;
    return this;
  }
  
  withPrice(price: number): this {
    this.item.price = price;
    return this;
  }
  
  withCategory(categoryId: string): this {
    this.item.categoryId = categoryId;
    return this;
  }
  
  build(): Item {
    return {
      id: `item-${Date.now()}`,
      name: 'Default Item',
      price: 0,
      ...this.item
    } as Item;
  }
}

// Usage
const item = new ItemBuilder()
  .withName('Premium Product')
  .withPrice(99.99)
  .withCategory('electronics')
  .build();
```

## Shared Test Data

```typescript
// data/test-users.ts
export const TEST_USERS = {
  admin: {
    email: 'admin@test.com',
    password: 'Admin123!',
    role: 'admin'
  },
  standard: {
    email: 'user@test.com', 
    password: 'User123!',
    role: 'user'
  },
  newUser: {
    email: `new-${Date.now()}@test.com`,
    password: 'NewUser123!',
    role: 'user'
  }
} as const;

// Usage
test('admin can delete items', async ({ page }) => {
  await login(page, TEST_USERS.admin);
  // ...
});
```

## Best Practices

1. **Don't hardcode IDs**: Generate unique identifiers
2. **Use transactions**: Rollback when possible
3. **Parallel safety**: Ensure tests can run in parallel
4. **Clean slate**: Start each test with no existing data
5. **API over UI**: 10x faster for data setup

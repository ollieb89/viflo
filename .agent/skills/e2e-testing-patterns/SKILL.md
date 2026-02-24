---
name: e2e-testing-patterns
description: Master end-to-end testing with Playwright and Cypress to build reliable test suites that catch bugs, improve confidence, and enable fast deployment. Use when implementing E2E tests, debugging flaky tests, or establishing testing standards.
triggers:
  - Implementing end-to-end test automation
  - Debugging flaky tests
  - Testing critical user workflows
  - Setting up CI/CD test pipelines
  - Testing across multiple browsers
  - Validating accessibility requirements
---

# E2E Testing Patterns

Build reliable, fast, and maintainable end-to-end test suites that provide confidence to ship code quickly and catch regressions before users do.

## When to Use This Skill

- Implementing end-to-end test automation
- Debugging flaky or unreliable tests
- Testing critical user workflows
- Setting up CI/CD test pipelines
- Testing across multiple browsers
- Validating accessibility requirements
- Testing responsive designs
- Establishing E2E testing standards

## Core Concepts

### 1. E2E Testing Fundamentals

**What to Test with E2E:**

- Critical user journeys (login, checkout, signup)
- Complex interactions (drag-and-drop, multi-step forms)
- Cross-browser compatibility
- Real API integration
- Authentication flows

**What NOT to Test with E2E:**

- Unit-level logic (use unit tests)
- API contracts (use integration tests)
- Edge cases (too slow)
- Internal implementation details

### 2. Test Philosophy

**The Testing Pyramid:**

```
        /\
       /E2E\         ← Few, focused on critical paths
      /─────\
     /Integr\        ← More, test component interactions
    /────────\
   /Unit Tests\      ← Many, fast, isolated
  /────────────\
```

**Best Practices:**

- Test user behavior, not implementation
- Keep tests independent
- Make tests deterministic
- Optimize for speed
- Use data-testid, not CSS selectors

## Page Object Model Pattern

Encapsulate page logic in reusable classes for maintainable tests.

```typescript
// pages/LoginPage.ts
import { Page, Locator } from "@playwright/test";

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel("Email");
    this.passwordInput = page.getByLabel("Password");
    this.loginButton = page.getByRole("button", { name: "Login" });
  }

  async goto() {
    await this.page.goto("/login");
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
}

// Test using Page Object
import { test, expect } from "@playwright/test";
import { LoginPage } from "./pages/LoginPage";

test("successful login", async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login("user@example.com", "password123");
  await expect(page).toHaveURL("/dashboard");
});
```

## Framework Comparison

| Feature | Playwright | Cypress |
|---------|------------|---------|
| **Browsers** | Chromium, Firefox, WebKit | Chromium, Firefox, WebKit (partial) |
| **Speed** | Faster (parallel by default) | Fast (single-threaded) |
| **API** | Async/await | Chainable commands |
| **Mobile** | Device emulation built-in | Viewport only |
| **Trace** | Built-in trace viewer | Screenshots/videos |
| **Best For** | Large suites, cross-browser | Component testing, DX |

**Detailed guides:**
- [Playwright Setup and Patterns](./references/guides/playwright-setup.md)
- [Cypress Setup and Patterns](./references/guides/cypress-setup.md)

## Test Structure Best Practices

```typescript
// ❌ Bad selectors
cy.get(".btn.btn-primary.submit-button").click();
cy.get("div > form > div:nth-child(2) > input").type("text");

// ✅ Good selectors
cy.getByRole("button", { name: "Submit" }).click();
cy.getByLabel("Email address").type("user@example.com");
cy.get('[data-testid="email-input"]').type("user@example.com");
```

## Advanced Patterns

### Visual Regression Testing

```typescript
// With Playwright
import { test, expect } from "@playwright/test";

test("homepage looks correct", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveScreenshot("homepage.png", {
    fullPage: true,
    maxDiffPixels: 100,
  });
});
```

### Parallel Testing with Sharding

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    {
      name: "shard-1",
      use: { ...devices["Desktop Chrome"] },
      shard: { current: 1, total: 4 },
    },
    // ... more shards
  ],
});

// Run in CI
// npx playwright test --shard=1/4
```

### Accessibility Testing

```typescript
// Install: npm install @axe-core/playwright
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("page should not have accessibility violations", async ({ page }) => {
  await page.goto("/");
  const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
  expect(accessibilityScanResults.violations).toEqual([]);
});
```

## CI/CD Integration

Key configurations for reliable CI runs:

```typescript
// playwright.config.ts
export default defineConfig({
  forbidOnly: !!process.env.CI,  // Fail on .only in CI
  retries: process.env.CI ? 2 : 0,  // Retry in CI
  workers: process.env.CI ? 1 : undefined,  // Limit workers in CI
  reporter: [["html"], ["junit", { outputFile: "results.xml" }]],
});
```

## Best Practices

1. **Use Data Attributes**: `data-testid` or `data-cy` for stable selectors
2. **Avoid Brittle Selectors**: Don't rely on CSS classes or DOM structure
3. **Test User Behavior**: Click, type, see - not implementation details
4. **Keep Tests Independent**: Each test should run in isolation
5. **Clean Up Test Data**: Create and destroy test data in each test
6. **Use Page Objects**: Encapsulate page logic
7. **Meaningful Assertions**: Check actual user-visible behavior
8. **Optimize for Speed**: Mock when possible, parallel execution

## Common Pitfalls

- **Flaky Tests**: Use proper waits, not fixed timeouts
- **Slow Tests**: Mock external APIs, use parallel execution
- **Over-Testing**: Don't test every edge case with E2E
- **Coupled Tests**: Tests should not depend on each other
- **Poor Selectors**: Avoid CSS classes and nth-child
- **No Cleanup**: Clean up test data after each test
- **Testing Implementation**: Test user behavior, not internals

## Debugging Failing Tests

```typescript
// Playwright debugging
// 1. Run in headed mode
npx playwright test --headed

// 2. Run in debug mode
npx playwright test --debug

// 3. Add test.step for better reporting
test('checkout flow', async ({ page }) => {
    await test.step('Add item to cart', async () => {
        await page.goto('/products');
        await page.getByRole('button', { name: 'Add to Cart' }).click();
    });

    await test.step('Proceed to checkout', async () => {
        await page.goto('/cart');
        await page.getByRole('button', { name: 'Checkout' }).click();
    });
});

// 4. Inspect page state
await page.pause();  // Pauses execution, opens inspector
```

## Resources

- **references/guides/playwright-setup.md**: Playwright-specific setup and patterns
- **references/guides/cypress-setup.md**: Cypress-specific setup and patterns
- **references/playwright-best-practices.md**: Playwright-specific patterns
- **references/cypress-best-practices.md**: Cypress-specific patterns
- **references/flaky-test-debugging.md**: Debugging unreliable tests
- **assets/e2e-testing-checklist.md**: What to test with E2E
- **assets/selector-strategies.md**: Finding reliable selectors
- **scripts/test-analyzer.ts**: Analyze test flakiness and duration

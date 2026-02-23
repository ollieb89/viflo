# Playwright E2E Testing Template

> Minimal Playwright setup with Page Object Model

## Quick Start

```bash
# Install dependencies
npm install

# Install Playwright browsers
npx playwright install

# Run all tests
npm test

# Run tests in headed mode
npm run test:headed

# Run with UI mode
npm run test:ui

# Generate new test
npm run test:generate Product -- --page --crud
```

## Project Structure

```
.
├── e2e/
│   ├── auth.setup.ts       # Authentication setup
│   └── *.spec.ts           # Test specifications
├── pages/
│   ├── BasePage.ts         # Base page object
│   ├── LoginPage.ts        # Login page object
│   └── *.ts                # Other page objects
├── fixtures/
│   └── auth.json           # Authentication state
├── utils/
│   └── test-helpers.ts     # Test utilities
├── playwright.config.ts    # Playwright configuration
└── package.json
```

## Writing Tests

### Page Object Example

```typescript
// pages/ProductPage.ts
import { BasePage } from "./BasePage";

export class ProductPage extends BasePage {
  readonly url = "/products";

  async waitForLoad() {
    await this.page.locator('[data-testid="product-list"]').waitFor();
  }

  async createProduct(name: string) {
    await this.page.locator('[data-testid="new-button"]').click();
    await this.page.locator('[data-testid="name-input"]').fill(name);
    await this.page.locator('[data-testid="save-button"]').click();
  }
}
```

### Test Example

```typescript
// e2e/product.spec.ts
import { test, expect } from "@playwright/test";
import { ProductPage } from "../pages/ProductPage";

test.describe("Product", () => {
  let productPage: ProductPage;

  test.beforeEach(async ({ page }) => {
    productPage = new ProductPage(page);
    await productPage.goto();
  });

  test("should create product", async () => {
    await productPage.createProduct("Test Product");
    await expect(
      productPage.page.locator('[data-testid="success"]'),
    ).toBeVisible();
  });
});
```

## Configuration

### Environment Variables

```bash
BASE_URL=http://localhost:3000    # Target application URL
CI=true                           # CI mode (parallel off, retries on)
```

### Browsers

Configured browsers in `playwright.config.ts`:

- Chromium (Desktop Chrome)
- Firefox (Desktop Firefox)
- WebKit (Desktop Safari)
- Mobile Chrome (Pixel 5)
- Mobile Safari (iPhone 12)

## Best Practices

1. **Use Page Objects**: Encapsulate selectors and actions
2. **data-testid attributes**: Use for selectors, not CSS classes
3. **Independent tests**: Each test should set up its own data
4. **API for setup**: Use API calls to create test data, not UI
5. **Wait for network idle**: Ensure all requests complete

## Generating Tests

Use the generator for scaffolding:

```bash
# Basic page object
python .agent/skills/e2e-testing-patterns/scripts/generate-test.py Product --page

# With CRUD tests
python .agent/skills/e2e-testing-patterns/scripts/generate-test.py Product --page --crud

# Output to specific directory
python .agent/skills/e2e-testing-patterns/scripts/generate-test.py Product --page --output ./e2e
```

## CI/CD Integration

See `references/ci-cd-integration.md` for GitHub Actions workflow.

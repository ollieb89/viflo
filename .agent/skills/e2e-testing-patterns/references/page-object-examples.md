# Page Object Model Examples

> Common patterns for Playwright Page Objects

## Base Page Class

```typescript
// pages/BasePage.ts
import { Page, Locator, expect } from '@playwright/test';

export abstract class BasePage {
  readonly page: Page;
  abstract readonly url: string;

  constructor(page: Page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto(this.url);
    await this.waitForLoad();
  }

  abstract waitForLoad(): Promise<void>;

  async isLoaded(): Promise<boolean> {
    return this.page.url().includes(this.url);
  }
}
```

## Form Handling

```typescript
// pages/FormPage.ts
export class FormPage extends BasePage {
  readonly url = '/form';
  
  // Form elements
  readonly nameInput = this.page.locator('[data-testid="name-input"]');
  readonly emailInput = this.page.locator('[data-testid="email-input"]');
  readonly submitButton = this.page.locator('[data-testid="submit-button"]');
  readonly successMessage = this.page.locator('[data-testid="success-message"]');

  async waitForLoad() {
    await this.nameInput.waitFor({ state: 'visible' });
  }

  async fillForm(data: { name: string; email: string }) {
    await this.nameInput.fill(data.name);
    await this.emailInput.fill(data.email);
  }

  async submit() {
    await this.submitButton.click();
  }

  async fillAndSubmit(data: { name: string; email: string }) {
    await this.fillForm(data);
    await this.submit();
    await this.successMessage.waitFor({ state: 'visible' });
  }
}
```

## Table/List Interactions

```typescript
// pages/ListPage.ts
export class ListPage extends BasePage {
  readonly url = '/items';
  
  readonly items = this.page.locator('[data-testid="item-row"]');
  readonly searchInput = this.page.locator('[data-testid="search-input"]');

  async waitForLoad() {
    await this.items.first().waitFor({ state: 'visible' });
  }

  async getItemCount(): Promise<number> {
    return this.items.count();
  }

  async getItemByText(text: string): Promise<Locator> {
    return this.items.filter({ hasText: text });
  }

  async clickItem(name: string) {
    const item = await this.getItemByText(name);
    await item.locator('[data-testid="view-button"]').click();
  }

  async search(query: string) {
    await this.searchInput.fill(query);
    await this.page.keyboard.press('Enter');
    await this.page.waitForLoadState('networkidle');
  }
}
```

## Modal/Dialog Handling

```typescript
// components/Modal.ts
export class Modal {
  readonly modal = this.page.locator('[data-testid="modal"]');
  readonly confirmButton = this.page.locator('[data-testid="confirm-button"]');
  readonly cancelButton = this.page.locator('[data-testid="cancel-button"]');

  constructor(private page: Page) {}

  async isVisible(): Promise<boolean> {
    return this.modal.isVisible();
  }

  async confirm() {
    await this.confirmButton.click();
    await this.modal.waitFor({ state: 'hidden' });
  }

  async cancel() {
    await this.cancelButton.click();
    await this.modal.waitFor({ state: 'hidden' });
  }
}

// Usage in page
export class ItemPage extends BasePage {
  readonly deleteModal = new Modal(this.page);

  async deleteItem() {
    await this.page.locator('[data-testid="delete-button"]').click();
    await this.deleteModal.confirm();
  }
}
```

## File Upload

```typescript
// pages/UploadPage.ts
export class UploadPage extends BasePage {
  readonly url = '/upload';
  
  readonly fileInput = this.page.locator('input[type="file"]');
  readonly uploadButton = this.page.locator('[data-testid="upload-button"]');
  readonly progressBar = this.page.locator('[data-testid="progress-bar"]');

  async waitForLoad() {
    await this.fileInput.waitFor({ state: 'visible' });
  }

  async uploadFile(filePath: string) {
    await this.fileInput.setInputFiles(filePath);
    await this.uploadButton.click();
    await this.progressBar.waitFor({ state: 'hidden' });
  }
}
```

## Multi-Step Wizard

```typescript
// pages/WizardPage.ts
export class WizardPage extends BasePage {
  readonly url = '/wizard';
  
  async waitForLoad() {
    await this.page.locator('[data-testid="wizard-container"]').waitFor();
  }

  async getCurrentStep(): Promise<number> {
    const stepText = await this.page.locator('[data-testid="step-indicator"]').textContent();
    return parseInt(stepText?.match(/Step (\d+)/)?.[1] || '1');
  }

  async nextStep() {
    await this.page.locator('[data-testid="next-button"]').click();
    await this.page.waitForLoadState('networkidle');
  }

  async previousStep() {
    await this.page.locator('[data-testid="previous-button"]').click();
    await this.page.waitForLoadState('networkidle');
  }

  async completeWizard(data: WizardData) {
    // Step 1
    await this.fillStep1(data.step1);
    await this.nextStep();
    
    // Step 2
    await this.fillStep2(data.step2);
    await this.nextStep();
    
    // Submit
    await this.page.locator('[data-testid="submit-button"]').click();
  }
}
```

## Authenticated Pages

```typescript
// pages/DashboardPage.ts
export class DashboardPage extends BasePage {
  readonly url = '/dashboard';
  
  readonly userMenu = this.page.locator('[data-testid="user-menu"]');
  readonly logoutButton = this.page.locator('[data-testid="logout-button"]');

  async waitForLoad() {
    await this.userMenu.waitFor({ state: 'visible' });
  }

  async logout() {
    await this.userMenu.click();
    await this.logoutButton.click();
    await this.page.waitForURL('/login');
  }

  async getUserName(): Promise<string> {
    return this.userMenu.textContent() || '';
  }
}
```

## API-Driven Setup

```typescript
// pages/ApiDrivenPage.ts
export class ProductPage extends BasePage {
  readonly url = '/products';

  async createViaAPI(product: Partial<Product>): Promise<string> {
    const response = await this.page.request.post('/api/products', {
      data: product
    });
    const data = await response.json();
    return data.id;
  }

  async gotoProduct(id: string) {
    await this.page.goto(`/products/${id}`);
    await this.waitForLoad();
  }
}
```

## Best Practices

1. **Abstract selectors**: Don't expose raw locators
2. **Wait for states**: Always wait after actions
3. **Return values**: Return data, not locators
4. **Chain actions**: Combine common sequences
5. **Handle errors**: Add error checking

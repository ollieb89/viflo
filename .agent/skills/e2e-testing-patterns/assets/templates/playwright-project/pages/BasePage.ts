import { Page, Locator, expect } from '@playwright/test';

/**
 * Base Page Object
 * 
 * Common functionality shared across all page objects
 */
export abstract class BasePage {
  readonly page: Page;
  abstract readonly url: string;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * Navigate to the page
   */
  async goto() {
    await this.page.goto(this.url);
    await this.waitForLoad();
  }

  /**
   * Wait for page to be fully loaded
   * Override in child classes for specific loading indicators
   */
  abstract waitForLoad(): Promise<void>;

  /**
   * Check if page is currently loaded
   */
  async isLoaded(): Promise<boolean> {
    return this.page.url().includes(this.url);
  }

  /**
   * Wait for element to be visible
   */
  async waitForElement(locator: Locator, timeout?: number) {
    await locator.waitFor({ state: 'visible', timeout });
  }

  /**
   * Click element with retry
   */
  async safeClick(locator: Locator) {
    await locator.waitFor({ state: 'visible' });
    await locator.click();
  }

  /**
   * Fill form field
   */
  async fillField(locator: Locator, value: string) {
    await locator.waitFor({ state: 'visible' });
    await locator.fill(value);
  }

  /**
   * Get toast/notification message
   */
  async getToastMessage(): Promise<string> {
    const toast = this.page.locator('[data-testid="toast-message"]');
    await toast.waitFor({ state: 'visible' });
    return toast.textContent() || '';
  }

  /**
   * Confirm dialog
   */
  async confirmDialog() {
    await this.page.locator('[data-testid="confirm-button"]').click();
  }

  /**
   * Cancel dialog
   */
  async cancelDialog() {
    await this.page.locator('[data-testid="cancel-button"]').click();
  }
}

import { Page, expect } from '@playwright/test';

/**
 * Test helper utilities
 */

/**
 * Create a random test user
 */
export function generateTestUser() {
  const timestamp = Date.now();
  return {
    email: `test-${timestamp}@example.com`,
    name: `Test User ${timestamp}`,
    password: 'TestPassword123!',
  };
}

/**
 * Create a random test entity
 */
export function generateTestEntity(prefix: string) {
  const timestamp = Date.now();
  return {
    name: `${prefix} ${timestamp}`,
    description: `Test description ${timestamp}`,
  };
}

/**
 * Wait for network to be idle
 */
export async function waitForNetworkIdle(page: Page, timeout = 5000) {
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * Clear all form fields in a container
 */
export async function clearFormFields(page: Page, containerSelector: string) {
  const inputs = page.locator(`${containerSelector} input, ${containerSelector} textarea`);
  const count = await inputs.count();
  
  for (let i = 0; i < count; i++) {
    await inputs.nth(i).fill('');
  }
}

/**
 * Check if element has specific class
 */
export async function hasClass(locator: ReturnType<typeof expect>, className: string): Promise<boolean> {
  const classAttribute = await locator.toHaveAttribute('class', /.*/);
  const classes = (await locator.toHaveAttribute('class', /.*/)) || '';
  return classes.split(' ').includes(className);
}

/**
 * Retry an async operation
 */
export async function retry<T>(
  operation: () => Promise<T>,
  maxAttempts = 3,
  delay = 1000
): Promise<T> {
  let lastError: Error;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;
      if (attempt < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  throw lastError!;
}

import { test as setup, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

const authFile = 'fixtures/auth.json';

/**
 * Authentication setup
 * Run once to save authenticated state
 */
setup('authenticate', async ({ page }) => {
  const loginPage = new LoginPage(page);
  
  // Navigate and login
  await loginPage.goto();
  await loginPage.login('test@example.com', 'password123');
  
  // Wait for navigation after login
  await page.waitForURL('/dashboard');
  
  // Verify logged in
  await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  
  // Save authentication state
  await page.context().storageState({ path: authFile });
});

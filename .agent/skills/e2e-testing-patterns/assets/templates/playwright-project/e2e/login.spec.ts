import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

test.describe('Login', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  test('should display login form', async () => {
    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.submitButton).toBeVisible();
  });

  test('should login with valid credentials', async ({ page }) => {
    // Act
    await loginPage.login('test@example.com', 'password123');
    
    // Assert
    await page.waitForURL('/dashboard');
    await expect(page.locator('[data-testid="dashboard-page"]')).toBeVisible();
  });

  test('should show error with invalid credentials', async () => {
    // Act
    await loginPage.login('invalid@example.com', 'wrongpassword');
    
    // Assert
    await expect(loginPage.errorMessage).toBeVisible();
    await expect(loginPage.errorMessage).toContainText('Invalid');
  });

  test('should require email', async () => {
    // Act
    await loginPage.passwordInput.fill('password123');
    await loginPage.submitButton.click();
    
    // Assert - HTML5 validation
    const emailInput = loginPage.emailInput;
    await expect(emailInput).toHaveAttribute('required', '');
  });

  test('should require password', async () => {
    // Act
    await loginPage.emailInput.fill('test@example.com');
    await loginPage.submitButton.click();
    
    // Assert - HTML5 validation
    const passwordInput = loginPage.passwordInput;
    await expect(passwordInput).toHaveAttribute('required', '');
  });
});

import { test, expect } from '@playwright/test';

test.describe('Minimal App', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('should display the app', async ({ page }) => {
    await expect(page.locator('h1')).toHaveText('Minimal App');
    await expect(page.locator('text=No items yet')).toBeVisible();
  });

  test('should create a new item', async ({ page }) => {
    // Fill form
    await page.fill('input[placeholder="Item name"]', 'Test Item');
    await page.fill('input[placeholder="Description"]', 'Test Description');
    
    // Submit
    await page.click('button:has-text("Add")');
    
    // Verify
    await expect(page.locator('text=Test Item')).toBeVisible();
    await expect(page.locator('text=Test Description')).toBeVisible();
  });

  test('should complete an item', async ({ page }) => {
    // Create item first
    await page.fill('input[placeholder="Item name"]', 'Complete Me');
    await page.click('button:has-text("Add")');
    
    // Check the checkbox
    await page.click('input[type="checkbox"]');
    
    // Verify strikethrough
    const itemText = page.locator('text=Complete Me');
    await expect(itemText).toHaveCSS('text-decoration', /line-through/);
  });

  test('should delete an item', async ({ page }) => {
    // Create item
    await page.fill('input[placeholder="Item name"]', 'Delete Me');
    await page.click('button:has-text("Add")');
    
    // Verify it exists
    await expect(page.locator('text=Delete Me')).toBeVisible();
    
    // Delete
    await page.click('button:has-text("Delete")');
    
    // Verify it's gone
    await expect(page.locator('text=Delete Me')).not.toBeVisible();
  });
});

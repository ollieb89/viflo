#!/usr/bin/env python3
"""
Generate Playwright E2E test files with Page Object Model.

Usage:
    python generate-test.py Login --page
    python generate-test.py Product --page --crud
    python generate-test.py Checkout --page --flows

Options:
    --page    Generate Page Object class
    --crud    Generate CRUD operation tests
    --flows   Generate user flow tests
"""

import argparse
import re
import sys
from pathlib import Path


PAGE_TEMPLATE = '''import {{ Page, Locator, expect }} from '@playwright/test';

/**
 * {name} Page Object
 * 
 * Encapsulates selectors and actions for the {name} page
 */
export class {name}Page {{
  readonly page: Page;
  readonly url: string;
  
  // Locators{locators}

  constructor(page: Page) {{
    this.page = page;
    this.url = '/{url_path}';
    {constructor_init}
  }}

  /**
   * Navigate to the page
   */
  async goto() {{
    await this.page.goto(this.url);
    await this.waitForLoad();
  }}

  /**
   * Wait for page to be fully loaded
   */
  async waitForLoad() {{
    // Override with specific loading indicators
    await this.page.waitForLoadState('networkidle');
  }}

  /**
   * Check if page is loaded
   */
  async isLoaded(): Promise<boolean> {{
    return this.page.url().includes(this.url);
  }}
{actions}
}}
'''


SPEC_TEMPLATE = '''import {{ test, expect }} from '@playwright/test';
import {{ {name}Page }} from './{name}Page';

/**
 * {name} E2E Tests
 * 
 * Generated test suite for {name} feature
 */

test.describe('{name}', () => {{
  let {var_name}Page: {name}Page;

  test.beforeEach(async ({{ page }}) => {{
    {var_name}Page = new {name}Page(page);
    await {var_name}Page.goto();
  }});
{tests}
}});
'''


CRUD_TESTS = '''
  test('should create new {resource}', async () => {{
    // Arrange
    await {var_name}Page.clickNew();
    
    // Act
    await {var_name}Page.fillForm({{
      name: 'Test {resource}',
      // Add other required fields
    }});
    await {var_name}Page.clickSave();
    
    // Assert
    await expect({var_name}Page.page).toHaveURL(/\\/{url_path}/);
    await expect({var_name}Page.page.locator('[data-testid="success-message"]')).toBeVisible();
  }});

  test('should read {resource} details', async () => {{
    // Arrange
    const {var_name}Id = '1'; // Use API to create test data
    await {var_name}Page.gotoDetail({var_name}Id);
    
    // Assert
    await expect({var_name}Page.page.locator('[data-testid="{url_path}-detail"]')).toBeVisible();
  }});

  test('should update {resource}', async () => {{
    // Arrange
    const {var_name}Id = '1';
    await {var_name}Page.gotoDetail({var_name}Id);
    await {var_name}Page.clickEdit();
    
    // Act
    await {var_name}Page.fillForm({{
      name: 'Updated {resource}',
    }});
    await {var_name}Page.clickSave();
    
    // Assert
    await expect({var_name}Page.page.locator('[data-testid="success-message"]')).toBeVisible();
  }});

  test('should delete {resource}', async () => {{
    // Arrange
    const {var_name}Id = '1';
    await {var_name}Page.gotoDetail({var_name}Id);
    
    // Act
    await {var_name}Page.clickDelete();
    await {var_name}Page.confirmDelete();
    
    // Assert
    await expect({var_name}Page.page).toHaveURL(`/{url_path}`);
    await expect({var_name}Page.page.locator('[data-testid="success-message"]')).toBeVisible();
  }});
'''


def to_pascal_case(name: str) -> str:
    """Convert to PascalCase."""
    return ''.join(word.capitalize() for word in name.split('-'))


def to_camel_case(name: str) -> str:
    """Convert to camelCase."""
    words = name.split('-')
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])


def to_kebab_case(name: str) -> str:
    """Convert to kebab-case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()


def generate_locators() -> str:
    """Generate common locator definitions."""
    locators = [
        ('submitButton', '[data-testid="submit-button"]'),
        ('cancelButton', '[data-testid="cancel-button"]'),
        ('form', '[data-testid="form"]'),
        ('list', '[data-testid="list"]'),
        ('loadingSpinner', '[data-testid="loading-spinner"]'),
    ]
    
    lines = []
    for name, selector in locators:
        lines.append(f"\n  readonly {name}: Locator;")
    
    return ''.join(lines)


def generate_constructor_init() -> str:
    """Generate constructor initialization."""
    locators = ['submitButton', 'cancelButton', 'form', 'list', 'loadingSpinner']
    lines = []
    for locator in locators:
        lines.append(f"    this.{locator} = page.locator('[data-testid=\"{to_kebab_case(locator)}\"]');")
    return '\n'.join(lines)


def generate_actions(name: str) -> str:
    """Generate common page actions."""
    var_name = to_camel_case(name)
    
    return f'''
  /**
   * Click submit button
   */
  async clickSave() {{
    await this.submitButton.click();
  }}

  /**
   * Click cancel button
   */
  async clickCancel() {{
    await this.cancelButton.click();
  }}

  /**
   * Fill form with data
   */
  async fillForm(data: Record<string, string>) {{
    for (const [key, value] of Object.entries(data)) {{
      const field = this.page.locator(`[data-testid="${{key}}-input"]`);
      await field.fill(value);
    }}
  }}

  /**
   * Navigate to detail page
   */
  async gotoDetail(id: string) {{
    await this.page.goto(`${{this.url}}/${{id}}`);
    await this.waitForLoad();
  }}

  /**
   * Click new/create button
   */
  async clickNew() {{
    await this.page.locator('[data-testid="new-button"]').click();
  }}

  /**
   * Click edit button
   */
  async clickEdit() {{
    await this.page.locator('[data-testid="edit-button"]').click();
  }}

  /**
   * Click delete button
   */
  async clickDelete() {{
    await this.page.locator('[data-testid="delete-button"]').click();
  }}

  /**
   * Confirm delete in modal
   */
  async confirmDelete() {{
    await this.page.locator('[data-testid="confirm-delete-button"]').click();
  }}
'''


def generate_tests(name: str, crud: bool, flows: bool) -> str:
    """Generate test cases."""
    var_name = to_camel_case(name)
    url_path = to_kebab_case(name) + 's'  # Pluralize
    
    tests = []
    
    # Always add basic navigation test
    tests.append(f'''  test('should display {name} page', async () => {{
    // Assert
    await expect({var_name}Page.page).toHaveURL(/{url_path}/);
    await expect({var_name}Page.page.locator('h1')).toContainText('{name}');
  }});
''')
    
    if crud:
        tests.append(CRUD_TESTS.format(
            name=name,
            var_name=var_name,
            resource=url_path,
            url_path=url_path
        ))
    
    if flows:
        tests.append(f'''  test('should complete user flow', async () => {{
    // Arrange
    await {var_name}Page.clickNew();
    
    // Act - Complete the workflow
    await {var_name}Page.fillForm({{
      name: 'Test Entry',
    }});
    await {var_name}Page.clickSave();
    
    // Assert
    await expect({var_name}Page.page.locator('[data-testid="success-message"]')).toBeVisible();
  }});
''')
    
    return '\n'.join(tests)


def generate_test_files(name: str, page: bool, crud: bool, flows: bool, output_dir: str):
    """Generate all test files."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    
    pascal_name = to_pascal_case(name)
    var_name = to_camel_case(name)
    url_path = to_kebab_case(name) + 's'
    
    files_created = []
    
    # Generate Page Object
    if page:
        page_content = PAGE_TEMPLATE.format(
            name=pascal_name,
            url_path=url_path,
            locators=generate_locators(),
            constructor_init=generate_constructor_init(),
            actions=generate_actions(pascal_name)
        )
        page_file = output / f"{pascal_name}Page.ts"
        page_file.write_text(page_content)
        files_created.append(f"{pascal_name}Page.ts")
        print(f"✅ Created: {pascal_name}Page.ts")
    
    # Generate Test Spec
    spec_content = SPEC_TEMPLATE.format(
        name=pascal_name,
        var_name=var_name,
        tests=generate_tests(pascal_name, crud, flows)
    )
    spec_file = output / f"{to_kebab_case(name)}.spec.ts"
    spec_file.write_text(spec_content)
    files_created.append(f"{to_kebab_case(name)}.spec.ts")
    print(f"✅ Created: {to_kebab_case(name)}.spec.ts")
    
    # Generate data-testid reference
    data_testid_content = f'''# Data Test IDs for {pascal_name}

Add these data-testid attributes to your components:

## Page Elements
- `[data-testid="{url_path}-page"]` - Page container
- `[data-testid="{url_path}-list"]` - List/table container
- `[data-testid="{url_path}-detail"]` - Detail view container

## Buttons
- `[data-testid="new-button"]` - Create new item
- `[data-testid="edit-button"]` - Edit item
- `[data-testid="delete-button"]` - Delete item
- `[data-testid="submit-button"]` - Save/submit form
- `[data-testid="cancel-button"]` - Cancel action
- `[data-testid="confirm-delete-button"]` - Confirm delete

## Form Elements
- `[data-testid="form"]` - Form container
- `[data-testid="<field>-input"]` - Input fields (e.g., "name-input")

## Feedback
- `[data-testid="loading-spinner"]` - Loading state
- `[data-testid="success-message"]` - Success notification
- `[data-testid="error-message"]` - Error notification
'''
    data_testid_file = output / f"{to_kebab_case(name)}-data-testids.md"
    data_testid_file.write_text(data_testid_content)
    files_created.append(f"{to_kebab_case(name)}-data-testids.md")
    print(f"✅ Created: {to_kebab_case(name)}-data-testids.md")
    
    print(f"\n🎉 Generated E2E tests for '{name}'!")
    print(f"\nNext steps:")
    print(f"  1. Add the data-testid attributes to your components")
    print(f"  2. Review and customize the generated Page Object")
    print(f"  3. Run tests: npx playwright test {to_kebab_case(name)}.spec.ts")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Playwright E2E test files"
    )
    parser.add_argument(
        "name",
        help="Feature name (e.g., 'login', 'user-profile', 'Product')"
    )
    parser.add_argument(
        "--page",
        action="store_true",
        help="Generate Page Object class"
    )
    parser.add_argument(
        "--crud",
        action="store_true",
        help="Generate CRUD operation tests"
    )
    parser.add_argument(
        "--flows",
        action="store_true",
        help="Generate user flow tests"
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Output directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Default to --page if no options specified
    if not any([args.page, args.crud, args.flows]):
        args.page = True
    
    generate_test_files(args.name, args.page, args.crud, args.flows, args.output)


if __name__ == "__main__":
    main()

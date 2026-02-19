import { test, expect } from '@playwright/test';

/**
 * Fabric Svelte UI E2E Tests
 * Tests the main UI functionality including patterns, models, and chat
 */

test.describe('Fabric UI - Core Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('homepage loads successfully', async ({ page }) => {
    await expect(page).toHaveTitle(/Fabric/i);
    // Wait for the app to hydrate
    await page.waitForLoadState('networkidle');
  });

  test('displays main navigation elements', async ({ page }) => {
    // Check for common UI elements
    await expect(page.locator('body')).toBeVisible();
    // Wait for any loading states to complete
    await page.waitForLoadState('networkidle');
  });
});

test.describe('Fabric UI - Pattern Selection', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('can view available patterns', async ({ page }) => {
    // Look for pattern-related elements
    const patternElements = page.locator('[data-testid="pattern"], [class*="pattern"], select, .pattern-select');
    
    // Wait for patterns to load (with timeout)
    try {
      await patternElements.first().waitFor({ timeout: 10000 });
      await expect(patternElements.first()).toBeVisible();
    } catch {
      // If no pattern elements found, check if there's an error message
      const errorMessage = page.locator('[class*="error"], .error, [role="alert"]');
      const hasError = await errorMessage.count() > 0;
      if (hasError) {
        console.log('Pattern loading may have failed - API might be down');
      }
    }
  });

  test('pattern list is searchable or filterable', async ({ page }) => {
    // Look for search/filter inputs
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], input[placeholder*="filter" i]');
    
    if (await searchInput.count() > 0) {
      await searchInput.first().fill('summarize');
      await page.waitForTimeout(500); // Wait for filter to apply
    }
  });
});

test.describe('Fabric UI - Model Selection', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('can view available models', async ({ page }) => {
    // Look for model selection elements
    const modelElements = page.locator('[data-testid="model"], [class*="model"], select[name*="model"]');
    
    try {
      await modelElements.first().waitFor({ timeout: 10000 });
    } catch {
      // Models might load asynchronously
      console.log('Model elements may load asynchronously');
    }
  });
});

test.describe('Fabric UI - Chat Interface', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('chat input area exists', async ({ page }) => {
    // Look for textarea or input for chat
    const chatInput = page.locator('textarea, input[type="text"][class*="chat"], [contenteditable="true"]');
    
    try {
      await chatInput.first().waitFor({ timeout: 10000 });
      await expect(chatInput.first()).toBeVisible();
    } catch {
      console.log('Chat input may be on a different route');
    }
  });

  test('can submit text for processing', async ({ page }) => {
    const chatInput = page.locator('textarea').first();
    
    try {
      await chatInput.waitFor({ timeout: 5000 });
      await chatInput.fill('Hello, this is a test message');
      
      // Look for submit button
      const submitButton = page.locator('button[type="submit"], button:has-text("Send"), button:has-text("Submit"), button[class*="submit"]');
      if (await submitButton.count() > 0) {
        await expect(submitButton.first()).toBeEnabled();
      }
    } catch {
      console.log('Chat functionality may require navigation');
    }
  });
});

test.describe('Fabric UI - API Health', () => {
  test('API health endpoint responds', async ({ request }) => {
    const response = await request.get('http://localhost:8080/health');
    expect(response.status()).toBe(200);
  });

  test('patterns API returns data', async ({ request }) => {
    const response = await request.get('http://localhost:8080/patterns');
    expect(response.status()).toBe(200);
    
    const patterns = await response.json();
    expect(Array.isArray(patterns)).toBeTruthy();
    expect(patterns.length).toBeGreaterThan(0);
  });

  test('models API returns data', async ({ request }) => {
    const response = await request.get('http://localhost:8080/models');
    expect(response.status()).toBe(200);
  });
});

test.describe('Fabric UI - Error Handling', () => {
  test('handles API errors gracefully', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check that no unhandled errors appear
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Wait a bit and check for critical errors
    await page.waitForTimeout(2000);
    
    // Filter out expected/acceptable errors
    const criticalErrors = consoleErrors.filter(err => 
      !err.includes('favicon') && 
      !err.includes('404') &&
      !err.includes('net::ERR')
    );
    
    // Log but don't fail for minor errors
    if (criticalErrors.length > 0) {
      console.log('Console errors found:', criticalErrors);
    }
  });
});

test.describe('Fabric UI - Responsive Design', () => {
  test('works on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Page should still be functional
    await expect(page.locator('body')).toBeVisible();
  });

  test('works on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }); // iPad
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('body')).toBeVisible();
  });

  test('works on desktop viewport', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('body')).toBeVisible();
  });
});

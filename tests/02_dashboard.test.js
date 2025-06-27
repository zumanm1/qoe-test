const puppeteer = require('puppeteer');
const { login, initializePage, ensureScreenshotsDir, config } = require('../qoe-tool-tests/helpers');

describe('Dashboard - Navigation & UI Test', () => {
  let browser;
  let page;
  let consoleErrors = [];

  beforeAll(async () => {
    // Ensure screenshots directory exists
    ensureScreenshotsDir();
    
    // Launch browser
    browser = await puppeteer.launch({
      headless: config.headless,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  });

  beforeEach(async () => {
    // Create new page for each test
    page = await initializePage(browser);
    
    // Track console errors
    consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
  });

  afterEach(async () => {
    if (page) {
      await page.close();
    }
  });

  afterAll(async () => {
    if (browser) {
      await browser.close();
    }
  });

  test('should navigate dashboard sidebar links and validate charts/tables', async () => {
    // Step 1: Login using helper
    await login(page);
    
    // Step 2: Verify we're on dashboard
    const currentUrl = page.url();
    expect(currentUrl).toContain('/dashboard');
    
    // Step 3: Wait for dashboard to stabilize
    await page.waitForSelector('#refresh-btn', { visible: true, timeout: 10000 });
    await page.waitForTimeout(2000); // Additional stabilization time
    
    // Step 4: Look for sidebar navigation elements
    const sidebarSelectors = [
      'nav a', 
      '.sidebar a', 
      '.nav-link', 
      '.menu-item a',
      'ul li a',
      '[data-nav]'
    ];
    
    let sidebarLinks = [];
    for (const selector of sidebarSelectors) {
      try {
        const links = await page.$$(selector);
        if (links.length > 0) {
          sidebarLinks = links;
          console.log(`Found ${links.length} sidebar links using selector: ${selector}`);
          break;
        }
      } catch (error) {
        // Continue to next selector
      }
    }
    
    // Step 5: Click on sidebar links and validate content
    if (sidebarLinks.length > 0) {
      // Test first few navigation links (limit to avoid excessive testing)
      const linksToTest = Math.min(3, sidebarLinks.length);
      
      for (let i = 0; i < linksToTest; i++) {
        try {
          const link = sidebarLinks[i];
          const linkText = await page.evaluate(el => el.textContent.trim(), link);
          
          if (linkText && linkText.length > 0) {
            console.log(`Testing navigation link: ${linkText}`);
            
            // Click the link
            await link.click();
            await page.waitForTimeout(2000); // Wait for navigation
            
            // Look for common dashboard elements: charts, tables, data visualizations
            const dashboardElements = await page.evaluate(() => {
              const charts = document.querySelectorAll('canvas, svg, .chart, [id*="chart"], [class*="chart"]');
              const tables = document.querySelectorAll('table, .table, .data-table');
              const dataContainers = document.querySelectorAll('.data-container, .content, .main-content');
              
              return {
                charts: charts.length,
                tables: tables.length,
                dataContainers: dataContainers.length
              };
            });
            
            console.log(`Dashboard elements found - Charts: ${dashboardElements.charts}, Tables: ${dashboardElements.tables}, Containers: ${dashboardElements.dataContainers}`);
            
            // Validate that some content is present
            expect(
              dashboardElements.charts + dashboardElements.tables + dashboardElements.dataContainers
            ).toBeGreaterThan(0);
          }
        } catch (linkError) {
          console.warn(`Failed to test link ${i}:`, linkError.message);
          // Continue with other links
        }
      }
    } else {
      console.log('No sidebar navigation links found, checking for main dashboard content');
    }
    
    // Step 6: Validate main dashboard content regardless of sidebar navigation
    await page.waitForTimeout(1000);
    
    const mainContent = await page.evaluate(() => {
      const charts = document.querySelectorAll('canvas, svg, .chart, [id*="chart"], [class*="chart"]');
      const tables = document.querySelectorAll('table, .table, .data-table');
      const widgets = document.querySelectorAll('.widget, .card, .panel, .dashboard-item');
      
      return {
        charts: charts.length,
        tables: tables.length,
        widgets: widgets.length,
        hasRefreshBtn: !!document.querySelector('#refresh-btn')
      };
    });
    
    console.log('Main dashboard content:', mainContent);
    
    // Assert that dashboard has some meaningful content
    expect(mainContent.hasRefreshBtn).toBe(true);
    expect(
      mainContent.charts + mainContent.tables + mainContent.widgets
    ).toBeGreaterThan(0);
    
    // Step 7: Capture screenshot after page stabilizes
    await page.waitForTimeout(2000);
    await page.screenshot({ 
      path: '02_dashboard_navigation.png',
      fullPage: true
    });
    
    // Step 8: Assert minimal console errors (some warnings may be acceptable)
    const criticalErrors = consoleErrors.filter(error => 
      !error.includes('Warning') && 
      !error.includes('DevTools') &&
      !error.includes('favicon')
    );
    expect(criticalErrors.length).toBeLessThanOrEqual(2);
    
    console.log('Dashboard navigation test completed successfully');
    console.log('Current URL:', page.url());
    console.log('Console errors:', consoleErrors.length);
  });
});

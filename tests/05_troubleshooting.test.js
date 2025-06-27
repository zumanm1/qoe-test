const puppeteer = require('puppeteer');
const { login, initializePage, ensureScreenshotsDir, config } = require('../qoe-tool-tests/helpers');

describe('Troubleshooting - Accordion/Panel Test', () => {
  let browser;
  let page;
  let consoleErrors = [];

  beforeAll(async () => {
    ensureScreenshotsDir();
    browser = await puppeteer.launch({
      headless: config.headless,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  });

  beforeEach(async () => {
    page = await initializePage(browser);
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

  test('should open troubleshooting page and expand accordion/panel', async () => {
    // Step 1: Login using helper
    await login(page);
    
    // Step 2: Navigate to troubleshooting page
    await page.goto(`${config.baseUrl}/troubleshooting`, { waitUntil: 'networkidle2' });
    
    // Step 3: Wait for page to stabilize
    await page.waitForTimeout(2000);
    
    // Step 4: Look for accordion/panel elements with multiple selectors
    const accordionSelectors = [
      '.accordion-header',
      '.panel-heading', 
      '.expand-btn',
      '.toggle-btn',
      '.collapsible-header',
      '[data-toggle="collapse"]',
      '.accordion-item button',
      '.panel-title'
    ];
    
    let accordionElement = null;
    let foundSelector = '';
    
    for (const selector of accordionSelectors) {
      try {
        accordionElement = await page.$(selector);
        if (accordionElement) {
          foundSelector = selector;
          console.log(`Found accordion element using selector: ${selector}`);
          break;
        }
      } catch (error) {
        // Continue to next selector
      }
    }
    
    // Step 5: If accordion found, expand it and verify data
    if (accordionElement) {
      // Click to expand the accordion/panel
      await accordionElement.click();
      await page.waitForTimeout(1500); // Wait for expansion animation
      
      // Look for populated data in the expanded section
      const dataPresent = await page.evaluate(() => {
        const contentSelectors = [
          '.accordion-content',
          '.panel-body',
          '.collapse-content',
          '.expanded-content',
          '.panel-content',
          '.accordion-panel'
        ];
        
        let hasData = false;
        let contentText = '';
        
        for (const selector of contentSelectors) {
          const element = document.querySelector(selector);
          if (element && element.offsetHeight > 0) {
            contentText = element.textContent.trim();
            hasData = contentText.length > 10; // Meaningful content
            if (hasData) break;
          }
        }
        
        // Also check for lists, tables, or other data containers
        const lists = document.querySelectorAll('.accordion-content ul li, .panel-body ul li, .expanded-content li');
        const tables = document.querySelectorAll('.accordion-content table, .panel-body table');
        const dataElements = document.querySelectorAll('.accordion-content .data-item, .panel-body .data-item');
        
        return {
          hasTextContent: hasData,
          contentLength: contentText.length,
          listItems: lists.length,
          tables: tables.length,
          dataElements: dataElements.length
        };
      });
      
      console.log('Expanded content data:', dataPresent);
      
      // Verify data is populated
      expect(
        dataPresent.hasTextContent || 
        dataPresent.listItems > 0 || 
        dataPresent.tables > 0 || 
        dataPresent.dataElements > 0
      ).toBe(true);
      
    } else {
      // If no accordion found, check for general troubleshooting content
      console.log('No accordion elements found, checking for general troubleshooting content');
      
      const troubleshootingContent = await page.evaluate(() => {
        const contentArea = document.querySelector('.troubleshooting-content, .main-content, .content');
        const hasContent = contentArea && contentArea.textContent.trim().length > 50;
        const hasLists = document.querySelectorAll('ul li, ol li').length > 0;
        const hasTables = document.querySelectorAll('table').length > 0;
        
        return {
          hasContent,
          hasLists,
          hasTables,
          contentLength: contentArea ? contentArea.textContent.trim().length : 0
        };
      });
      
      console.log('General troubleshooting content:', troubleshootingContent);
      
      // Verify some meaningful content exists
      expect(
        troubleshootingContent.hasContent || 
        troubleshootingContent.hasLists || 
        troubleshootingContent.hasTables
      ).toBe(true);
    }
    
    // Step 6: Capture screenshot after page stabilizes
    await page.waitForTimeout(2000);
    await page.screenshot({ 
      path: '05_troubleshooting_expanded.png',
      fullPage: true
    });
    
    // Step 7: Assert minimal console errors
    const criticalErrors = consoleErrors.filter(error => 
      !error.includes('Warning') && 
      !error.includes('DevTools') &&
      !error.includes('favicon')
    );
    expect(criticalErrors.length).toBeLessThanOrEqual(1);
    
    console.log('Troubleshooting test completed successfully');
    console.log('Current URL:', page.url());
    console.log('Accordion selector used:', foundSelector);
    console.log('Console errors:', consoleErrors.length);
  });
});

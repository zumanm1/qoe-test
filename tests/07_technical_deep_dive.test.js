const puppeteer = require('puppeteer');
const { login, initializePage, ensureScreenshotsDir, config } = require('../qoe-tool-tests/helpers');

describe('Technical Deep Dive - Code Blocks/Plots Test', () => {
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

  test('should open Technical Deep Dive and verify code blocks and plots', async () => {
    // Step 1: Login using helper
    await login(page);
    
    // Step 2: Navigate to Technical Deep Dive
    await page.goto(`${config.baseUrl}/feature04/technical-deep-dive`, { waitUntil: 'networkidle2' });
    
    // Step 3: Wait for page to stabilize
    await page.waitForTimeout(2000);
    
    // Step 4: Look for code blocks, plots, or technical diagrams
    const deepDiveElements = await page.evaluate(() => {
      // Collection of elements indicative of technical content
      const codeBlocks = document.querySelectorAll('pre, code, .code-block, [class*="code"]');
      const plots = document.querySelectorAll('canvas, svg, .plot, .diagram, [id*="plot"], [class*="plot"], .visualization');
      const technicalFigures = document.querySelectorAll('.technical-figure, img, figure, .image, .illustration');
      
      // Check for visible, reasonable size elements
      const visibleCodeBlocks = Array.from(codeBlocks).filter(el => el.offsetWidth > 50 && el.offsetHeight > 20);
      const visiblePlots = Array.from(plots).filter(el => el.offsetWidth > 100 && el.offsetHeight > 50);
      const visibleFigures = Array.from(technicalFigures).filter(el => el.offsetWidth > 50 && el.offsetHeight > 50);
      
      return {
        totalCodeBlocks: codeBlocks.length,
        visibleCodeBlocks: visibleCodeBlocks.length,
        totalPlots: plots.length,
        visiblePlots: visiblePlots.length,
        totalFigures: technicalFigures.length,
        visibleFigures: visibleFigures.length
      };
    });
    
    console.log('Deep Dive elements found:', deepDiveElements);
    
    // Step 5: Verify that technical elements are present
    const meaningfulTechContent = deepDiveElements.visibleCodeBlocks + deepDiveElements.visiblePlots + deepDiveElements.visibleFigures;
    expect(meaningfulTechContent).toBeGreaterThan(0);

    // Step 6: Additional checks for specific Deep Dive content
    const additionalTechContent = await page.evaluate(() => {
      const syntaxHighlighter = document.querySelectorAll('.hljs, .prism-code, .syntax-highlight');
      const dataTables = document.querySelectorAll('table, .data-table, .info-table, .table-container');
      const resultDisplays = document.querySelectorAll('.result-display, .result-section, .result-card');
      
      return {
        syntaxHighlighter: syntaxHighlighter.length,
        dataTables: dataTables.length,
        resultDisplays: resultDisplays.length
      };
    });
    
    console.log('Additional Deep Dive content:', additionalTechContent);
    
    // Verify that additional technical content is meaningful
    expect(
      additionalTechContent.syntaxHighlighter +
      additionalTechContent.dataTables +
      additionalTechContent.resultDisplays
    ).toBeGreaterThan(0);

    // Step 7: Wait for any dynamic elements to load complete
    await page.waitForTimeout(2000);

    // Step 8: Capture screenshot after content stabilizes
    await page.screenshot({ 
      path: '07_technical_deep_dive.png',
      fullPage: true
    });

    // Step 9: Assert minimal console errors
    const criticalErrors = consoleErrors.filter(error => 
      !error.includes('Warning') && 
      !error.includes('DevTools') &&
      !error.includes('favicon') &&
      !error.includes('Code')
    );
    expect(criticalErrors.length).toBeLessThanOrEqual(2);

    console.log('Technical Deep Dive test completed successfully');
    console.log('Current URL:', page.url());
    console.log('Total tech content identified:', meaningfulTechContent);
    console.log('Console errors:', consoleErrors.length);
  });
});

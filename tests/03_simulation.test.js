const puppeteer = require('puppeteer');
const { login, initializePage, ensureScreenshotsDir, config } = require('../qoe-tool-tests/helpers');

describe('Simulation - Lightweight Run Test', () => {
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

  test('should run a simulation and verify results table', async () => {
    await login(page);
    await page.goto(`${config.baseUrl}/simulation`, { waitUntil: 'networkidle2' });

    await page.waitForSelector('.simulation-form', { visible: true, timeout: 10000 });
    await page.click(".run-simulation-btn");
    await page.waitForTimeout(2000);

    const resultsVisible = await page.waitForSelector('.results-table', { visible: true, timeout: 10000 });
    expect(resultsVisible).toBeTruthy();

    await page.screenshot({
      path: '03_simulation_results.png',
      fullPage: true
    });

    const criticalErrors = consoleErrors.filter(error => !error.includes('Warning'));
    expect(criticalErrors.length).toBe(0);
  });
});


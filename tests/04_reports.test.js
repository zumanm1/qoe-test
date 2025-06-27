const puppeteer = require('puppeteer');
const { login, initializePage, ensureScreenshotsDir, config } = require('../qoe-tool-tests/helpers');

describe('Reports - Generate Test', () => {
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

  test('should navigate to reports and trigger a report generation', async () => {
    await login(page);
    await page.goto(`${config.baseUrl}/reports`, { waitUntil: 'networkidle2' });

    const generateButton = await Promise.race([
      page.$('.generate-report-btn'),
      page.$('button:contains("Generate")'),
      page.$('input[value="Generate"]')
    ]);

    if (generateButton) {
      await Promise.all([
        generateButton.click(),
        page.waitForNavigation({ waitUntil: 'networkidle2' })
      ]);

      const downloadableLink = await page.waitForSelector('.download-link', { visible: true, timeout: 10000 });
      expect(downloadableLink).toBeTruthy();
    } else {
      throw new Error('Generate button not found');
    }

    await page.screenshot({
      path: '04_reports_generate.png',
      fullPage: true
    });

    const criticalErrors = consoleErrors.filter(error => !error.includes('Warning'));
    expect(criticalErrors.length).toBe(0);
  });
});


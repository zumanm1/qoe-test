const puppeteer = require('puppeteer');
const { login, initializePage, ensureScreenshotsDir, config } = require('../helpers');

describe('QoE Tool Login Tests', () => {
  let browser;
  let page;

  beforeAll(async () => {
    // Ensure screenshots directory exists
    ensureScreenshotsDir();
    
    // Launch browser with configuration
    browser = await puppeteer.launch({
      headless: config.headless,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  });

  beforeEach(async () => {
    page = await initializePage(browser);
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

  test('should login successfully with admin credentials', async () => {
    // Use the login helper function
    await login(page);
    
    // Verify we're on the dashboard by checking for the refresh button
    const refreshBtn = await page.$('#refresh-btn');
    expect(refreshBtn).toBeTruthy();
    
    // Additional verification - check page title or other dashboard elements
    const title = await page.title();
    console.log('Page title after login:', title);
    
    // Take a final screenshot
    if (config.saveScreens) {
      await page.screenshot({ 
        path: `${config.screenshotsDir}/dashboard-loaded-${Date.now()}.png`,
        fullPage: true
      });
    }
  });

  test('should handle login form presence', async () => {
    // Navigate to base URL
    await page.goto(config.baseUrl, { waitUntil: 'networkidle2' });
    
    // Check if login form elements are present
    const usernameField = await page.$('input[type="text"], input[name="username"], input[id="username"]');
    const passwordField = await page.$('input[type="password"], input[name="password"], input[id="password"]');
    
    expect(usernameField).toBeTruthy();
    expect(passwordField).toBeTruthy();
  });
});

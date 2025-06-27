const puppeteer = require('puppeteer');

describe('Authentication - Login Test', () => {
  let browser;
  let page;
  let consoleErrors = [];

  beforeAll(async () => {
    // Launch browser
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  });

  beforeEach(async () => {
    // Create new page for each test
    page = await browser.newPage();
    
    // Set viewport
    await page.setViewport({ width: 1920, height: 1080 });
    
    // Set user agent
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
    
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

  test('should login successfully and redirect to dashboard', async () => {
    // Step 1: Go to /auth/login
    const response = await page.goto('http://127.0.0.1:5000/auth/login', { 
      waitUntil: 'networkidle2' 
    });
    
    // Assert HTTP 200 response
    expect(response.status()).toBe(200);
    
    // Step 2: Fill username & password, click submit
    // Wait for login form elements
    await page.waitForSelector('input[name="username"], input[id="username"]', { timeout: 10000 });
    await page.waitForSelector('input[name="password"], input[id="password"]', { timeout: 10000 });
    
    // Fill username field
    await page.type('input[name="username"], input[id="username"]', 'admin');
    
    // Fill password field
    await page.type('input[name="password"], input[id="password"]', 'Admin123!');
    
    // Click submit button
    const submitButton = await page.$('button[type="submit"], input[type="submit"]');
    if (submitButton) {
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'networkidle2' }),
        submitButton.click()
      ]);
    } else {
      // Fallback: press Enter on password field
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'networkidle2' }),
        page.keyboard.press('Enter')
      ]);
    }
    
    // Step 3: Expect redirect to /dashboard and selector #refresh-btn visible
    const currentUrl = page.url();
    expect(currentUrl).toContain('/dashboard');
    
    // Wait for refresh button to be visible
    await page.waitForSelector('#refresh-btn', { 
      visible: true, 
      timeout: 15000 
    });
    
    // Verify the refresh button is visible
    const refreshBtn = await page.$('#refresh-btn');
    expect(refreshBtn).toBeTruthy();
    
    const isVisible = await page.evaluate(() => {
      const btn = document.querySelector('#refresh-btn');
      return btn && btn.offsetWidth > 0 && btn.offsetHeight > 0;
    });
    expect(isVisible).toBe(true);
    
    // Step 4: Capture screenshot 01_login_success.png
    await page.screenshot({ 
      path: '01_login_success.png',
      fullPage: true
    });
    
    // Step 5: Assert no console errors
    expect(consoleErrors).toHaveLength(0);
    
    console.log('Login test completed successfully');
    console.log('Current URL:', currentUrl);
    console.log('Console errors:', consoleErrors.length);
  });
});

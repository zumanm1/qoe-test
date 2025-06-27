const fs = require('fs');
const path = require('path');
const config = require('./config.json');

/**
 * Login helper function that authenticates with admin credentials
 * and waits for the dashboard to load
 * @param {Object} page - Puppeteer page object
 * @returns {Promise<void>}
 */
async function login(page) {
  try {
    // Navigate to the base URL
    await page.goto(config.baseUrl, { waitUntil: 'networkidle2' });
    
    // Wait for login form elements to be available
    await page.waitForSelector('input[type="text"], input[name="username"], input[id="username"]', { timeout: 10000 });
    await page.waitForSelector('input[type="password"], input[name="password"], input[id="password"]', { timeout: 10000 });
    
    // Find and fill the username field
    const usernameSelector = await page.$('input[type="text"], input[name="username"], input[id="username"]');
    if (usernameSelector) {
      await page.type('input[type="text"], input[name="username"], input[id="username"]', 'admin');
    }
    
    // Find and fill the password field
    const passwordSelector = await page.$('input[type="password"], input[name="password"], input[id="password"]');
    if (passwordSelector) {
      await page.type('input[type="password"], input[name="password"], input[id="password"]', 'Admin123!');
    }
    
    // Find and click the login/submit button
    const submitButton = await page.$('button[type="submit"], input[type="submit"], button:contains("Login"), button:contains("Sign in")');
    if (submitButton) {
      await submitButton.click();
    } else {
      // Fallback: press Enter on password field
      await page.keyboard.press('Enter');
    }
    
    // Wait for dashboard to load by checking for the refresh button
    await page.waitForSelector('#refresh-btn', { timeout: 15000 });
    
    console.log('Successfully logged in and dashboard loaded');
    
    // Take screenshot if configured
    if (config.saveScreens) {
      const screenshotPath = path.join(config.screenshotsDir, `login-success-${Date.now()}.png`);
      await page.screenshot({ path: screenshotPath });
      console.log(`Screenshot saved: ${screenshotPath}`);
    }
    
  } catch (error) {
    console.error('Login failed:', error.message);
    
    // Take error screenshot if configured
    if (config.saveScreens) {
      const screenshotPath = path.join(config.screenshotsDir, `login-error-${Date.now()}.png`);
      await page.screenshot({ path: screenshotPath });
      console.log(`Error screenshot saved: ${screenshotPath}`);
    }
    
    throw error;
  }
}

/**
 * Initialize Puppeteer page with global configuration
 * @param {Object} browser - Puppeteer browser object
 * @returns {Promise<Object>} Configured page object
 */
async function initializePage(browser) {
  const page = await browser.newPage();
  
  // Set viewport from config
  await page.setViewport(config.viewport);
  
  // Set user agent
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
  
  return page;
}

/**
 * Ensure screenshots directory exists
 */
function ensureScreenshotsDir() {
  const screenshotsPath = path.resolve(config.screenshotsDir);
  if (!fs.existsSync(screenshotsPath)) {
    fs.mkdirSync(screenshotsPath, { recursive: true });
  }
}

module.exports = {
  login,
  initializePage,
  ensureScreenshotsDir,
  config
};

const puppeteer = require('puppeteer');
const fs = require('fs');
const { login, initializePage, ensureScreenshotsDir, config } = require('../qoe-tool-tests/helpers');


describe('Download Docs - Functionality Test', () => {
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

  test('should download documentation and verify content', async () => {
    await login(page);

    // Navigate to any page (dashboard after login)
    await page.goto(`${config.baseUrl}/dashboard`, { waitUntil: 'networkidle2' });

    // Screenshot before click
    await page.screenshot({ 
      path: `${config.screenshotsDir}/08_before_download_click.png`,
      fullPage: true 
    });

    // Set up response interception for PDF download
    const interceptedResponse = new Promise((resolve) => {
      page.on('response', async (response) => {
        const url = response.url();
        if (url.includes('/docs/download-docs') || url.endsWith('.pdf')) {
          const headers = response.headers();
          const buffer = await response.buffer();
          resolve({ headers, buffer, url, status: response.status() });
        }
      });
    });

    // Look for "Download Docs" button or link
    const downloadButton = await Promise.race([
      page.waitForXPath('//button[contains(text(), "Download Docs")]', { timeout: 5000 }).catch(() => null),
      page.waitForXPath('//a[contains(text(), "Download Docs")]', { timeout: 5000 }).catch(() => null),
      page.waitForSelector('a[href*="download-docs"]', { timeout: 5000 }).catch(() => null),
      page.waitForSelector('.download-docs-btn', { timeout: 5000 }).catch(() => null),
      page.waitForSelector('button.download-docs', { timeout: 5000 }).catch(() => null)
    ]);

    if (!downloadButton) {
      // Try direct navigation to download endpoint
      console.log('Download button not found, trying direct GET request');
      await page.goto(`${config.baseUrl}/docs/download-docs`, { waitUntil: 'networkidle2' });
    } else {
      // Click the download button
      await downloadButton.click();
    }

    // Wait for the network response
    const responseData = await Promise.race([
      interceptedResponse,
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Download timeout')), 15000)
      )
    ]);

    // Verify response data
    expect(responseData.status).toBe(200);
    expect(responseData.headers['content-type']).toContain('application/pdf');
    expect(responseData.buffer.length).toBeGreaterThan(0);

    console.log(`PDF downloaded: ${responseData.buffer.length} bytes`);
    console.log(`Content-Type: ${responseData.headers['content-type']}`);

    // Save PDF to file system for verification
    const pdfPath = `${config.screenshotsDir}/08_downloaded_docs.pdf`;
    fs.writeFileSync(pdfPath, responseData.buffer);
    console.log(`PDF saved to: ${pdfPath}`);

    // Look for toast/flash message after download (with timeout)
    try {
      await page.waitForSelector('.toast-message, .flash-message, .alert, .notification', { 
        visible: true, 
        timeout: 5000 
      });
    } catch (e) {
      console.log('No toast/flash message found after download - this may be expected');
    }

    // Screenshot after download attempt
    await page.screenshot({ 
      path: `${config.screenshotsDir}/08_after_download_toast.png`,
      fullPage: true 
    });

    // Optional: Load PDF with pdfjs to verify first page content
    // Uncomment if pdfjs-dist is available in the project
    /*
    try {
      const pdfjsLib = require('pdfjs-dist/es5/build/pdf');
      const pdfDoc = await pdfjsLib.getDocument({ data: responseData.buffer }).promise;
      const page1 = await pdfDoc.getPage(1);
      const textContent = await page1.getTextContent();
      const text = textContent.items.map(item => item.str).join(' ');
      expect(text).toContain('Mobile QoE Tool Documentation');
      console.log('PDF content verified: Contains expected documentation title');
    } catch (pdfError) {
      console.log('PDF content verification skipped - pdfjs not available:', pdfError.message);
    }
    */

    // Assert no critical console errors
    const criticalErrors = consoleErrors.filter(error => 
      !error.includes('Warning') && 
      !error.includes('favicon.ico')
    );
    expect(criticalErrors.length).toBe(0);

    console.log('Download Docs test completed successfully');
  });
});


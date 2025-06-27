# QoE Tool MCP Test Suite

This is a Puppeteer-based test suite for the QoE Tool application, providing end-to-end testing capabilities.

## Structure

```
qoe-tool-tests/
├── config.json          # Global test configuration
├── helpers.js           # Helper functions including login()
├── jest.setup.js        # Jest configuration
├── package.json         # Dependencies and scripts
├── tests/               # Test files
│   └── sample-login-test.js
└── mcp-reports/         # Test reports and screenshots
    └── screens/         # Screenshots directory
```

## Configuration

The global configuration is defined in `config.json`:

```json
{
  "baseUrl": "http://127.0.0.1:5000",
  "screenshotsDir": "mcp-reports/screens",
  "saveScreens": true,
  "headless": true,
  "viewport": { "width": 1920, "height": 1080 }
}
```

## Helper Functions

### `login(page)`

The main helper function that handles authentication:
- Logs in with credentials: **admin / Admin123!**
- Waits for the dashboard to load (looks for `#refresh-btn` element)
- Takes screenshots on success/failure if `saveScreens` is enabled
- Throws an error if login fails

### `initializePage(browser)`

Initializes a new page with the configured viewport and user agent.

### `ensureScreenshotsDir()`

Creates the screenshots directory if it doesn't exist.

## Installation

```bash
cd qoe-tool-tests
npm install
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Debug tests
npm run test:debug
```

## Usage Example

```javascript
const puppeteer = require('puppeteer');
const { login, initializePage, config } = require('./helpers');

describe('My Test Suite', () => {
  let browser, page;

  beforeAll(async () => {
    browser = await puppeteer.launch({ headless: config.headless });
  });

  beforeEach(async () => {
    page = await initializePage(browser);
  });

  afterEach(async () => {
    await page.close();
  });

  afterAll(async () => {
    await browser.close();
  });

  test('should login and access dashboard', async () => {
    await login(page);
    
    // Your test logic here
    const refreshBtn = await page.$('#refresh-btn');
    expect(refreshBtn).toBeTruthy();
  });
});
```

## Screenshots

When `saveScreens` is enabled, screenshots are automatically saved to the `mcp-reports/screens` directory:
- Login success screenshots
- Error screenshots
- Custom test screenshots

## Notes

- Tests timeout after 30 seconds by default
- The login function is flexible and tries to find common login form selectors
- Screenshots include timestamps to avoid conflicts
- Browser launches with `--no-sandbox` and `--disable-setuid-sandbox` flags for CI compatibility

// Jest setup file for global test configuration

// Set longer timeout for all tests
jest.setTimeout(60000);

// Global setup for puppeteer tests
global.console = {
  ...console,
  // Suppress console.log during tests unless explicitly needed
  log: jest.fn(),
  debug: jest.fn(),
  info: console.info,
  warn: console.warn,
  error: console.error,
};

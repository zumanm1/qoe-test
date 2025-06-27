// Jest setup file for additional test configuration
const { config } = require('./helpers');

// Set test timeout to accommodate slow operations
jest.setTimeout(30000);

// Global test configuration
global.testConfig = config;

// Optional: Add custom matchers or global setup here
beforeAll(async () => {
  console.log('Starting test suite with configuration:', JSON.stringify(config, null, 2));
});

afterAll(async () => {
  console.log('Test suite completed');
});

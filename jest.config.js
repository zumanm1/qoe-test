module.exports = {
  testEnvironment: 'node',
  testTimeout: 60000, // 60 seconds timeout for E2E tests
  verbose: true,
  testMatch: [
    '**/tests/**/*.test.js'
  ],
  collectCoverage: false,
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js']
};

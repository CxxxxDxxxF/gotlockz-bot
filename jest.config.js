export default {
  // Use ts-jest for TypeScript files
  preset: 'ts-jest',
  // Our code and tests run in Node
  testEnvironment: 'node',
  // Recognize these extensions
  moduleFileExtensions: ['ts', 'js', 'json'],
  // Transform TS via ts-jest
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', { useESM: true }],
  },
  // Treat .ts as ESM modules
  extensionsToTreatAsEsm: ['.ts'],
  // Allow absolute imports from src/
  moduleNameMapper: {
    '^src/(.*)$': '<rootDir>/src/$1',
  },
  globals: {
    'ts-jest': {
      // Tell ts-jest we're targeting ESM
      tsconfig: '<rootDir>/tsconfig.json',
      useESM: true,
    },
  },
}; 
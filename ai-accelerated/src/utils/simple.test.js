// Simple test to verify Jest is working
describe('Simple Test', () => {
  test('should pass basic test', () => {
    expect(1 + 1).toBe(2);
  });

  test('should handle strings', () => {
    expect('hello').toBe('hello');
  });

  test('should handle arrays', () => {
    expect([1, 2, 3]).toHaveLength(3);
  });
}); 
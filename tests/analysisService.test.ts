import { generateAnalysis } from '../src/services/analysisService';

// Mock environment variables
process.env['DISCORD_BOT_TOKEN'] = 'test-token';
process.env['OPENAI_API_KEY'] = 'test-openai-key';

jest.mock('openai', () => {
  return {
    __esModule: true,
    default: function () {
      return {
        chat: {
          completions: {
            create: jest.fn().mockResolvedValue({
              choices: [{ message: { content: 'Test analysis.' } }]
            })
          }
        }
      };
    }
  };
});

describe('Analysis Service', () => {
  it('returns analysis text', async () => {
    const text = await generateAnalysis({ foo: 'bar' }, { baz: 'qux' }, 12.34, { temp: 72 });
    expect(text).toBe('Test analysis.');
  });
}); 
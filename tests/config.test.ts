import Ajv from 'ajv';
import commandsConfig from '../src/config/commands.json';

describe('commands.json schema', () => {
  const schema = {
    type: 'array',
    items: {
      type: 'object',
      required: ['name', 'description', 'options'],
      properties: {
        name: { type: 'string' },
        description: { type: 'string' },
        options: {
          type: 'array',
          items: {
            type: 'object',
            required: ['name', 'type', 'required'],
            properties: {
              name: { type: 'string' },
              type: { type: 'string' },
              required: { type: 'boolean' },
            },
          },
        },
      },
    },
  };

  it('should match the schema', () => {
    const ajv = new Ajv();
    const valid = ajv.validate(schema, commandsConfig.commands);
    if (!valid) {
      // eslint-disable-next-line no-console
      console.error(ajv.errors);
    }
    expect(valid).toBe(true);
  });
}); 
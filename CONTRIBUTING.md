# Contributing to GotLockz Bot

Thank you for your interest in contributing to GotLockz Bot! 🚀

## 🤝 How to Contribute

### Types of Contributions

We welcome contributions of all kinds:

- 🐛 **Bug Reports**: Help us identify and fix issues
- ✨ **Feature Requests**: Suggest new features and improvements
- 📝 **Documentation**: Improve guides, READMEs, and comments
- 🔧 **Code**: Fix bugs, add features, improve performance
- 🧪 **Testing**: Write tests, improve test coverage
- 🎨 **UI/UX**: Improve user experience and interface
- 🔒 **Security**: Report vulnerabilities and security improvements

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Git
- Discord Bot Token (for testing)

### Setup Development Environment

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/gotlockz-bot.git
   cd gotlockz-bot/ai-accelerated
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment**
   ```bash
   cp env.example .env
   # Edit .env with your Discord bot credentials
   ```

4. **Test setup**
   ```bash
   npm run setup
   npm run status
   ```

5. **Start development**
   ```bash
   npm run dev
   ```

## 📋 Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/amazing-feature
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Follow the [coding standards](#coding-standards)
- Write tests for new functionality
- Update documentation as needed
- Test your changes thoroughly

### 3. Test Your Changes

```bash
# Run all tests
npm test

# Run linting
npm run lint

# Check deployment status
npm run status

# Test health endpoint
npm run health
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add amazing feature"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/amazing-feature
```

Then create a pull request using the [PR template](.github/pull_request_template.md).

## 🎯 Coding Standards

### JavaScript/ES6

- Use ES6 modules (`import`/`export`)
- Prefer `const` and `let` over `var`
- Use async/await over Promises
- Use template literals for string interpolation
- Use destructuring for cleaner code

### Error Handling

```javascript
try {
  const result = await riskyOperation();
  return { success: true, data: result };
} catch (error) {
  logger.error('Operation failed:', {
    error: error.message,
    stack: error.stack,
    context: 'additional info'
  });
  return { success: false, error: error.message };
}
```

### Discord.js v14 Patterns

```javascript
import { SlashCommandBuilder } from 'discord.js';
import { logger } from '../utils/logger.js';

export const data = new SlashCommandBuilder()
  .setName('command')
  .setDescription('Description');

export async function execute(interaction) {
  try {
    await interaction.deferReply();
    // Command logic here
    await interaction.editReply('Response');
  } catch (error) {
    logger.error('Command failed:', error);
    await interaction.editReply('Error message');
  }
}
```

### File Organization

- **Commands**: `src/commands/`
- **Services**: `src/services/`
- **Utilities**: `src/utils/`
- **Configuration**: `src/config/`
- **Tests**: `tests/`

### Naming Conventions

- **Variables/Functions**: camelCase
- **Classes**: PascalCase
- **Files**: kebab-case
- **Constants**: UPPER_SNAKE_CASE

## 🧪 Testing

### Writing Tests

```javascript
// tests/services/ocrService.test.js
import { describe, it, expect, beforeEach } from '@jest/globals';
import { analyzeImage } from '../../src/services/ocrService.js';

describe('OCRService', () => {
  it('should analyze image successfully', async () => {
    const result = await analyzeImage('test-image-url');
    expect(result.success).toBe(true);
    expect(result.data).toBeDefined();
  });

  it('should handle errors gracefully', async () => {
    const result = await analyzeImage('invalid-url');
    expect(result.success).toBe(false);
    expect(result.error).toBeDefined();
  });
});
```

### Running Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- tests/services/ocrService.test.js

# Run tests in watch mode
npm test -- --watch
```

## 📝 Documentation

### Code Documentation

- Add JSDoc comments for all public functions
- Include parameter types and return values
- Document complex business logic
- Keep README files updated

```javascript
/**
 * Analyzes an image using OCR to extract text
 * @param {string} imageUrl - URL of the image to analyze
 * @param {boolean} debug - Enable debug mode for detailed output
 * @returns {Promise<Object>} Analysis result with success status and data
 */
async function analyzeImage(imageUrl, debug = false) {
  // Implementation
}
```

### README Updates

When adding new features:
- Update the main README.md
- Add examples and usage instructions
- Include any new environment variables
- Update the features list

## 🔒 Security

### Security Guidelines

- Never log sensitive data (tokens, API keys)
- Validate all user inputs
- Use environment variables for secrets
- Follow the principle of least privilege
- Report security issues privately

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Email [security@gotlockz.com](mailto:security@gotlockz.com) with:
- Detailed description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## 🚀 Pull Request Process

### Before Submitting

1. **Test thoroughly**
   - Run all tests: `npm test`
   - Test manually with Discord bot
   - Check for linting errors: `npm run lint`

2. **Update documentation**
   - Update README if needed
   - Add JSDoc comments
   - Update any relevant guides

3. **Follow the template**
   - Use the [PR template](.github/pull_request_template.md)
   - Fill out all sections
   - Include screenshots if relevant

### Review Process

1. **Automated checks** must pass
   - Tests
   - Linting
   - Security audit
   - Build verification

2. **Code review** by maintainers
   - Code quality
   - Security considerations
   - Performance impact
   - Documentation quality

3. **Final approval** and merge

## 🏆 Recognition

### Contributors

All contributors will be:
- Listed in the [CONTRIBUTORS.md](CONTRIBUTORS.md) file
- Mentioned in release notes
- Given credit in the project documentation

### Special Recognition

- **Bug Hunters**: Find and report critical bugs
- **Feature Creators**: Implement major new features
- **Documentation Heroes**: Significantly improve docs
- **Security Researchers**: Report security vulnerabilities

## 📞 Getting Help

### Questions?

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For general questions
- **Discord Server**: For real-time help
- **Email**: [support@gotlockz.com](mailto:support@gotlockz.com)

### Resources

- [Discord.js Documentation](https://discord.js.org/)
- [Node.js Documentation](https://nodejs.org/docs/)
- [Jest Testing Framework](https://jestjs.io/)
- [ESLint Rules](https://eslint.org/docs/rules/)

## 🎯 Contribution Ideas

### High Priority

- [ ] Add more AI models for analysis
- [ ] Improve OCR accuracy
- [ ] Add caching layer
- [ ] Implement user preferences
- [ ] Add analytics dashboard

### Medium Priority

- [ ] Add more betting analysis features
- [ ] Improve error messages
- [ ] Add internationalization
- [ ] Create mobile app
- [ ] Add web dashboard

### Low Priority

- [ ] Add themes/customization
- [ ] Create browser extension
- [ ] Add social features
- [ ] Create API for third-party integrations

---

**Thank you for contributing to GotLockz Bot! 🚀**

Your contributions help make this project better for everyone in the betting community. 
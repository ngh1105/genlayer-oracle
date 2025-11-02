# Contributing to GenLayer Oracle

Thank you for your interest in contributing to GenLayer Oracle! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Documentation](#documentation)

## 🤝 Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

## 🚀 Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/ngh1105/genlayer-oracle.git
   cd genlayer-oracle
   ```

2. **Install dependencies**
   ```bash
   # Root dependencies
   npm install
   
   # Oracle SDK
   cd packages/oracle-sdk
   npm install
   
   # Frontend
   cd ../frontend
   npm install
   ```

3. **Set up development environment**
   - Ensure Node.js 18+ is installed
   - Python 3.9+ for GenVM contracts
   - GenLayer Studio access for contract deployment

## 💡 How to Contribute

### Reporting Bugs

1. Check if the issue already exists in [GitHub Issues](https://github.com/ngh1105/genlayer-oracle/issues)
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Node version, etc.)
   - Screenshots if applicable

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and its use case
3. Explain why it would be valuable
4. Consider implementation approach if possible

### Contributing Code

1. **Pick an issue** or create a new one
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following code standards
4. **Test your changes**
5. **Submit a Pull Request**

## 🔄 Development Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Messages

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Test additions
- `chore`: Maintenance tasks

**Examples**:
```
feat(web-fetcher): Add stock price pattern
fix(oracle-sdk): Fix type imports
docs(api-keys): Update security best practices
```

## 📝 Code Standards

### Python (GenVM Contracts)

- Follow PEP 8 style guide
- Use type hints where applicable
- Document all public methods with docstrings
- Ensure state persistence (type annotations in class body)

**Example**:
```python
class MyContract(gl.Contract):
    # CRITICAL: Declare persistent fields in class body
    last_value: float
    
    def __init__(self):
        self.last_value = 0.0
    
    @gl.public.view
    def get_value(self) -> dict:
        """Get current stored value.
        
        Returns:
            dict: Value data
        """
        return {"value": str(self.last_value)}
```

### TypeScript/JavaScript

- Follow ESLint configuration
- Use TypeScript for type safety
- Document exported functions with JSDoc
- Prefer async/await over promises

**Example**:
```typescript
/**
 * Get price from oracle contract.
 * 
 * @param symbol - Cryptocurrency symbol (e.g., 'ETH')
 * @returns Promise resolving to price data
 */
async getPrice(symbol: string): Promise<number> {
  // Implementation
}
```

### General Guidelines

- **Keep functions focused**: One responsibility per function
- **Write clear names**: Variables and functions should be self-documenting
- **Add comments**: Explain "why", not "what"
- **Keep it simple**: Prefer clarity over cleverness

## 🧪 Testing

### Contract Testing

1. Test on GenLayer Studio (`studionet`)
2. Verify state persistence
3. Test error handling
4. Validate consensus behavior

**Example Test Checklist**:
- [ ] Contract deploys successfully
- [ ] State persists across transactions
- [ ] Error handling works correctly
- [ ] Consensus validation functions

### SDK Testing

```bash
cd packages/oracle-sdk
npm test
```

### Frontend Testing

```bash
cd frontend
npm test
```

## 📤 Submitting Changes

### Pull Request Process

1. **Update documentation** if needed
2. **Add/update tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** with your changes
5. **Create Pull Request** with:
   - Clear title and description
   - Reference related issues
   - Screenshots for UI changes
   - Checklist of changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
- [ ] Tests pass locally
- [ ] Contract tested on studionet
- [ ] Manual testing completed

## Related Issues
Fixes #issue-number

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Tests added/updated
```

## 📚 Documentation

### When to Update Documentation

- New features or patterns
- API changes
- Configuration changes
- Breaking changes

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add diagrams for complex concepts
- Keep README files up to date

### Documentation Locations

- `README.md` - Project overview
- `docs/` - Detailed documentation
- Code comments - Inline documentation
- `CHANGELOG.md` - Version history

## 🎯 Project Structure

```
genlayer-oracle/
├── contracts/          # GenVM Python contracts
├── packages/
│   ├── genvm-web-fetcher/  # Web fetcher library
│   └── oracle-sdk/         # TypeScript SDK
├── frontend/           # React frontend
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

## 🔍 Review Process

1. Maintainers review PRs within 48 hours
2. Address review comments promptly
3. CI checks must pass before merge
4. At least one approval required

## ❓ Questions?

- Open a [Discussion](https://github.com/ngh1105/genlayer-oracle/discussions)
- Check existing [Issues](https://github.com/ngh1105/genlayer-oracle/issues)
- Read project [Documentation](docs/)

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!


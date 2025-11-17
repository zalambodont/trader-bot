# Contributing to Crypto Trading Bot

First off, thank you for considering contributing to this project! It's people like you that make this bot better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior by opening an issue.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**
```
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g., macOS, Windows, Linux]
 - Python version: [e.g., 3.10]
 - Node.js version: [e.g., 18.0]
 - Trading mode: [Paper or Live]

**Logs**
Paste relevant error logs here.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description** of the enhancement
- **Use case**: Why is this enhancement useful?
- **Possible implementation**: If you have ideas on how to implement it

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Follow the code style** of the project (PEP 8 for Python, ESLint for JavaScript)
3. **Add tests** if you're adding functionality
4. **Update documentation** (README, QUICKSTART, code comments)
5. **Test thoroughly** in both paper and live modes (if applicable)
6. **Write a clear commit message** following the format below

#### Commit Message Format

We use conventional commits:

```
type(scope): subject

body (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(scanner): add volume filter to market scanner
fix(risk): correct stop loss calculation for short positions
docs(readme): update installation instructions for Windows
```

### Development Setup

1. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/crypto-trading-bot.git
   cd crypto-trading-bot
   ```

2. **Set up Python environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up React frontend:**
   ```bash
   cd frontend
   npm install
   ```

4. **Create .env file:**
   ```bash
   cp .env.example .env
   # Leave blank for paper trading
   ```

5. **Run tests** (before submitting PR):
   ```bash
   # Backend tests
   pytest

   # Frontend tests
   cd frontend
   npm test
   ```

### Code Style Guidelines

**Python:**
- Follow PEP 8
- Use type hints where applicable
- Add docstrings to functions and classes
- Keep functions focused and small
- Use meaningful variable names

**JavaScript/React:**
- Use functional components with hooks
- Follow ESLint rules
- Use meaningful component and variable names
- Keep components focused and reusable

**General:**
- Comment complex logic
- Avoid hardcoded values (use constants)
- Handle errors gracefully
- Think about security (especially for trading operations)

### Testing Guidelines

**Before submitting a PR, test:**

1. **Paper Trading Mode** - Ensure it works without API keys
2. **Error Handling** - Test with invalid inputs
3. **UI Responsiveness** - Check on different screen sizes
4. **Cross-browser** - Test on Chrome, Firefox, Safari
5. **Different Scenarios** - Test edge cases

**Critical: For trading logic changes:**
- Test extensively in paper mode
- Verify risk calculations
- Check position sizing
- Validate stop loss/take profit logic

### Security Considerations

**NEVER commit:**
- API keys or secrets
- Real wallet addresses
- Personal information
- Production credentials

**When working on security-related code:**
- Validate all user inputs
- Sanitize data before API calls
- Be cautious with eval() or exec()
- Follow principle of least privilege

## Project Structure

```
.
├── backend/
│   ├── binance_client.py      # Binance API wrapper
│   ├── strategies.py           # Trading strategies
│   ├── market_scanner.py       # Market scanning logic
│   ├── multi_pair_bot.py       # Multi-pair trading bot
│   └── risk_management.py      # Risk management
├── frontend/
│   └── src/
│       ├── components/         # React components
│       ├── App.js             # Main app
│       └── App.css            # Styles
├── docs/                       # Additional documentation
├── tests/                      # Test files
└── README.md                  # Main documentation
```

## Financial Responsibility

**This is a trading bot that handles real money. Contributors must:**
- Test thoroughly before submitting changes
- Consider edge cases that could cause financial loss
- Document risks in code comments
- Be conservative with default values
- Validate all trading logic extensively

## Need Help?

- Check the [QUICKSTART.md](QUICKSTART.md) for setup help
- Read the [README.md](README.md) for technical documentation
- Open an issue for questions
- Join discussions in existing issues

## Recognition

Contributors who make significant contributions will be recognized in:
- The README.md contributors section
- Release notes for their contributions

Thank you for making this project better!

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete open-source project setup
- MIT License
- Contributing guidelines
- Code of Conduct
- Security policy
- This changelog

### Changed
- Simplified .env configuration to API keys only
- All trading settings now configured through dashboard
- Updated documentation for consistency across README, QUICKSTART, and .env.example

### Fixed
- Removed unused imports from ActivePositions.js
- Fixed React Hook dependency warnings

## [0.2.0] - 2025-11-17

### Added
- Multi-pair trading support
- Market scanner with technical analysis
- Pair search functionality with autocomplete
- OpenAI GPT-4 integration for AI trading advisor
- Real-time portfolio tracking
- Active positions dashboard with live charts
- Trading settings configuration modal
- Paper trading mode (no API keys required)
- Portfolio statistics and P&L tracking
- Emoji-based backend logging
- WebSocket support for real-time updates

### Changed
- Moved from single-pair to multi-pair trading bot
- Separated search functionality into dedicated PairSearch component
- All trading configuration moved to dashboard
- Removed hardcoded trading parameters from .env

### Security
- API keys made optional for paper trading
- Improved .gitignore to prevent credential leaks
- Added security warnings in documentation

## [0.1.0] - 2025-11-16

### Added
- Initial project setup
- Basic trading bot with RSI and MACD strategies
- React dashboard
- Binance API integration
- Risk management system
- Backtesting engine
- Paper trading mode
- Basic README and setup instructions

---

## Version History Guidelines

### Types of Changes
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` in case of vulnerabilities

### Version Numbering
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality (backward compatible)
- **PATCH** version for backward compatible bug fixes

### Release Notes Template

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- Feature description

### Changed
- Change description

### Deprecated
- Deprecation notice

### Removed
- Removal notice

### Fixed
- Bug fix description

### Security
- Security fix description
```

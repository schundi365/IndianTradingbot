# Contributing to MT5 Trading Bot

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Python version, MT5 version, OS)
- Relevant log files

### Suggesting Features

Feature requests are welcome! Please:
- Check if the feature already exists
- Explain the use case
- Describe the expected behavior
- Consider backward compatibility

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add comments for complex logic
- Include docstrings for functions
- Keep functions focused and small

### Testing

- Test on demo account first
- Verify all existing features still work
- Add test cases for new features
- Document any new configuration options

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/mt5-trading-bot.git
cd mt5-trading-bot

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_connection.py
```

## Project Structure

```
mt5-trading-bot/
├── src/                    # Core bot code
│   ├── mt5_trading_bot.py
│   ├── config.py
│   ├── adaptive_risk_manager.py
│   ├── split_order_calculator.py
│   └── trailing_strategies.py
├── docs/                   # Documentation
├── examples/               # Example scripts
├── run_bot.py             # Main entry point
└── test_connection.py     # Connection test
```

## Questions?

Feel free to open an issue for any questions or clarifications.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

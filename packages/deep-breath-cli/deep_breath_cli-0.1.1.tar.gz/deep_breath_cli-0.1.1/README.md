# Deep Breath CLI

**Deep Breath CLI** is a command-line tool designed to help you relax, regain focus, and boost your energy—right from your terminal.

## 🌬️ What is Deep Breath CLI?

Whether you're coding, studying, or just need a quick break, Deep Breath CLI offers guided breathing exercises with visual progress bars and calming colors. With simple commands, you can access different breathing patterns to help you reset and recharge.

## 🚀 Features

- Multiple breathing patterns (4-7-8, Box breathing)
- Visual progress bars with calming colors
- Customizable session lengths and cycles
- Clear, distraction-free interface
- Easy preset management

## 🛠️ Installation

Install from PyPI:

```bash
pip install deep-breath-cli
```

## ⚡️ Usage

### Start a breathing session

```bash
# Default session (4 cycles of 4-7-8 pattern)
breath start

# Custom number of cycles
breath start --cycle 8

# Different breathing pattern
breath start --pattern "4-4-4-4"

# Combined options
breath start --cycle 6 --pattern "4-4-4-4"
```

### View available patterns

```bash
breath presets
```

Output:

```plaintext
Available breathing patterns:
  4-7-8: 4s Breathe in..., 7s Hold..., 8s Breathe out...
  4-4-4-4: 4s Breathe in..., 4s Hold..., 4s Breathe out..., 4s Hold...

You can use these patterns with the --pattern option.
```

### Get help

```bash
breath --help
breath start --help
```

## 🌟 Breathing Patterns

- **4-7-8**: Relaxation pattern (inhale 4s, hold 7s, exhale 8s)
- **4-4-4-4**: Box breathing for focus (inhale 4s, hold 4s, exhale 4s, hold 4s)
- **More to come**

## 🤔 Why use Deep Breath CLI?

- **Quick:** Take a break without leaving your terminal
- **Effective:** Scientifically-backed breathing techniques
- **Customizable:** Choose the pattern and duration that fits your needs
- **Distraction-free:** Clear your mind with simple, focused interface

## 🛠️ Development

### Setup

```bash
git clone https://github.com/weart99/deep-breath-cli
cd deep-breath-cli
uv sync --extra dev
```

### Running tests

```bash
uv run pytest tests/ --cov=src
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

## 📄 License

[MIT Licence](https://choosealicense.com/licenses/mit/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

## Authors

[@weart99](https://www.github.com/weart99)

---

Take a deep breath, and let's get started! 🌬️

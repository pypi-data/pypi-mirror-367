<div align="center">
  <br/>
  <!-- <img src=".github/assets/logo.png" alt="logo" width="200" height="auto" /> -->
  <h1>Python Code Validator</h1>
  <p>
    <b>A flexible, AST-based framework for static validation of Python code using declarative JSON rules.</b>
  </p>
  <br/>

  <!-- Badges -->
  <p>
    <a href="https://github.com/Qu1nel/PythonCodeValidator/stargazers"><img src="https://img.shields.io/github/stars/Qu1nel/PythonCodeValidator" alt="GitHub Stars"></a>
    <a href="https://github.com/Qu1nel/PythonCodeValidator/network/members"><img src="https://img.shields.io/github/forks/Qu1nel/PythonCodeValidator" alt="GitHub Forks"></a>
    <a href="https://github.com/Qu1nel/PythonCodeValidator/graphs/contributors"><img src="https://img.shields.io/github/contributors/Qu1nel/PythonCodeValidator" alt="Contributors"></a>
    <a href="https://github.com/Qu1nel/PythonCodeValidator/issues/"><img src="https://img.shields.io/github/issues/Qu1nel/PythonCodeValidator" alt="Open Issues"></a>
    <a href="https://github.com/Qu1nel/PythonCodeValidator/commits/main"><img src="https://img.shields.io/github/last-commit/Qu1nel/PythonCodeValidator" alt="Last Commit"></a>
  </p>
  <p>
    <a href="https://github.com/Qu1nel/PythonCodeValidator/actions/workflows/ci.yml"><img src="https://github.com/Qu1nel/PythonCodeValidator/actions/workflows/ci.yml/badge.svg" alt="CI Status"></a>
    <a href="https://app.codecov.io/gh/Qu1nel/PythonCodeValidator"><img src="https://codecov.io/gh/Qu1nel/PythonCodeValidator/graph/badge.svg" alt="Coverage"></a>
    <a href="https://pypi.org/project/python-code-validator/"><img src="https://img.shields.io/pypi/v/python-code-validator.svg" alt="PyPI Version"></a>
    <a href="https://pypi.org/project/python-code-validator/"><img src="https://img.shields.io/pypi/pyversions/python-code-validator.svg" alt="Python Versions"></a>
    <a href="https://github.com/Qu1nel/PythonCodeValidator/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Qu1nel/PythonCodeValidator" alt="License"></a>
  </p>

  <h4>
    <a href="#-quick-usage-example">Usage Examples</a>
    <span>·</span>
    <a href="https://pythoncodevalidator.readthedocs.io/en/latest/">Full Documentation</a>
    <span>·</span>
    <a href="https://deepwiki.com/Qu1nel/PythonCodeValidator">AI documentation</a>
    <span>·</span>
    <a href="https://github.com/Qu1nel/PythonCodeValidator/blob/main/docs/how_it_works/index.md">Developer's Guide</a>
    <span>·</span>
    <a href="https://github.com/Qu1nel/PythonCodeValidator/issues/new?template=1-bug-report.md">Report a Bug</a>
    <span>·</span>
    <a href="https://github.com/Qu1nel/PythonCodeValidator/issues/new?template=4-feature-request.md">Request Feature</a>
  </h4>
</div>

<br/>

---

## Table of Contents

- [About The Project](#-about-the-project)
- [The Power of Combinatorics](#-the-power-of-combinatorics)
- [Key Features](#-key-features)
- [Getting Started](#-getting-started)
    - [Installation](#installation)
- [Usage Examples](#-quick-usage-example)
    - [Example 1: Simple Check](#example-1-simple-check)
    - [Example 2: Advanced Check](#example-2-advanced-check)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#Contact)

## 📖 About The Project

**Python Code Validator** is an engine designed for educational platforms and automated testing systems. It solves a key
problem: **how to verify that a student's code meets specific structural and stylistic requirements *before* running
resource-intensive dynamic tests.**

Instead of writing complex Python scripts for each new validation rule, you can define them declaratively in a simple,
powerful **JSON format**. This allows teachers and curriculum developers to easily create and adapt validation scenarios
without deep programming knowledge. The framework analyzes the code's Abstract Syntax Tree (AST), providing a deep and
reliable way to enforce best practices.

## 📈 The Power of Combinatorics

The framework's power lies in its combinatorial architecture. It is built on a small set of primitive "bricks":
**Selectors** ($S$) that define *what* to find in the code, and **Constraints** ($C$) that define *what condition* to
check.

The number of unique validation rules ($R$) is not a sum, but a product of these components. A single rule can be
represented as:

$$R_{\text{single}} = S \times C$$

With approximately $10$ types of selectors and $10$ types of constraints, this already provides ~$100$ unique checks.
However,
the true flexibility comes from logical composition, allowing for a near-infinite number of validation scenarios:

$$R_{\text{total}} \approx S \times \sum_{k=1}^{|C|} \binom{|C|}{k} = S \times (2^{|C|} - 1)$$

This design provides **thousands of potential validation scenarios** out-of-the-box, offering extreme flexibility with
minimal complexity.

## ✨ Key Features

- **Declarative JSON Rules**: Define validation logic in a human-readable format.
- **Powerful Static Analysis**:
    - ✅ Check syntax and PEP8 compliance (`flake8`).
    - ✅ Enforce or forbid specific `import` statements.
    - ✅ Verify class structure, inheritance, and function signatures.
    - ✅ Forbid "magic numbers" or specific function calls like `eval`.
- **Precise Scoping**: Apply rules globally, or narrowly to a specific function, class, or method.
- **Extensible Architecture**: Easily add new, custom checks by creating new Selector or Constraint components.

## 🚀 Getting Started

### Installation

**1. For Users (from PyPI):**

Install the package with one command. This will make the `validate-code` command-line tool available.

```bash
pip install python-code-validator
```

**2. For Users (from source):**

If you want to install directly from the repository:

```bash
git clone https://github.com/Qu1nel/PythonCodeValidator.git
cd PythonCodeValidator
pip install .
```

**3. For Developers:**

To set up a full development environment, see the [Contributing Guidelines](./CONTRIBUTING.md).

## ⚡ Quick Usage Example

The validator is a command-line tool named `validate-code`.

### Example 1: Simple Check

Let's check if a required function exists.

**`solution_simple.py`:**

```python
# This file is missing the 'solve' function
def main():
    print("Hello")
```

**`rules_simple.json`:**

```json
{
  "validation_rules": [
    {
      "rule_id": 1,
      "message": "Required function 'solve' is missing.",
      "check": {
        "selector": {
          "type": "function_def",
          "name": "solve"
        },
        "constraint": {
          "type": "is_required"
        }
      }
    }
  ]
}
```

**Running the validator:**

```bash
$ validate-code solution_simple.py rules_simple.json
Starting validation for: solution_simple.py
Required function 'solve' is missing.
Validation failed.
```

### Example 2: Advanced Check

Let's enforce a complex rule: "In our game class, the `update` method must not contain any `print` statements."

**`game.py`:**

```python
import arcade


class MyGame(arcade.Window):
    def update(self, delta_time):
        print("Debugging player position...")  # Forbidden call
        self.player.x += 1
```

**`rules_advanced.json`:**

```json
{
  "validation_rules": [
    {
      "rule_id": 101,
      "message": "Do not use 'print' inside the 'update' method.",
      "check": {
        "selector": {
          "type": "function_call",
          "name": "print",
          "in_scope": {
            "class": "MyGame",
            "method": "update"
          }
        },
        "constraint": {
          "type": "is_forbidden"
        }
      }
    }
  ]
}
```

**Running the validator:**

```bash
$ validate-code game.py rules_advanced.json
Starting validation for: game.py
Do not use 'print' inside the 'update' method.
Validation failed.
```

## 📚 Documentation

- **Full User Guide & JSON Specification**: Our complete documentation is hosted on
  **[Read the Docs](https://[your-project].readthedocs.io)**.
- **Developer's Guide**: For a deep dive into the architecture, see the
  **[How It Works guide](./docs/how_it_works/index.md)**.
- **Interactive AI-Powered Docs**: **[DeepWiki](https://deepwiki.com/Qu1nel/PythonCodeValidator)**.

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn, inspire, and create. Any contributions you make
are **greatly appreciated**.

Please read our **[Contributing Guidelines](./CONTRIBUTING.md)** to get started. This project adheres to the
**[Code of Conduct](./CODE_OF_CONDUCT.md)**.

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

### Contact

Developed by **[Ivan Kovach (@Qu1nel)](https://github.com/Qu1nel)**.

Email: **[covach.qn@gmail.com](mailto:covach.qn@gmail.com)** Telegram: **[@qnllnq](https://t.me/qnllnq)**

<br/>

<p align="right"><a href="./LICENSE">MIT</a> © <a href="https://github.com/Qu1nel/">Ivan Kovach</a></p>

"""Enables running the validator as a package.

This file allows the package to be executed directly from the command line
using the ``-m`` flag with Python (e.g., ``python -m code_validator``). It
serves as the primary entry point that finds and invokes the command-line
interface logic defined in the `cli` module.

Example:
    You can run the validator package like this from the project root:

    .. code-block:: bash

        python -m code_validator path/to/solution.py path/to/rules.json

"""

from .cli import run_from_cli

if __name__ == "__main__":
    run_from_cli()

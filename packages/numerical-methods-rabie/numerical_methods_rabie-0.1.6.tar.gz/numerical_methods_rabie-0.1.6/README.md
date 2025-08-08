# numerical_methods_rabie

A Python package for solving numerical analysis problems, including root-finding, interpolation, integration, and solving systems of equations.

## Installation

To install the package from PyPI:

```bash
pip install numerical-methods-rabie
```

## Documentation

Full documentation is available on [Read the Docs](https://numerical-methods-project-rabie.readthedocs.io/en/latest/).

The documentation is generated using **Sphinx** and hosted automatically via **Read the Docs**.

To build the documentation locally:

```bash
cd docs
sphinx-apidoc -o source ../numerical_methods_rabie
make html
```

## Features

- Root-finding methods (e.g., bisection, Newton-Raphson)
- Interpolation (e.g., Lagrange, Newton)
- Numerical integration (e.g., trapezoidal rule, Simpson's rule)
- Solving systems of linear equations

## Project Structure

```
numerical_methods_rabie/
├── numerical_methods/
│   ├── __init__.py
│   ├── roots.py
│   ├── interpolation.py
│   ├── integration.py
│   └── systems.py
├── docs/
│   ├── source/
│   └── build/
├── tests/
├── setup.py
└── README.md
```

## License

This project is licensed under the MIT License.

## Author

Rabie Oudghiri
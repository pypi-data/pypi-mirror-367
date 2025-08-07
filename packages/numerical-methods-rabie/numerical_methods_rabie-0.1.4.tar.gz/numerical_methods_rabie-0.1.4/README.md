# numerical-methods-rabie

A Python package for implementing classical **numerical methods**, including:
- Root-finding methods (Dichotomy, Newton, Fixed Point)
- [Coming soon] Integration, Interpolation, Systems resolution

📦 Published on PyPI: [numerical-methods-rabie](https://pypi.org/project/numerical-methods-rabie/)

---

## 📥 Installation

It's recommended to use a virtual environment:

```bash
# Create and activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate     # Or: venv\Scripts\activate on Windows

# Install the package
pip install numerical-methods-rabie
🚀 Usage
Here is how to use the root-finding methods:

python
Copy code
from numerical_methods.roots.dichotomie import dichotomie
from numerical_methods.roots.newton import newton
from numerical_methods.roots.point_fixe import pointFixe

# Example function
f = lambda x: x**2 - 2
f_prime = lambda x: 2*x
g = lambda x: (x + 2/x) / 2  # fixed point

# Dichotomy method
res, history = dichotomie(1, 2, 1e-6, f)
print("Root (dichotomy):", res)

# Newton's method
res = newton(1e-6, f, f_prime)
print("Root (newton):", res)

# Fixed-point method
res = pointFixe(1e-6, g)
print("Root (fixed point):", res)
📂 Project Structure
Copy code
numerical_methods/
│
├── roots/
│   ├── dichotomie.py
│   ├── newton.py
│   └── point_fixe.py
├── integration/          ← Coming soon
├── interpolation/        ← Coming soon
└── systems/              ← Coming soon
📊 Requirements
Python ≥ 3.7

tabulate

Installed automatically via pip.

🛠 To do / Coming Soon
 Root-finding methods

 Numerical integration (trapezoidal, Simpson)

 Polynomial interpolation (Lagrange, Newton)

 System solvers (Gauss, LU decomposition)

 Graphical interface or CLI

 Documentation with Sphinx

👨‍💻 Author
Rabie Oudghiri
📧 oudghirirabie@gmail.com
🔗 GitHub Project
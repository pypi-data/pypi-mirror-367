from setuptools import setup, find_packages

setup(
    name='numerical-methods-rabie',
    version='0.1.4',
    description='Méthodes numériques classiques : racines, Newton, etc.',
    author='Rabie Oudghiri',
    author_email='oudghirirabie@gmail.com',
    url='https://github.com/anyrabie/numerical_methods_project_rabie',
    packages=find_packages(),
    install_requires=['tabulate'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics"
    ],
    python_requires='>=3.7',
)
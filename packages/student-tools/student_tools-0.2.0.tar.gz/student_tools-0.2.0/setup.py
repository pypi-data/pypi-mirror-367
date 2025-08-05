from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='student_tools',
    packages=['st'],
    version='0.2.0',
    author='Error Dev',
    author_email='3rr0r.d3v@gmail.com',
    description='[Python 3.12 Recommended] A collection of English, Math, and Utility tools, made for students.',
    install_requires=[
        'sympy', 'pyfiglet'
    ],
    python_requires='>=3.6,<3.13',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ],
)
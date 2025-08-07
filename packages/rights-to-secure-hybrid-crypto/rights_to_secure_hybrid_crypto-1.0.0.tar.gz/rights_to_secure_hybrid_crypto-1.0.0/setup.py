"""
RightsToSecure Hybrid Crypto Wrapper - Setup
Setup configuration for Python package distribution.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "RightsToSecure Hybrid Crypto Wrapper - Quantum-resistant cryptography library"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        'cryptography>=41.0.0',
        'liboqs-python>=0.7.2',
        'pytest>=7.0.0'
    ]

setup(
    name="rights-to-secure-hybrid-crypto",
    version="1.0.0",
    author="Praveen Naidu",
    author_email="contact@arkaenterprises.com",
    description="Hybrid Post-Quantum Cryptography Library combining classical and quantum-resistant algorithms",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://rightstosecure.com",
    project_urls={
        "Bug Tracker": "https://github.com/rightstosecure/hybrid-crypto/issues",
        "Documentation": "https://academy.rightstosecure.com",
        "Source Code": "https://github.com/rightstosecure/hybrid-crypto",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Email",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "api": [
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0",
            "pydantic>=2.0.0",
        ],
        "web": [
            "flask>=2.3.0",
            "flask-cors>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rights-to-secure-demo=examples.demo_key_exchange:main",
            "rights-to-secure-sign-demo=examples.demo_signing:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords=[
        "cryptography",
        "post-quantum",
        "quantum-resistant",
        "hybrid",
        "rsa",
        "ecc",
        "ecdsa",
        "kyber",
        "dilithium",
        "security",
        "encryption",
        "signature",
        "key-exchange",
        "kem",
        "rights-to-secure",
    ],
    platforms=["any"],
    license="MIT",
    zip_safe=False,
) 
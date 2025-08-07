# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2024-12-19

### Changed
- **Improved Project Description**: Updated README.md with more accurate and comprehensive project description
- **Enhanced Documentation**: Added detailed technical implementation sections, performance tables, and deployment guides
- **Better Keywords**: Added "quantum-safe" and "quantum-proof" keywords for better discoverability
- **Updated Package Metadata**: More descriptive package description focusing on production readiness and backward compatibility

### Documentation
- **Comprehensive README**: Added Quick Start section, Technical Implementation details, Performance & Security Levels table
- **Production Guidelines**: Added best practices for production deployment and integration examples
- **Testing Coverage**: Detailed testing instructions and validation procedures
- **Docker Support**: Complete Docker deployment instructions and service descriptions

## [1.0.0] - 2024-12-19

### Added
- Initial release of RightsToSecure Hybrid Crypto Wrapper
- Hybrid Key Encapsulation Mechanism (KEM) combining RSA/ECC with Kyber
- Hybrid Digital Signatures combining ECDSA with Dilithium
- Support for multiple security levels (Kyber levels 1, 3, 5; Dilithium levels 2, 3, 5)
- Key derivation functions using SHAKE256 and HKDF
- Comprehensive utility functions for key generation, encoding, and random generation
- Mock OQS implementation for testing without liboqs-python dependency
- Complete test suite with unit and integration tests
- FastAPI-based REST API for easy integration
- Docker and Docker Compose support for containerized deployment
- Comprehensive documentation and usage examples
- Python package distribution with setup.py and pyproject.toml
- Console scripts for easy demonstration

### Features
- **Hybrid KEM**: RSA+Kyber and ECC+Kyber key exchange mechanisms
- **Hybrid Signatures**: ECDSA+Dilithium digital signatures
- **Multiple Formats**: Support for structured and compact signature formats
- **Key Exchange Packages**: Complete key exchange packages with metadata
- **Signature Manipulation**: Extract, export, and import signature information
- **Tampering Detection**: Built-in verification for message integrity
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Production Ready**: Includes security best practices and error handling

### Technical Details
- Python 3.8+ compatibility
- Uses cryptography library for classical cryptography
- Uses liboqs-python for post-quantum cryptography (optional with mock fallback)
- MIT License for open source use
- Comprehensive test coverage
- Type hints and documentation

### Security Considerations
- Cryptographically secure random generation
- Secure key derivation functions
- Private key protection
- Regular security audits recommended
- Crypto-agility for algorithm updates 
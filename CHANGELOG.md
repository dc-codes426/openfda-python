# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-11-08

### Added
- Initial release of openfda-python
- Comprehensive Python wrapper for openFDA API
- Support for major FDA endpoints:
  - Drug NDC Directory
  - Drug Adverse Events
  - Drug Product Labeling
  - Drug Recall Enforcement Reports
  - Drug Drugs@FDA
  - Drug Shortages
  - Device Adverse Events
  - Device Classifications
  - Device Premarket Approval
  - Device Registrations and Listings
  - Device Unique Device Identifiers
  - Device COVID-19 Testing Evaluations
  - Animal/Veterinary Adverse Events
  - Cosmetic Events
  - Food Adverse Events
  - Tobacco Problem Reports
  - Other Substance Data Reports
  - Other Historical Documents
  - Transparency CRLS
- Smart pagination with automatic hybrid strategy:
  - Skip/limit pagination for first 25,000 results
  - Search_after pagination for results beyond 25,000
  - Support for unlimited result fetching (limit=-1)
- Built-in rate limiting:
  - Token bucket algorithm
  - Configurable per-minute and per-day limits
  - Automatic request throttling
- Type-safe query classes with validation
- Comprehensive data models for all endpoints
- Context manager support for automatic cleanup
- Detailed documentation and usage examples
- GPL-3.0 license

### Features
- `FDAClient`: Main client class with rate limiting
- `BaseQuery`: Abstract base class for all query types
- 20+ specialized query classes for different FDA endpoints
- `Record` and `QueryResult` data models
- Automatic pagination handling
- Error handling and logging
- Support for all FDA API query parameters (search, sort, count, limit, skip)

[Unreleased]: https://github.com/dc-codes426/openfda-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/dc-codes426/openfda-python/releases/tag/v0.1.0

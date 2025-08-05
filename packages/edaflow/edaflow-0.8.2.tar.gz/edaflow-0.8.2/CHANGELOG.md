# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Future features will be documented here

### Changed
- Future changes will be documented here

### Deprecated
- Future deprecations will be documented here

### Removed
- Future removals will be documented here

## [0.8.2] - 2025-08-04

### Fixed
- **METADATA**: Enhanced PyPI metadata to ensure proper changelog display
- **PYPI**: Forced PyPI cache refresh by updating package metadata
- **LINKS**: Added additional project URLs for better discoverability

## [0.8.1] - 2025-08-04

### Fixed
- **FIXED**: Updated changelog dates to current date format
- **FIXED**: Removed duplicate changelog header that was causing PyPI display issues
- **ENHANCED**: Improved changelog formatting for better PyPI presentation

## [0.8.0] - 2025-08-04

### Added
- **NEW**: `visualize_histograms()` function with advanced statistical analysis and skewness detection
- Comprehensive distribution analysis with normality testing (Shapiro-Wilk, Jarque-Bera, Anderson-Darling)
- Advanced skewness interpretation: Normal (|skew| < 0.5), Moderate (0.5-1), High (≥1)
- Kurtosis analysis: Normal, Heavy-tailed (leptokurtic), Light-tailed (platykurtic)
- KDE curve overlays and normal distribution comparisons
- Statistical text boxes with comprehensive distribution metrics
- Transformation recommendations based on skewness analysis
- Multi-column histogram visualization with automatic subplot layout
- Missing data handling and robust error validation
- Detailed statistical reporting with emoji-formatted output

### Enhanced
- Updated Complete EDA Workflow to include 12 functions (from 9)
- Added histogram analysis as Step 10 in the comprehensive workflow
- Enhanced README documentation with detailed histogram function examples
- Comprehensive test suite with 7 test scenarios covering various distribution types

### Fixed
- Fixed Anderson-Darling test attribute error (significance_levels → significance_level)
- Improved statistical test error handling and validation

## [0.7.0] - 2025-08-03

### Added
- **NEW**: `visualize_heatmap()` function with comprehensive heatmap visualizations
- Four distinct heatmap types: correlation, missing data patterns, values, and cross-tabulation
- Multiple correlation methods: Pearson, Spearman, and Kendall
- Missing data pattern visualization with threshold highlighting
- Data values heatmap for detailed small dataset inspection  
- Cross-tabulation heatmaps for categorical relationship analysis
- Automatic statistical insights and detailed reporting
- Smart column detection and validation for each heatmap type
- Comprehensive customization options (colors, sizing, annotations)
- Enhanced Complete EDA Workflow with Step 11: Heatmap Analysis
- Comprehensive test suite with error handling validation
- Updated README documentation with detailed heatmap examples and use cases

### Enhanced
- Complete EDA workflow now includes 11 steps with comprehensive heatmap analysis
- Updated package features to highlight new heatmap visualization capabilities
- Improved documentation with statistical insights explanations

## [0.6.0] - 2025-08-02

### Added
- **NEW**: `visualize_interactive_boxplots()` function with full Plotly Express integration
- Interactive boxplot visualization with hover tooltips, zoom, and pan functionality
- Statistical summaries with emoji-formatted output for better readability
- Customizable styling options (colors, dimensions, margins)
- Smart column selection for numerical data
- Complete Plotly Express px.box equivalent functionality
- Added plotly>=5.0.0 dependency for interactive visualizations
- Comprehensive test suite for interactive visualization function
- Updated Complete EDA Workflow Example to include interactive visualization as Step 10
- Enhanced README documentation with interactive visualization examples and features

### Enhanced
- Complete EDA workflow now includes 10 steps with interactive final visualization
- Updated requirements documentation to include plotly dependency
- Improved package feature list to highlight interactive capabilities

## [0.5.1] - 2024-01-14

### Fixed
- Updated PyPI documentation to properly showcase handle_outliers_median() function in Complete EDA Workflow Example
- Ensured PyPI page displays the complete 9-step EDA workflow including outlier handling
- Synchronized local documentation improvements with PyPI display

## [0.5.0] - 2025-08-04

### Added
- `handle_outliers_median()` function for automated outlier detection and replacement
- Multiple outlier detection methods: IQR, Z-score, and Modified Z-score
- Complete outlier analysis workflow integration with boxplot visualization
- Median-based outlier replacement for robust statistical handling
- Flexible column selection with automatic numerical column detection
- Detailed reporting showing exactly which outliers were replaced and statistical bounds
- Safe operation mode (inplace=False by default) to preserve original data
- Statistical method comparison with customizable IQR multipliers
- Complete 9-function EDA package with comprehensive outlier management

### Fixed
- Dtype compatibility improvements to eliminate pandas FutureWarnings
- Enhanced error handling and validation for numerical column processing

## [0.4.2] - 2025-08-04

### Fixed
- Updated README.md changelog to properly reflect v0.4.1 boxplot features on PyPI page
- Corrected version history display for proper PyPI documentation

## [0.4.1] - 2025-08-04

### Added
- `visualize_numerical_boxplots()` function for comprehensive outlier detection and statistical analysis
- Advanced boxplot visualization with customizable layouts (rows/cols), orientations, and color palettes
- Automatic numerical column detection for boxplot analysis
- Detailed statistical summaries including skewness analysis and interpretation
- IQR-based outlier detection with threshold reporting
- Comprehensive outlier identification with actual outlier values displayed
- Support for horizontal and vertical boxplot orientations
- Seaborn integration for enhanced styling and color palettes

### Fixed
- `impute_categorical_mode()` function now properly returns DataFrame instead of None
- Corrected inplace parameter handling for categorical imputation function

### Fixed
- Future fixes will be documented here

### Security
- Future security updates will be documented here

## [0.1.0] - 2025-08-04

### Added
- Initial package structure
- Basic `hello()` function in `edaflow.__init__`
- Setup configuration with `setup.py` and `pyproject.toml`
- Core dependencies: pandas, numpy, matplotlib, seaborn, scipy, missingno
- Comprehensive README with installation and usage instructions
- MIT License
- Development dependencies and tooling configuration
- Git ignore file
- Basic project documentation structure

### Infrastructure
- Package structure with `edaflow/` module directory
- Development tooling setup (black, flake8, isort, pytest, mypy)
- Continuous integration ready configuration
- PyPI publishing ready setup

[Unreleased]: https://github.com/yourusername/edaflow/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/edaflow/releases/tag/v0.1.0

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

## [0.12.0] - 2025-08-06 - Machine Learning Preprocessing Release 🤖

### Added
- `analyze_encoding_needs()` function for intelligent categorical encoding strategy analysis
  - Automatic cardinality analysis for optimal encoding method selection
  - Target correlation analysis for supervised encoding recommendations
  - Memory impact assessment for high-cardinality features
  - Support for 7 different encoding strategies: One-Hot, Target, Ordinal, Binary, TF-IDF, Text, and Keep Numeric
  - Beautiful emoji-rich output with detailed recommendations and summaries
  
- `apply_smart_encoding()` function for automated categorical variable transformation
  - Intelligent preprocessing pipeline with automatic analysis integration
  - Memory-efficient handling of high-cardinality categorical variables
  - Support for scikit-learn encoders: OneHotEncoder, TargetEncoder, OrdinalEncoder
  - TF-IDF vectorization for text features with customizable parameters
  - Binary encoding for medium cardinality features to optimize memory usage
  - Graceful handling of unknown categories with configurable strategies
  - Comprehensive progress tracking with emoji-rich status updates
  - Automatic shape transformation reporting (columns before/after)

### Enhanced
- Package now includes comprehensive ML preprocessing capabilities alongside EDA functions
- Total function count increased from 18 to 20 with new encoding suite
- Improved integration with scikit-learn ecosystem for end-to-end ML workflows
- Enhanced documentation with ML preprocessing examples and use cases

### Dependencies
- Added scikit-learn integration for advanced encoding transformations
- Maintained backward compatibility with existing EDA functionality
- All new features include graceful fallbacks if optional dependencies unavailable

## [0.11.0] - 2025-01-30 - Image Feature Analysis Release 🎨

### Added
- `analyze_image_features()` function for deep statistical analysis of visual features
- Edge density analysis using Canny, Sobel, and Laplacian edge detection methods  
- Texture analysis with Local Binary Patterns (LBP) for pattern characterization
- Color histogram analysis across RGB, HSV, LAB, and grayscale color spaces
- Gradient magnitude and direction analysis for understanding image structure
- Feature ranking system to identify most discriminative features between classes
- Statistical comparison framework for quantifying inter-class visual differences
- Comprehensive visualization suite with box plots for feature distributions
- Automated recommendation system for feature engineering and preprocessing decisions
- Production-ready feature extraction with optional raw feature vector export
- OpenCV and scikit-image integration with graceful fallback mechanisms
- Support for custom analysis parameters (LBP radius, edge thresholds, color spaces)

### Enhanced
- Expanded edaflow from 16 to 17 comprehensive EDA functions
- Complete computer vision EDA trinity: Visualization + Quality + Features
- Advanced dependency handling for optimal performance with available libraries

### Technical
- Added CV2_AVAILABLE and SKIMAGE_AVAILABLE flags for robust dependency checking
- Implemented comprehensive edge detection fallbacks using scipy when advanced libraries unavailable
- Enhanced texture analysis with multiple feature extraction methods
- Added multi-color-space support with automatic conversion handling

## [0.8.6] - 2025-08-05

### Fixed - PyPI Changelog Display Issue
- **CRITICAL**: Fixed PyPI changelog not displaying latest releases (v0.8.4, v0.8.5)
- **DOCUMENTATION**: Updated README.md changelog section that PyPI displays instead of CHANGELOG.md
- **PYPI**: Synchronized README.md changelog with comprehensive CHANGELOG.md content
- **ENHANCED**: Ensured PyPI users see complete version history and latest features

## [0.8.5] - 2025-08-05

### Changed - Code Organization and Structure Improvement Release
- **REFACTORED**: Renamed `missing_data.py` to `core.py` to better reflect comprehensive EDA functionality
- **ENHANCED**: Updated module docstring to describe complete suite of analysis functions
- **IMPROVED**: Better project structure with appropriately named core module containing all 14 EDA functions
- **FIXED**: Updated all imports and tests to reference the new core module structure
- **MAINTAINED**: Full backward compatibility - all functions work exactly the same

## [0.8.4] - 2025-08-05

### Added - Comprehensive Scatter Matrix Visualization Release
- **NEW**: `visualize_scatter_matrix()` function with advanced pairwise relationship analysis
- **NEW**: Flexible diagonal plots: histograms, KDE curves, and box plots
- **NEW**: Customizable upper/lower triangles: scatter plots, correlation coefficients, or blank
- **NEW**: Color coding by categorical variables for group-specific pattern analysis
- **NEW**: Multiple regression line types: linear, polynomial (2nd/3rd degree), and LOWESS smoothing
- **NEW**: Comprehensive statistical insights: correlation analysis, pattern identification
- **NEW**: Professional scatter matrix layouts with adaptive figure sizing
- **NEW**: Full integration with existing edaflow workflow and styling consistency
- **ENHANCED**: Complete EDA visualization suite now includes 14 functions (from 13)
- **ENHANCED**: Added scikit-learn and statsmodels dependencies for advanced analytics
- **ENHANCED**: Updated package metadata and documentation for scatter matrix capabilities

### Technical Features
- **Matrix Customization**: Independent control of diagonal, upper, and lower triangle content
- **Statistical Analysis**: Automatic correlation strength categorization and reporting  
- **Regression Analysis**: Advanced trend line fitting with multiple algorithm options
- **Color Intelligence**: Automatic categorical/numerical variable handling for color coding
- **Performance Optimization**: Efficient handling of large datasets with smart sampling suggestions
- **Error Handling**: Comprehensive validation with informative error messages
- **Professional Output**: Publication-ready visualizations with consistent edaflow styling

## [0.8.3] - 2025-08-04

### Fixed
- **CRITICAL**: Updated README.md changelog section that PyPI was displaying instead of CHANGELOG.md
- **PYPI**: Fixed PyPI changelog display by synchronizing README.md changelog with main CHANGELOG.md
- **DOCUMENTATION**: Ensured consistent changelog information across all package files

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

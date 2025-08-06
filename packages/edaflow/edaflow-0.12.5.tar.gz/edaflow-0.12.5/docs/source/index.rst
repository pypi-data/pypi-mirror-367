edaflow Documentation
=====================

.. image:: https://img.shields.io/pypi/v/edaflow.svg
   :target: https://pypi.org/project/edaflow/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/edaflow.svg
   :target: https://pypi.org/project/edaflow/
   :alt: Python versions

.. image:: https://img.shields.io/github/license/evanlow/edaflow.svg
   :target: https://github.com/evanlow/edaflow/blob/main/LICENSE
   :alt: License

edaflow is a Python package designed to streamline exploratory data analysis (EDA) workflows. It provides 16 comprehensive functions that cover the essential steps of data exploration, from missing data analysis to advanced visualizations and computer vision dataset assessment.

**edaflow** simplifies and accelerates the EDA process by providing a collection of 16 powerful functions for data scientists and analysts. The package integrates popular data science libraries to create a cohesive workflow for data exploration, visualization, and preprocessing - now including computer vision datasets and quality assessment.

🎯 **Key Features**
-------------------

* **Missing Data Analysis**: Color-coded analysis of null values with customizable thresholds
* **Categorical Data Insights**: Identify object columns that might be numeric, detect data type issues
* **Automatic Data Type Conversion**: Smart conversion of object columns to numeric when appropriate
* **Data Imputation**: Smart missing value imputation using median for numerical and mode for categorical columns
* **Advanced Visualizations**: Interactive boxplots, comprehensive heatmaps, statistical histograms
* **Scatter Matrix Analysis**: Advanced pairwise relationship visualization with regression lines
* **Computer Vision EDA**: Class-wise image sample visualization for image classification datasets
* **Outlier Handling**: Automated outlier detection and replacement using multiple statistical methods
* **Professional Output**: Beautiful, color-coded results optimized for Jupyter notebooks

📦 **Quick Installation**
-------------------------

.. code-block:: bash

   pip install edaflow

🚀 **Quick Start Example**
--------------------------

.. code-block:: python

   import edaflow
   import pandas as pd

   # Load your data
   df = pd.read_csv('your_data.csv')

   # Complete EDA workflow with 16 functions
   edaflow.check_null_columns(df)                    # 1. Missing data analysis
   edaflow.analyze_categorical_columns(df)           # 2. Categorical insights
   df_clean = edaflow.convert_to_numeric(df)         # 3. Smart type conversion
   edaflow.visualize_categorical_values(df_clean)    # 4. Category exploration
   edaflow.visualize_scatter_matrix(df_clean)        # 5. Relationship analysis
   edaflow.visualize_heatmap(df_clean)              # 6. Correlation heatmaps
   edaflow.visualize_histograms(df_clean)           # 7. Distribution analysis
   # ... and 9 more powerful functions!
   
   # NEW: Computer Vision EDA & Quality Assessment
   edaflow.visualize_image_classes(data_source='dataset/images/')  # Simple directory path
   edaflow.assess_image_quality(data_source='dataset/images/')     # Image quality assessment

📚 **Documentation Contents**
-----------------------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   user_guide/index
   api_reference/index
   examples/index
   changelog
   contributing

🔗 **Useful Links**
-------------------

* **GitHub Repository**: https://github.com/evanlow/edaflow
* **PyPI Package**: https://pypi.org/project/edaflow/
* **Issue Tracker**: https://github.com/evanlow/edaflow/issues
* **Changelog**: :doc:`changelog`

📊 **Function Overview**
------------------------

edaflow provides 16 comprehensive EDA functions organized into logical categories:

**Data Quality & Analysis**
~~~~~~~~~~~~~~~~~~~~~~~~~~~
* :func:`~edaflow.check_null_columns` - Missing data analysis with color coding
* :func:`~edaflow.analyze_categorical_columns` - Categorical data insights
* :func:`~edaflow.convert_to_numeric` - Smart data type conversion
* :func:`~edaflow.display_column_types` - Column type classification

**Data Cleaning & Preprocessing**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* :func:`~edaflow.impute_numerical_median` - Numerical missing value imputation
* :func:`~edaflow.impute_categorical_mode` - Categorical missing value imputation
* :func:`~edaflow.handle_outliers_median` - Outlier detection and handling

**Visualization & Analysis**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* :func:`~edaflow.visualize_categorical_values` - Categorical value exploration
* :func:`~edaflow.visualize_numerical_boxplots` - Distribution and outlier analysis
* :func:`~edaflow.visualize_interactive_boxplots` - Interactive Plotly visualizations
* :func:`~edaflow.visualize_heatmap` - Comprehensive heatmap analysis
* :func:`~edaflow.visualize_histograms` - Statistical distribution analysis
* :func:`~edaflow.visualize_scatter_matrix` - Advanced pairwise relationship analysis

**Computer Vision EDA** 🖼️ **NEW in v0.9.0-v0.12.3!**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* :func:`~edaflow.visualize_image_classes` - Class-wise image sample visualization for image classification datasets

**Image Quality Assessment** 🔍 **NEW in v0.10.0-v0.12.3!**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* :func:`~edaflow.assess_image_quality` - Comprehensive automated quality assessment and corruption detection for image datasets

**Helper Functions**
~~~~~~~~~~~~~~~~~~~~
* :func:`~edaflow.hello` - Package verification function

🎓 **Background**
-----------------------------

edaflow was developed in part of a Capstone project during an AI/ML course conducted by NTUC LearningHub (Cohort 15). 
Special thanks to our instructor, Ms. Isha Sehgal, who inspired the project works which led to the development of this comprehensive EDA toolkit.

📄 **License**
--------------

This project is licensed under the MIT License - see the `LICENSE <https://github.com/evanlow/edaflow/blob/main/LICENSE>`_ file for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

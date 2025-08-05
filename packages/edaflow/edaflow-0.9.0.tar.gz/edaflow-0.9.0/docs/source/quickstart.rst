Quick Start Guide
=================

This guide will get you up and running with edaflow in just a few minutes!

🚀 **Basic Usage**
------------------

First, install and import edaflow:

.. code-block:: python

   # Install (if not already done)
   # pip install edaflow
   
   import edaflow
   import pandas as pd
   
   # Verify installation
   print(edaflow.hello())

📊 **Complete EDA Workflow**
----------------------------

Here's how to perform a complete exploratory data analysis with edaflow's 14 functions:

.. code-block:: python

   import pandas as pd
   import edaflow
   
   # Load your dataset
   df = pd.read_csv('your_data.csv')
   print(f"Dataset shape: {df.shape}")
   
   # Step 1: Missing Data Analysis
   print("\\n1. MISSING DATA ANALYSIS")
   print("-" * 40)
   null_analysis = edaflow.check_null_columns(df, threshold=10)
   null_analysis  # Beautiful color-coded output in Jupyter
   
   # Step 2: Categorical Data Insights
   print("\\n2. CATEGORICAL DATA ANALYSIS")
   print("-" * 40)
   edaflow.analyze_categorical_columns(df, threshold=35)
   
   # Step 3: Smart Data Type Conversion
   print("\\n3. AUTOMATIC DATA TYPE CONVERSION")
   print("-" * 40)
   df_cleaned = edaflow.convert_to_numeric(df, threshold=35)
   
   # Step 4: Explore Categorical Values
   print("\\n4. CATEGORICAL VALUES EXPLORATION")
   print("-" * 40)
   edaflow.visualize_categorical_values(df_cleaned)
   
   # Step 5: Column Type Classification
   print("\\n5. COLUMN TYPE CLASSIFICATION")
   print("-" * 40)
   column_types = edaflow.display_column_types(df_cleaned)
   
   # Step 6: Data Imputation
   print("\\n6. MISSING VALUE IMPUTATION")
   print("-" * 40)
   df_numeric_imputed = edaflow.impute_numerical_median(df_cleaned)
   df_fully_imputed = edaflow.impute_categorical_mode(df_numeric_imputed)
   
   # Step 7: Statistical Distribution Analysis
   print("\\n7. STATISTICAL DISTRIBUTION ANALYSIS")
   print("-" * 40)
   edaflow.visualize_histograms(df_fully_imputed, kde=True, show_normal_curve=True)
   
   # Step 8: Comprehensive Relationship Analysis
   print("\\n8. RELATIONSHIP ANALYSIS")
   print("-" * 40)
   edaflow.visualize_heatmap(df_fully_imputed, heatmap_type='correlation')
   edaflow.visualize_scatter_matrix(df_fully_imputed, regression_line='linear')
   
   # Step 9: Outlier Detection and Visualization
   print("\\n9. OUTLIER DETECTION")
   print("-" * 40)
   edaflow.visualize_numerical_boxplots(df_fully_imputed, show_skewness=True)
   edaflow.visualize_interactive_boxplots(df_fully_imputed)
   
   # Step 10: Advanced Heatmap Analysis
   print("\\n10. ADVANCED HEATMAP ANALYSIS")
   print("-" * 40)
   edaflow.visualize_heatmap(df_fully_imputed, heatmap_type='missing')
   edaflow.visualize_heatmap(df_fully_imputed, heatmap_type='values')
   
   # Step 11: Outlier Handling
   print("\\n11. OUTLIER HANDLING")
   print("-" * 40)
   df_final = edaflow.handle_outliers_median(df_fully_imputed, method='iqr', verbose=True)
   
   # Step 12: Results Verification
   print("\\n12. RESULTS VERIFICATION")
   print("-" * 40)
   edaflow.visualize_scatter_matrix(df_final, title="Clean Data Relationships")
   edaflow.visualize_numerical_boxplots(df_final, title="Final Clean Distribution")

🎯 **Key Function Examples**
----------------------------

**Missing Data Analysis**
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   import edaflow
   
   # Sample data with missing values
   df = pd.DataFrame({
       'name': ['Alice', 'Bob', None, 'Diana'],
       'age': [25, None, 35, None],
       'salary': [50000, 60000, None, 70000]
   })
   
   # Color-coded missing data analysis
   result = edaflow.check_null_columns(df, threshold=20)
   result  # Display in Jupyter for beautiful formatting

**Scatter Matrix Analysis** ⭐ *New in v0.8.4*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Advanced pairwise relationship visualization
   edaflow.visualize_scatter_matrix(
       df,
       columns=['feature1', 'feature2', 'feature3'],
       color_column='category',      # Color by category
       diagonal_type='kde',          # KDE plots on diagonal
       upper_triangle='corr',        # Correlations in upper triangle
       lower_triangle='scatter',     # Scatter plots in lower triangle
       regression_line='linear',     # Add regression lines
       figsize=(12, 12)
   )

**Interactive Visualizations**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Interactive Plotly boxplots with zoom and hover
   edaflow.visualize_interactive_boxplots(
       df,
       title="Interactive Data Exploration",
       height=600,
       show_points='outliers'  # Show outlier points
   )

**Comprehensive Heatmaps**
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Multiple heatmap types for different insights
   
   # 1. Correlation analysis
   edaflow.visualize_heatmap(df, heatmap_type='correlation', method='pearson')
   
   # 2. Missing data patterns
   edaflow.visualize_heatmap(df, heatmap_type='missing')
   
   # 3. Cross-tabulation analysis
   edaflow.visualize_heatmap(df, heatmap_type='crosstab')
   
   # 4. Data values visualization
   edaflow.visualize_heatmap(df.head(20), heatmap_type='values')

**Statistical Distribution Analysis**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Advanced histogram analysis with statistical testing
   edaflow.visualize_histograms(
       df,
       kde=True,                    # Add KDE curves
       show_normal_curve=True,      # Compare to normal distribution
       show_stats=True,             # Statistical summary boxes
       bins=30                      # Custom bin count
   )

**Smart Data Type Conversion**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Automatically detect and convert numeric columns stored as text
   df_original = pd.DataFrame({
       'product': ['Laptop', 'Mouse', 'Keyboard'],
       'price_text': ['999', '25', '75'],        # Should be numeric
       'category': ['Electronics', 'Accessories', 'Accessories']
   })
   
   # Smart conversion
   df_converted = edaflow.convert_to_numeric(df_original, threshold=35)
   print(df_converted.dtypes)  # 'price_text' now converted to float

🔍 **Function Categories**
--------------------------

**Data Quality & Analysis**
~~~~~~~~~~~~~~~~~~~~~~~~~~~
* ``check_null_columns()`` - Missing data analysis
* ``analyze_categorical_columns()`` - Categorical insights  
* ``convert_to_numeric()`` - Smart type conversion
* ``display_column_types()`` - Column classification

**Data Cleaning & Preprocessing**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* ``impute_numerical_median()`` - Numerical imputation
* ``impute_categorical_mode()`` - Categorical imputation
* ``handle_outliers_median()`` - Outlier handling

**Visualization & Analysis**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* ``visualize_categorical_values()`` - Category exploration
* ``visualize_numerical_boxplots()`` - Distribution analysis
* ``visualize_interactive_boxplots()`` - Interactive plots
* ``visualize_heatmap()`` - Comprehensive heatmaps
* ``visualize_histograms()`` - Statistical distributions
* ``visualize_scatter_matrix()`` - Pairwise relationships

💡 **Pro Tips**
---------------

1. **Jupyter Notebooks**: Use edaflow in Jupyter for the best visual experience with color-coded outputs
2. **Large Datasets**: For datasets with >10,000 rows, consider sampling for visualization functions
3. **Memory Management**: Process data in chunks for very large datasets
4. **Custom Thresholds**: Adjust threshold parameters based on your data quality tolerance
5. **Interactive Mode**: Use ``visualize_interactive_boxplots()`` for presentations and exploratory analysis

🚀 **Next Steps**
-----------------

* Explore the :doc:`user_guide/index` for detailed function documentation
* Check out :doc:`examples/index` for real-world use cases
* Review the :doc:`api_reference/index` for complete function parameters
* See :doc:`changelog` for the latest features and improvements

**Ready to dive deeper?** The User Guide contains comprehensive examples and advanced usage patterns!

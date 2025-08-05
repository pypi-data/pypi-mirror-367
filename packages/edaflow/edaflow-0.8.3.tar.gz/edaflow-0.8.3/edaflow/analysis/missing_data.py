"""
Missing data analysis functions for edaflow.

This module provides utilities for analyzing and visualizing missing data patterns.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Union
import math


def check_null_columns(df: pd.DataFrame,
                       threshold: Optional[float] = 10) -> pd.DataFrame:
    """
    Check null values in DataFrame columns with styled output.

    Calculates the percentage of null values per column and applies color styling
    based on the percentage of nulls relative to the threshold.

    Args:
        df (pd.DataFrame): The input DataFrame to analyze
        threshold (Optional[float], optional): The threshold percentage for
                                             highlighting. Defaults to 10.

    Returns:
        pd.DataFrame: A styled DataFrame showing column names and null
                     percentages with color coding:
                     - Red: > 2*threshold (high null percentage)
                     - Yellow: > threshold but <= 2*threshold (medium null %)
                     - Light yellow: > 0 but <= threshold (low null %)
                     - Gray: 0 (no nulls)

    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> df = pd.DataFrame({'A': [1, 2, None], 'B': [1, None, None]})
        >>> styled_result = edaflow.check_null_columns(df, threshold=20)
        >>> # Returns styled DataFrame with null percentages

        # Alternative import style:
        >>> from edaflow.analysis import check_null_columns
        >>> styled_result = check_null_columns(df, threshold=20)
    """
    # Calculate null percentages
    null_counts = df.isnull().sum()
    total_rows = len(df)
    null_percentages = (null_counts / total_rows * 100).round(2)

    # Create result DataFrame
    result_df = pd.DataFrame({
        'Column': df.columns,
        'Null_Count': null_counts.values,
        'Null_Percentage': null_percentages.values
    })

    def style_nulls(val):
        """Apply color styling based on null percentage."""
        if val == 0:
            return 'background-color: lightgray'
        elif val > threshold * 2:
            return 'background-color: red; color: white'
        elif val > threshold:
            return 'background-color: yellow'
        else:  # val > 0
            return 'background-color: lightyellow'

    # Apply styling to the Null_Percentage column
    styled_df = result_df.style.map(style_nulls, subset=['Null_Percentage'])

    return styled_df


def analyze_categorical_columns(df: pd.DataFrame, 
                              threshold: Optional[float] = 35) -> None:
    """
    Analyze categorical columns of object type to identify potential data issues.
    
    This function examines object-type columns to detect:
    1. Columns that might be numeric but stored as strings
    2. Categorical columns with their unique values
    3. Data type consistency issues
    
    Args:
        df (pd.DataFrame): The input DataFrame to analyze
        threshold (Optional[float], optional): The threshold percentage for 
                                             non-numeric values. If a column 
                                             has less than this percentage of 
                                             non-numeric values, it's flagged 
                                             as potentially numeric. Defaults to 35.
    
    Returns:
        None: Prints analysis results directly to console with color coding
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> df = pd.DataFrame({
        ...     'name': ['Alice', 'Bob', 'Charlie'],
        ...     'age_str': ['25', '30', '35'], 
        ...     'mixed': ['1', '2', 'three'],
        ...     'numbers': [1, 2, 3]
        ... })
        >>> edaflow.analyze_categorical_columns(df, threshold=35)
        # Output with color coding:
        # age_str is potentially a numeric column that needs conversion
        # age_str has ['25' '30' '35'] values
        # mixed has too many non-numeric values (33.33% non-numeric)
        # numbers is not an object column
        
        # Alternative import style:
        >>> from edaflow.analysis import analyze_categorical_columns
    """
    print("Analyzing categorical columns of object type...")
    print("=" * 50)
    
    for col in df.columns:
        if df[col].dtype == 'object':
            # Try to convert to numeric and check how many fail
            numeric_col = pd.to_numeric(df[col], errors='coerce')
            non_numeric_pct = (numeric_col.isnull().sum() / len(numeric_col)) * 100
            
            if non_numeric_pct < threshold:
                # Potential numeric column - highlight in red with blue background
                print('\x1b[1;31;44m{} is potentially a numeric column that needs conversion\x1b[m'.format(col))
                print('\x1b[1;30;43m{} has {} unique values: {}\x1b[m'.format(
                    col, df[col].nunique(), df[col].unique()[:10]  # Show first 10 unique values
                ))
            else:
                # Truly categorical column
                unique_count = df[col].nunique()
                total_count = len(df[col])
                print('{} has too many non-numeric values ({}% non-numeric)'.format(
                    col, round(non_numeric_pct, 2)
                ))
                print('  └─ {} unique values out of {} total ({} unique values shown): {}'.format(
                    unique_count, total_count, min(10, unique_count), 
                    df[col].unique()[:10]  # Show first 10 unique values
                ))
        else:
            print('{} is not an object column (dtype: {})'.format(col, df[col].dtype))
    
    print("=" * 50)
    print("Analysis complete!")


def convert_to_numeric(df: pd.DataFrame, 
                      threshold: Optional[float] = 35,
                      inplace: bool = False) -> pd.DataFrame:
    """
    Convert object columns to numeric when appropriate based on data analysis.
    
    This function examines object-type columns and converts them to numeric
    if the percentage of non-numeric values is below the specified threshold.
    This helps clean datasets where numeric data is stored as strings.
    
    Args:
        df (pd.DataFrame): The input DataFrame to process
        threshold (Optional[float], optional): The threshold percentage for 
                                             non-numeric values. Columns with
                                             fewer non-numeric values than this
                                             threshold will be converted to numeric.
                                             Defaults to 35.
        inplace (bool, optional): If True, modify the DataFrame in place and return None.
                                If False, return a new DataFrame with conversions applied.
                                Defaults to False.
    
    Returns:
        pd.DataFrame or None: If inplace=False, returns a new DataFrame with 
                            numeric conversions applied. If inplace=True, 
                            modifies the original DataFrame and returns None.
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> df = pd.DataFrame({
        ...     'name': ['Alice', 'Bob', 'Charlie'],
        ...     'age_str': ['25', '30', '35'], 
        ...     'mixed': ['1', '2', 'three'],
        ...     'numbers': [1, 2, 3]
        ... })
        >>> 
        >>> # Create a copy with conversions
        >>> df_cleaned = edaflow.convert_to_numeric(df, threshold=35)
        >>> 
        >>> # Or modify the original DataFrame
        >>> edaflow.convert_to_numeric(df, threshold=35, inplace=True)
        >>> 
        >>> # Alternative import style:
        >>> from edaflow.analysis import convert_to_numeric
        >>> df_cleaned = convert_to_numeric(df, threshold=50)
    
    Notes:
        - Values that cannot be converted to numeric become NaN
        - The function provides colored output showing which columns were converted
        - Use a lower threshold to be more strict about conversions
        - Use a higher threshold to be more lenient about mixed data
    """
    # Create a copy if not modifying inplace
    if not inplace:
        df_result = df.copy()
    else:
        df_result = df
    
    print("Converting object columns to numeric where appropriate...")
    print("=" * 60)
    
    conversions_made = []
    
    for col in df_result.columns:
        if df_result[col].dtype == 'object':
            # Try to convert to numeric and check how many fail
            numeric_col = pd.to_numeric(df_result[col], errors='coerce')
            non_numeric_pct = (numeric_col.isnull().sum() / len(numeric_col)) * 100
            
            if non_numeric_pct < threshold:
                # Convert the column to numeric
                original_nulls = df_result[col].isnull().sum()
                df_result[col] = pd.to_numeric(df_result[col], errors='coerce')
                new_nulls = df_result[col].isnull().sum()
                values_converted_to_nan = new_nulls - original_nulls
                
                # Colored output for successful conversion
                print('\x1b[1;31;44mConverting {} to a numerical column\x1b[m'.format(col))
                print('  └─ {}% of values were non-numeric ({} values converted to NaN)'.format(
                    round(non_numeric_pct, 2), values_converted_to_nan
                ))
                
                conversions_made.append({
                    'column': col,
                    'non_numeric_pct': round(non_numeric_pct, 2),
                    'values_converted_to_nan': values_converted_to_nan
                })
            else:
                # Skip conversion - too many non-numeric values
                print('{} skipped: {}% non-numeric values (threshold: {}%)'.format(
                    col, round(non_numeric_pct, 2), threshold
                ))
        else:
            print('{} skipped: already numeric (dtype: {})'.format(col, df_result[col].dtype))
    
    print("=" * 60)
    
    if conversions_made:
        print(f"✅ Successfully converted {len(conversions_made)} columns to numeric:")
        for conversion in conversions_made:
            print(f"   • {conversion['column']}: {conversion['non_numeric_pct']}% non-numeric")
    else:
        print("ℹ️  No columns were converted (all were either already numeric or above threshold)")
    
    print("Conversion complete!")
    
    # Return the result DataFrame if not inplace, otherwise return None
    return None if inplace else df_result


def visualize_categorical_values(df: pd.DataFrame, 
                                max_unique_values: Optional[int] = 20,
                                show_counts: bool = True,
                                show_percentages: bool = True) -> None:
    """
    Visualize unique values in categorical (object-type) columns with counts and percentages.
    
    This function provides a comprehensive overview of categorical columns by displaying:
    - Unique values in each categorical column
    - Value counts (frequency of each unique value)
    - Percentages (relative frequency)
    - Summary statistics for each column
    
    Args:
        df (pd.DataFrame): The input DataFrame to analyze
        max_unique_values (Optional[int], optional): Maximum number of unique values 
                                                   to display per column. If a column 
                                                   has more unique values, only the top 
                                                   N most frequent will be shown. 
                                                   Defaults to 20.
        show_counts (bool, optional): Whether to show the count of each unique value.
                                    Defaults to True.
        show_percentages (bool, optional): Whether to show the percentage of each 
                                         unique value. Defaults to True.
    
    Returns:
        None: Prints visualization results directly to console with formatting
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> df = pd.DataFrame({
        ...     'category': ['A', 'B', 'A', 'C', 'B', 'A'],
        ...     'status': ['active', 'inactive', 'active', 'pending', 'active', 'active'],
        ...     'region': ['North', 'South', 'North', 'East', 'West', 'North'],
        ...     'score': [85, 92, 78, 88, 95, 82]
        ... })
        >>> 
        >>> # Basic visualization
        >>> edaflow.visualize_categorical_values(df)
        >>> 
        >>> # Show only top 10 values per column, without percentages
        >>> edaflow.visualize_categorical_values(df, max_unique_values=10, show_percentages=False)
        >>> 
        >>> # Alternative import style:
        >>> from edaflow.analysis import visualize_categorical_values
        >>> visualize_categorical_values(df, max_unique_values=15)
    
    Notes:
        - Only analyzes columns with object dtype (categorical/string columns)
        - Columns with many unique values are truncated to show most frequent ones
        - Provides summary statistics including total unique values and most common value
        - Uses color coding to highlight column names and important information
    """
    # Find categorical columns
    cat_columns = [col for col in df.columns if df[col].dtype == 'object']
    
    if not cat_columns:
        print("🔍 No categorical (object-type) columns found in the DataFrame.")
        print("   All columns appear to be numeric or datetime types.")
        return
    
    print("📊 CATEGORICAL COLUMNS VISUALIZATION")
    print("=" * 70)
    print(f"Found {len(cat_columns)} categorical column(s): {', '.join(cat_columns)}")
    print("=" * 70)
    
    for i, col in enumerate(cat_columns, 1):
        # Get value counts
        value_counts = df[col].value_counts(dropna=False)
        total_values = len(df[col])
        unique_count = len(value_counts)
        
        # Handle missing values
        null_count = df[col].isnull().sum()
        
        # Column header with color coding
        print(f'\n\x1b[1;36m[{i}/{len(cat_columns)}] Column: {col}\x1b[m')
        print(f'📈 Total values: {total_values} | Unique values: {unique_count} | Missing: {null_count}')
        
        if unique_count == 0:
            print('⚠️  Column is completely empty')
            continue
            
        # Determine how many values to show
        values_to_show = min(max_unique_values, unique_count)
        
        if unique_count > max_unique_values:
            print(f'📋 Showing top {values_to_show} most frequent values (out of {unique_count} total):')
        else:
            print(f'📋 All unique values:')
        
        # Display values with counts and percentages
        for j, (value, count) in enumerate(value_counts.head(values_to_show).items(), 1):
            # Handle NaN values display
            display_value = 'NaN/Missing' if pd.isna(value) else repr(value)
            
            # Calculate percentage
            percentage = (count / total_values) * 100
            
            # Build the display string
            display_parts = [f'   {j:2d}. {display_value}']
            
            if show_counts:
                display_parts.append(f'Count: {count}')
            
            if show_percentages:
                display_parts.append(f'({percentage:.1f}%)')
            
            print(' | '.join(display_parts))
        
        # Show truncation message if needed
        if unique_count > max_unique_values:
            remaining = unique_count - max_unique_values
            print(f'   ... and {remaining} more unique value(s)')
        
        # Summary statistics
        most_common_value = value_counts.index[0]
        most_common_count = value_counts.iloc[0]
        most_common_pct = (most_common_count / total_values) * 100
        
        display_most_common = 'NaN/Missing' if pd.isna(most_common_value) else repr(most_common_value)
        
        print(f'🏆 Most frequent: {display_most_common} ({most_common_count} times, {most_common_pct:.1f}%)')
        
        # Add separator between columns (except for the last one)
        if i < len(cat_columns):
            print('-' * 50)
    
    print("\n" + "=" * 70)
    print("✅ Categorical visualization complete!")
    
    # Provide actionable insights
    high_cardinality_cols = [col for col in cat_columns if df[col].nunique() > max_unique_values]
    if high_cardinality_cols:
        print(f"\n💡 High cardinality columns detected: {', '.join(high_cardinality_cols)}")
        print("   Consider: grouping rare categories, encoding, or feature engineering")
    
    # Check for columns that might need attention
    mostly_unique_cols = [col for col in cat_columns if df[col].nunique() / len(df) > 0.8]
    if mostly_unique_cols:
        print(f"\n⚠️  Mostly unique columns (>80% unique): {', '.join(mostly_unique_cols)}")
        print("   These might be IDs or need special handling")


def display_column_types(df):
    """
    Display categorical and numerical columns in a DataFrame.
    
    This function separates DataFrame columns into categorical (object dtype) 
    and numerical (non-object dtypes) columns and displays them in a clear format.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to analyze
        
    Returns:
    --------
    dict
        Dictionary containing 'categorical' and 'numerical' lists of column names
        
    Example:
    --------
    >>> import pandas as pd
    >>> from edaflow import display_column_types
    >>> 
    >>> # Create sample data
    >>> data = {
    ...     'name': ['Alice', 'Bob', 'Charlie'],
    ...     'age': [25, 30, 35],
    ...     'city': ['NYC', 'LA', 'Chicago'],
    ...     'salary': [50000, 60000, 70000],
    ...     'is_active': [True, False, True]
    ... }
    >>> df = pd.DataFrame(data)
    >>> 
    >>> # Display column types
    >>> result = display_column_types(df)
    >>> print("Categorical columns:", result['categorical'])
    >>> print("Numerical columns:", result['numerical'])
    """
    import pandas as pd
    
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    if df.empty:
        print("⚠️  DataFrame is empty!")
        return {'categorical': [], 'numerical': []}
    
    # Separate columns by type
    cat_cols = [col for col in df.columns if df[col].dtype == 'object']
    num_cols = [col for col in df.columns if df[col].dtype != 'object']
    
    # Display results
    print("📊 Column Type Analysis")
    print("=" * 50)
    
    print(f"\n📝 Categorical Columns ({len(cat_cols)} total):")
    if cat_cols:
        for i, col in enumerate(cat_cols, 1):
            unique_count = df[col].nunique()
            print(f"   {i:2d}. {col:<20} (unique values: {unique_count})")
    else:
        print("   No categorical columns found")
    
    print(f"\n🔢 Numerical Columns ({len(num_cols)} total):")
    if num_cols:
        for i, col in enumerate(num_cols, 1):
            dtype = str(df[col].dtype)
            print(f"   {i:2d}. {col:<20} (dtype: {dtype})")
    else:
        print("   No numerical columns found")
    
    # Summary
    total_cols = len(df.columns)
    cat_percentage = (len(cat_cols) / total_cols * 100) if total_cols > 0 else 0
    num_percentage = (len(num_cols) / total_cols * 100) if total_cols > 0 else 0
    
    print(f"\n📈 Summary:")
    print(f"   Total columns: {total_cols}")
    print(f"   Categorical: {len(cat_cols)} ({cat_percentage:.1f}%)")
    print(f"   Numerical: {len(num_cols)} ({num_percentage:.1f}%)")
    
    return {
        'categorical': cat_cols,
        'numerical': num_cols
    }


def impute_numerical_median(df, columns=None, inplace=False):
    """
    Impute missing values in numerical columns using median values.
    
    This function identifies numerical columns and fills missing values (NaN) 
    with the median value of each column. It provides detailed reporting of 
    the imputation process and handles edge cases safely.
    
    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing data to impute
    columns : list, optional
        Specific columns to impute. If None, all numerical columns will be processed
    inplace : bool, default False
        If True, modify the original DataFrame. If False, return a new DataFrame
        
    Returns
    -------
    pandas.DataFrame or None
        If inplace=False, returns the DataFrame with imputed values
        If inplace=True, returns None and modifies the original DataFrame
        
    Examples
    --------
    >>> import pandas as pd
    >>> import edaflow
    >>> 
    >>> # Create sample data with missing values
    >>> df = pd.DataFrame({
    ...     'age': [25, None, 35, None, 45],
    ...     'salary': [50000, 60000, None, 70000, None],
    ...     'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
    ... })
    >>> 
    >>> # Impute all numerical columns
    >>> df_imputed = edaflow.impute_numerical_median(df)
    >>> 
    >>> # Impute specific columns only
    >>> df_imputed = edaflow.impute_numerical_median(df, columns=['age'])
    >>> 
    >>> # Impute in place
    >>> edaflow.impute_numerical_median(df, inplace=True)
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    if df.empty:
        print("⚠️  DataFrame is empty. Nothing to impute.")
        return df.copy() if not inplace else None
    
    # Work with copy unless inplace=True
    result_df = df if inplace else df.copy()
    
    # Determine which columns to process
    if columns is None:
        # Get all numerical columns
        numerical_cols = result_df.select_dtypes(include=[np.number]).columns.tolist()
        if not numerical_cols:
            print("⚠️  No numerical columns found in DataFrame.")
            return result_df if not inplace else None
    else:
        # Validate specified columns
        if isinstance(columns, str):
            columns = [columns]
        
        # Check if columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columns not found in DataFrame: {missing_cols}")
        
        # Check if columns are numerical
        non_numerical = [col for col in columns if not pd.api.types.is_numeric_dtype(df[col])]
        if non_numerical:
            raise ValueError(f"Non-numerical columns specified: {non_numerical}")
        
        numerical_cols = columns
    
    print("🔢 Numerical Missing Value Imputation (Median)")
    print("=" * 55)
    
    imputed_columns = []
    total_imputed = 0
    
    for col in numerical_cols:
        missing_count = result_df[col].isnull().sum()
        
        if missing_count == 0:
            print(f"✅ {col:<20} - No missing values")
            continue
        
        # Calculate median (ignoring NaN values)
        median_value = result_df[col].median()
        
        if pd.isna(median_value):
            print(f"⚠️  {col:<20} - All values are missing, skipping")
            continue
        
        # Perform imputation
        result_df[col] = result_df[col].fillna(median_value)
        
        # Track results
        imputed_columns.append(col)
        total_imputed += missing_count
        
        print(f"🔄 {col:<20} - Imputed {missing_count:,} values with median: {median_value}")
    
    # Summary
    print(f"\n📊 Imputation Summary:")
    print(f"   Columns processed: {len(numerical_cols)}")
    print(f"   Columns imputed: {len(imputed_columns)}")
    print(f"   Total values imputed: {total_imputed:,}")
    
    if imputed_columns:
        print(f"   Imputed columns: {', '.join(imputed_columns)}")
    
    return result_df if not inplace else None


def impute_categorical_mode(df, columns=None, inplace=False):
    """
    Impute missing values in categorical columns using mode (most frequent value).
    
    This function identifies categorical columns and fills missing values (NaN) 
    with the mode (most frequent value) of each column. It provides detailed 
    reporting of the imputation process and handles edge cases safely.
    
    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing data to impute
    columns : list, optional
        Specific columns to impute. If None, all categorical columns will be processed
    inplace : bool, default False
        If True, modify the original DataFrame. If False, return a new DataFrame
        
    Returns
    -------
    pandas.DataFrame or None
        If inplace=False, returns the DataFrame with imputed values
        If inplace=True, returns None and modifies the original DataFrame
        
    Examples
    --------
    >>> import pandas as pd
    >>> import edaflow
    >>> 
    >>> # Create sample data with missing values
    >>> df = pd.DataFrame({
    ...     'category': ['A', 'B', 'A', None, 'A'],
    ...     'status': ['Active', None, 'Active', 'Inactive', None],
    ...     'age': [25, 30, 35, 40, 45]
    ... })
    >>> 
    >>> # Impute all categorical columns
    >>> df_imputed = edaflow.impute_categorical_mode(df)
    >>> 
    >>> # Impute specific columns only
    >>> df_imputed = edaflow.impute_categorical_mode(df, columns=['category'])
    >>> 
    >>> # Impute in place
    >>> edaflow.impute_categorical_mode(df, inplace=True)
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    if df.empty:
        print("⚠️  DataFrame is empty. Nothing to impute.")
        return df.copy() if not inplace else None
    
    # Work with copy unless inplace=True
    result_df = df if inplace else df.copy()
    
    # Determine which columns to process
    if columns is None:
        # Get all categorical (object) columns
        categorical_cols = result_df.select_dtypes(include=['object']).columns.tolist()
        if not categorical_cols:
            print("⚠️  No categorical columns found in DataFrame.")
            return result_df if not inplace else None
    else:
        # Validate specified columns
        if isinstance(columns, str):
            columns = [columns]
        
        # Check if columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columns not found in DataFrame: {missing_cols}")
        
        # Check if columns are categorical (object type)
        non_categorical = [col for col in columns if df[col].dtype != 'object']
        if non_categorical:
            print(f"⚠️  Warning: Non-object columns specified: {non_categorical}")
            print("   These will be processed but may not be truly categorical")
        
        categorical_cols = columns
    
    print("📝 Categorical Missing Value Imputation (Mode)")
    print("=" * 55)
    
    imputed_columns = []
    total_imputed = 0
    
    for col in categorical_cols:
        missing_count = result_df[col].isnull().sum()
        
        if missing_count == 0:
            print(f"✅ {col:<20} - No missing values")
            continue
        
        # Calculate mode (most frequent value)
        mode_values = result_df[col].mode()
        
        if len(mode_values) == 0:
            print(f"⚠️  {col:<20} - All values are missing, skipping")
            continue
        
        # Use the first mode value (in case of ties)
        mode_value = mode_values.iloc[0]
        
        # Check for ties in mode
        value_counts = result_df[col].value_counts()
        if len(value_counts) > 1 and value_counts.iloc[0] == value_counts.iloc[1]:
            tie_count = (value_counts == value_counts.iloc[0]).sum()
            print(f"ℹ️  {col:<20} - Mode tie detected ({tie_count} values), using: '{mode_value}'")
        
        # Perform imputation
        result_df[col] = result_df[col].fillna(mode_value)
        
        # Track results
        imputed_columns.append(col)
        total_imputed += missing_count
        
        print(f"🔄 {col:<20} - Imputed {missing_count:,} values with mode: '{mode_value}'")
    
    # Summary
    print(f"\n📊 Imputation Summary:")
    print(f"   Columns processed: {len(categorical_cols)}")
    print(f"   Columns imputed: {len(imputed_columns)}")
    print(f"   Total values imputed: {total_imputed:,}")
    
    if imputed_columns:
        print(f"   Imputed columns: {', '.join(imputed_columns)}")
    
    return None if inplace else result_df


def visualize_numerical_boxplots(df: pd.DataFrame,
                                 columns: Optional[List[str]] = None,
                                 figsize: Optional[tuple] = None,
                                 rows: Optional[int] = None,
                                 cols: Optional[int] = None,
                                 title: str = "Boxplots for Numerical Columns",
                                 show_skewness: bool = True,
                                 orientation: str = 'horizontal',
                                 color_palette: str = 'Set2') -> None:
    """
    Create boxplots for numerical columns to visualize distributions and outliers.
    
    This function automatically detects numerical columns and creates a grid of boxplots
    to help identify outliers, skewness, and distribution characteristics. Each boxplot
    can optionally display the skewness value in the title.
    
    Args:
        df (pd.DataFrame): The input DataFrame to analyze
        columns (Optional[List[str]], optional): Specific columns to plot. If None, 
                                               all numerical columns are used. 
                                               Defaults to None.
        figsize (Optional[tuple], optional): Figure size (width, height). If None, 
                                           automatically calculated based on subplot grid.
                                           Defaults to None.
        rows (Optional[int], optional): Number of rows in subplot grid. If None, 
                                      automatically calculated. Defaults to None.
        cols (Optional[int], optional): Number of columns in subplot grid. If None, 
                                      automatically calculated. Defaults to None.
        title (str, optional): Main title for the entire plot. 
                              Defaults to "Boxplots for Numerical Columns".
        show_skewness (bool, optional): Whether to show skewness values in subplot titles.
                                      Defaults to True.
        orientation (str, optional): Boxplot orientation. Either 'horizontal' or 'vertical'.
                                   Defaults to 'horizontal'.
        color_palette (str, optional): Seaborn color palette to use. 
                                     Defaults to 'Set2'.
    
    Returns:
        None: Displays the boxplot visualization
    
    Raises:
        ValueError: If orientation is not 'horizontal' or 'vertical'
        ValueError: If no numerical columns are found
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> df = pd.DataFrame({
        ...     'age': [25, 30, 35, 40, 100, 28, 32],  # 100 is outlier
        ...     'salary': [50000, 60000, 75000, 80000, 200000, 55000, 65000],  # 200000 is outlier
        ...     'experience': [2, 5, 8, 12, 25, 3, 6],
        ...     'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C']
        ... })
        >>> 
        >>> # Basic boxplot visualization
        >>> edaflow.visualize_numerical_boxplots(df)
        >>> 
        >>> # Custom layout and styling
        >>> edaflow.visualize_numerical_boxplots(df, 
        ...                                     rows=2, cols=2,
        ...                                     title="Custom Boxplots",
        ...                                     orientation='vertical',
        ...                                     color_palette='viridis')
        >>> 
        >>> # Specific columns only
        >>> edaflow.visualize_numerical_boxplots(df, columns=['age', 'salary'])
        >>> 
        >>> # Alternative import style:
        >>> from edaflow.analysis import visualize_numerical_boxplots
        >>> visualize_numerical_boxplots(df, show_skewness=False)
    
    Notes:
        - Automatically identifies numerical columns (int64, float64, etc.)
        - Skips columns with all missing values
        - Outliers are clearly visible as points beyond the whiskers
        - Skewness interpretation:
          * |skewness| < 0.5: Approximately symmetric
          * 0.5 ≤ |skewness| < 1: Moderately skewed  
          * |skewness| ≥ 1: Highly skewed
        - Uses seaborn styling for better visual appearance
    """
    # Validate orientation
    if orientation not in ['horizontal', 'vertical']:
        raise ValueError("orientation must be either 'horizontal' or 'vertical'")
    
    # Get numerical columns
    if columns is None:
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    else:
        # Validate that specified columns exist and are numerical
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columns not found in DataFrame: {missing_cols}")
        
        non_numerical = [col for col in columns if col in df.columns and 
                        not pd.api.types.is_numeric_dtype(df[col])]
        if non_numerical:
            print(f"⚠️  Warning: Skipping non-numerical columns: {non_numerical}")
        
        numerical_cols = [col for col in columns if col in df.columns and 
                         pd.api.types.is_numeric_dtype(df[col])]
    
    # Filter out columns with all missing values
    valid_cols = []
    for col in numerical_cols:
        if not df[col].isna().all():
            valid_cols.append(col)
        else:
            print(f"⚠️  Warning: Skipping column '{col}' - all values are missing")
    
    if not valid_cols:
        raise ValueError("No valid numerical columns found for plotting")
    
    print(f"📊 Creating boxplots for {len(valid_cols)} numerical column(s): {', '.join(valid_cols)}")
    
    # Calculate grid dimensions if not provided
    n_plots = len(valid_cols)
    if rows is None and cols is None:
        cols = min(3, n_plots)  # Default to 3 columns max
        rows = math.ceil(n_plots / cols)
    elif rows is None:
        rows = math.ceil(n_plots / cols)
    elif cols is None:
        cols = math.ceil(n_plots / rows)
    
    # Calculate figure size if not provided
    if figsize is None:
        if orientation == 'horizontal':
            figsize = (4 * cols, 3 * rows)
        else:
            figsize = (3 * cols, 4 * rows)
    
    # Set style
    plt.style.use('default')
    sns.set_palette(color_palette)
    
    # Create the subplot grid
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    fig.suptitle(title, fontsize=16, y=0.98)
    
    # Handle case where there's only one subplot
    if n_plots == 1:
        axes = [axes]
    elif rows == 1 or cols == 1:
        axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
    else:
        axes = axes.flatten()
    
    # Create boxplots
    for i, col in enumerate(valid_cols):
        ax = axes[i]
        
        # Create the boxplot
        if orientation == 'horizontal':
            sns.boxplot(data=df, x=col, ax=ax, orient='h')
            ax.set_xlabel(col)
            ax.set_ylabel('')
        else:
            sns.boxplot(data=df, y=col, ax=ax, orient='v')
            ax.set_ylabel(col)
            ax.set_xlabel('')
        
        # Calculate and display skewness if requested
        if show_skewness:
            skewness = df[col].skew(skipna=True)
            skew_text = f"{col}\nSkewness: {skewness:.2f}"
            ax.set_title(skew_text, fontsize=10)
        else:
            ax.set_title(col, fontsize=10)
        
        # Add grid for better readability
        ax.grid(True, alpha=0.3)
    
    # Hide empty subplots
    for i in range(n_plots, len(axes)):
        axes[i].set_visible(False)
    
    # Adjust layout
    plt.tight_layout()
    
    # Show summary statistics
    print("\n📈 Summary Statistics:")
    print("=" * 50)
    for col in valid_cols:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            skewness = col_data.skew()
            q1, q3 = col_data.quantile([0.25, 0.75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
            
            print(f"📊 {col}:")
            print(f"   Range: {col_data.min():.2f} to {col_data.max():.2f}")
            print(f"   Median: {col_data.median():.2f}")
            print(f"   IQR: {iqr:.2f} (Q1: {q1:.2f}, Q3: {q3:.2f})")
            print(f"   Skewness: {skewness:.2f}", end="")
            
            # Skewness interpretation
            if abs(skewness) < 0.5:
                print(" (approximately symmetric)")
            elif abs(skewness) < 1:
                print(" (moderately skewed)")
            else:
                print(" (highly skewed)")
            
            print(f"   Outliers: {len(outliers)} values outside [{lower_bound:.2f}, {upper_bound:.2f}]")
            if len(outliers) > 0 and len(outliers) <= 5:
                print(f"   Outlier values: {sorted(outliers.tolist())}")
            elif len(outliers) > 5:
                print(f"   Sample outliers: {sorted(outliers.tolist())[:5]}... (+{len(outliers)-5} more)")
            print()
    
    # Display the plot
    plt.show()


def handle_outliers_median(df: pd.DataFrame,
                          columns: Optional[Union[str, List[str]]] = None,
                          method: str = 'iqr',
                          iqr_multiplier: float = 1.5,
                          inplace: bool = False,
                          verbose: bool = True) -> pd.DataFrame:
    """
    Replace outliers in numerical columns with the median value.
    
    This function identifies outliers using statistical methods and replaces them
    with the median value of the respective column. It's designed to work seamlessly
    with the visualize_numerical_boxplots function for a complete outlier workflow.
    
    Args:
        df (pd.DataFrame): The input DataFrame
        columns (Optional[Union[str, List[str]]], optional): Column name(s) to process.
                                                            If None, processes all numerical columns.
                                                            Defaults to None.
        method (str, optional): Method to identify outliers. Options:
                               - 'iqr': Interquartile Range method (Q1 - 1.5*IQR, Q3 + 1.5*IQR)
                               - 'zscore': Z-score method (values with |z-score| > 3)
                               - 'modified_zscore': Modified Z-score using median absolute deviation
                               Defaults to 'iqr'.
        iqr_multiplier (float, optional): Multiplier for IQR method. Defaults to 1.5.
        inplace (bool, optional): If True, modifies the original DataFrame.
                                 If False, returns a new DataFrame. Defaults to False.
        verbose (bool, optional): If True, displays detailed information about
                                 the outlier handling process. Defaults to True.
    
    Returns:
        pd.DataFrame: DataFrame with outliers replaced by median values.
                     If inplace=True, returns the modified original DataFrame.
    
    Raises:
        ValueError: If no valid numerical columns are found or if an invalid method is specified.
        KeyError: If specified column(s) don't exist in the DataFrame.
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> 
        >>> # Create sample data with outliers
        >>> df = pd.DataFrame({
        ...     'A': [1, 2, 3, 4, 5, 100],  # 100 is an outlier
        ...     'B': [10, 20, 30, 40, 50, 60],
        ...     'C': ['x', 'y', 'z', 'x', 'y', 'z']
        ... })
        >>> 
        >>> # First visualize outliers
        >>> edaflow.visualize_numerical_boxplots(df)
        >>> 
        >>> # Then handle outliers
        >>> df_clean = edaflow.handle_outliers_median(df)
        >>> 
        >>> # Or handle specific columns
        >>> df_clean = edaflow.handle_outliers_median(df, columns=['A'])
        >>> 
        >>> # Or modify inplace
        >>> edaflow.handle_outliers_median(df, inplace=True)
        
        # Alternative import style:
        >>> from edaflow.analysis import handle_outliers_median
        >>> df_clean = handle_outliers_median(df, method='zscore')
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    if method not in ['iqr', 'zscore', 'modified_zscore']:
        raise ValueError("Method must be 'iqr', 'zscore', or 'modified_zscore'")
    
    # Handle column selection
    if columns is None:
        # Get all numerical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    elif isinstance(columns, str):
        numerical_cols = [columns]
    else:
        numerical_cols = list(columns)
    
    # Validate columns exist
    missing_cols = [col for col in numerical_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Column(s) not found in DataFrame: {missing_cols}")
    
    # Filter for actual numerical columns
    valid_cols = []
    for col in numerical_cols:
        if df[col].dtype in [np.number] or pd.api.types.is_numeric_dtype(df[col]):
            valid_cols.append(col)
        elif verbose:
            print(f"⚠️  Skipping non-numerical column: {col}")
    
    if not valid_cols:
        raise ValueError("No valid numerical columns found for outlier handling")
    
    # Create working DataFrame
    if inplace:
        result_df = df
    else:
        result_df = df.copy()
    
    if verbose:
        print(f"🔧 Handling outliers in {len(valid_cols)} numerical column(s): {', '.join(valid_cols)}")
        print(f"📊 Method: {method.upper()}")
        if method == 'iqr':
            print(f"📈 IQR Multiplier: {iqr_multiplier}")
        print("=" * 60)
    
    total_outliers_replaced = 0
    
    for col in valid_cols:
        col_data = result_df[col].dropna()
        
        if len(col_data) == 0:
            if verbose:
                print(f"⚠️  {col}: No data available (all NaN)")
            continue
        
        original_outliers = 0
        
        if method == 'iqr':
            # IQR method
            q1, q3 = col_data.quantile([0.25, 0.75])
            iqr = q3 - q1
            lower_bound = q1 - iqr_multiplier * iqr
            upper_bound = q3 + iqr_multiplier * iqr
            outlier_mask = (result_df[col] < lower_bound) | (result_df[col] > upper_bound)
            
        elif method == 'zscore':
            # Z-score method
            mean_val = col_data.mean()
            std_val = col_data.std()
            if std_val == 0:
                outlier_mask = pd.Series([False] * len(result_df), index=result_df.index)
            else:
                z_scores = np.abs((result_df[col] - mean_val) / std_val)
                outlier_mask = z_scores > 3
                
        elif method == 'modified_zscore':
            # Modified Z-score using median absolute deviation
            median_val = col_data.median()
            mad = np.median(np.abs(col_data - median_val))
            if mad == 0:
                outlier_mask = pd.Series([False] * len(result_df), index=result_df.index)
            else:
                modified_z_scores = 0.6745 * (result_df[col] - median_val) / mad
                outlier_mask = np.abs(modified_z_scores) > 3.5
        
        # Count outliers before replacement
        original_outliers = outlier_mask.sum()
        
        if original_outliers > 0:
            # Calculate median for replacement
            median_val = col_data.median()
            
            # Replace outliers with median, ensuring dtype compatibility
            result_df.loc[outlier_mask, col] = result_df[col].dtype.type(median_val)
            total_outliers_replaced += original_outliers
            
            if verbose:
                print(f"📊 {col}:")
                print(f"   🎯 Median value: {median_val:.2f}")
                print(f"   🔄 Outliers replaced: {original_outliers}")
                if method == 'iqr':
                    print(f"   📏 Valid range: [{lower_bound:.2f}, {upper_bound:.2f}]")
                elif method == 'zscore':
                    print(f"   📏 Z-score threshold: ±3.0")
                elif method == 'modified_zscore':
                    print(f"   📏 Modified Z-score threshold: ±3.5")
                print()
        else:
            if verbose:
                print(f"✅ {col}: No outliers detected")
                print()
    
    if verbose:
        print("=" * 60)
        print(f"🎉 Outlier handling completed!")
        print(f"📈 Total outliers replaced: {total_outliers_replaced}")
        print(f"🔧 Method used: {method.upper()}")
        if not inplace:
            print("💾 Original DataFrame unchanged (inplace=False)")
        else:
            print("💾 Original DataFrame modified (inplace=True)")
    
    return result_df


def visualize_interactive_boxplots(df: pd.DataFrame,
                                 columns: Optional[Union[str, List[str]]] = None,
                                 title: str = "Interactive Boxplot Analysis",
                                 height: int = 600,
                                 color_sequence: Optional[List[str]] = None,
                                 show_points: str = "outliers",
                                 verbose: bool = True) -> None:
    """
    Create interactive boxplots for numerical columns using Plotly Express.
    
    This function provides an interactive alternative to matplotlib-based boxplots,
    allowing users to hover, zoom, and explore data distributions dynamically.
    Perfect for final visualization after data cleaning and outlier handling.
    
    Args:
        df (pd.DataFrame): The input DataFrame
        columns (Optional[Union[str, List[str]]], optional): Column name(s) to visualize.
                                                            If None, processes all numerical columns.
                                                            Defaults to None.
        title (str, optional): Title for the interactive plot. Defaults to "Interactive Boxplot Analysis".
        height (int, optional): Height of the plot in pixels. Defaults to 600.
        color_sequence (Optional[List[str]], optional): Custom color sequence for the boxplots.
                                                       If None, uses Plotly's default colors.
                                                       Defaults to None.
        show_points (str, optional): Points to show on boxplots. Options:
                                   - "outliers": Show only outlier points
                                   - "all": Show all data points
                                   - "suspectedoutliers": Show suspected outliers
                                   - False: Show no points
                                   Defaults to "outliers".
        verbose (bool, optional): If True, displays detailed information about
                                 the visualization process. Defaults to True.
    
    Returns:
        None: Displays the interactive plot directly
    
    Raises:
        ValueError: If no valid numerical columns are found.
        KeyError: If specified column(s) don't exist in the DataFrame.
        ImportError: If plotly is not installed.
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> 
        >>> # Create sample data
        >>> df = pd.DataFrame({
        ...     'age': [25, 30, 28, 35, 32, 29, 31, 33],
        ...     'income': [50000, 55000, 48000, 62000, 51000, 45000, 53000, 49000],
        ...     'score': [85, 90, 78, 92, 88, 95, 81, 87],
        ...     'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B']
        ... })
        >>> 
        >>> # Interactive visualization of all numerical columns
        >>> edaflow.visualize_interactive_boxplots(df)
        >>> 
        >>> # Visualize specific columns with custom styling
        >>> edaflow.visualize_interactive_boxplots(
        ...     df, 
        ...     columns=['age', 'income'],
        ...     title="Age and Income Distribution",
        ...     height=500,
        ...     show_points="all"
        ... )
        
        # Alternative import style:
        >>> from edaflow.analysis import visualize_interactive_boxplots
        >>> visualize_interactive_boxplots(df, verbose=True)
    """
    # Check if plotly is available
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        raise ImportError(
            "Plotly is required for interactive boxplots. Install it with: pip install plotly"
        )
    
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    # Handle column selection
    if columns is None:
        # Get all numerical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    elif isinstance(columns, str):
        numerical_cols = [columns]
    else:
        numerical_cols = list(columns)
    
    # Validate columns exist
    missing_cols = [col for col in numerical_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Column(s) not found in DataFrame: {missing_cols}")
    
    # Filter for actual numerical columns
    valid_cols = []
    for col in numerical_cols:
        if df[col].dtype in [np.number] or pd.api.types.is_numeric_dtype(df[col]):
            # Check if column has any non-null values
            if df[col].dropna().empty:
                if verbose:
                    print(f"⚠️  Skipping column with no valid data: {col}")
            else:
                valid_cols.append(col)
        elif verbose:
            print(f"⚠️  Skipping non-numerical column: {col}")
    
    if not valid_cols:
        raise ValueError("No valid numerical columns found for interactive visualization")
    
    if verbose:
        print(f"📊 Creating interactive boxplots for {len(valid_cols)} numerical column(s): {', '.join(valid_cols)}")
        print(f"🎨 Plot configuration: {height}px height, showing {show_points} points")
    
    # Prepare data for plotting
    # Create a melted dataframe for easier plotting with px.box
    plot_data = df[valid_cols].copy()
    
    # Melt the dataframe to long format for plotly
    melted_data = plot_data.melt(var_name='Variable', value_name='Value')
    
    # Set up color sequence
    if color_sequence is None:
        color_sequence = px.colors.qualitative.Set2
    
    # Create the interactive boxplot
    fig = px.box(
        melted_data, 
        x='Variable', 
        y='Value',
        title=title,
        color='Variable',
        color_discrete_sequence=color_sequence,
        points=show_points,
        hover_data={'Variable': False}  # Don't show variable name in hover (redundant)
    )
    
    # Customize the layout
    fig.update_layout(
        height=height,
        showlegend=False,  # Hide legend since x-axis already shows variable names
        xaxis_title="Variables",
        yaxis_title="Values",
        hovermode='closest',
        template='plotly_white'
    )
    
    # Improve hover information
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>' +
                     'Value: %{y}<br>' +
                     '<extra></extra>'  # Remove the trace box
    )
    
    # Add some styling improvements
    fig.update_xaxes(
        tickangle=45 if len(valid_cols) > 5 else 0,
        title_font_size=14
    )
    fig.update_yaxes(title_font_size=14)
    
    # Display summary statistics if verbose
    if verbose:
        print("\n📈 Interactive Boxplot Summary:")
        print("=" * 50)
        for col in valid_cols:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                q1, q3 = col_data.quantile([0.25, 0.75])
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
                
                print(f"📊 {col}:")
                print(f"   📏 Range: {col_data.min():.2f} to {col_data.max():.2f}")
                print(f"   📍 Median: {col_data.median():.2f}")
                print(f"   📦 IQR: {iqr:.2f} (Q1: {q1:.2f}, Q3: {q3:.2f})")
                print(f"   🎯 Outliers: {len(outliers)} values")
                print()
        
        print("🖱️  Interactive Features:")
        print("   • Hover over points to see exact values")
        print("   • Click and drag to zoom into specific regions")
        print("   • Double-click to reset zoom")
        print("   • Use the toolbar to pan, select, and download the plot")
        print()
    
    # Show the interactive plot
    fig.show()
    
    if verbose:
        print("✅ Interactive boxplot visualization completed!")
        print("🎉 Use the interactive features to explore your data distributions!")


def visualize_heatmap(df: pd.DataFrame,
                     heatmap_type: str = "correlation",
                     columns: Optional[Union[str, List[str]]] = None,
                     title: Optional[str] = None,
                     figsize: Optional[tuple] = None,
                     cmap: str = "RdYlBu_r",
                     annot: bool = True,
                     fmt: str = ".2f",
                     square: bool = True,
                     linewidths: float = 0.5,
                     cbar_kws: Optional[dict] = None,
                     method: str = "pearson",
                     missing_threshold: float = 5.0,
                     verbose: bool = True) -> None:
    """
    Create comprehensive heatmap visualizations for exploratory data analysis.
    
    This function provides multiple types of heatmaps for different EDA purposes:
    - Correlation heatmaps for numerical relationships
    - Missing data pattern heatmaps
    - Numerical data value heatmaps
    - Cross-tabulation heatmaps for categorical relationships
    
    Args:
        df (pd.DataFrame): The input DataFrame
        heatmap_type (str, optional): Type of heatmap to create. Options:
                                    - "correlation": Correlation matrix heatmap (default)
                                    - "missing": Missing data pattern heatmap
                                    - "values": Raw data values heatmap (for small datasets)
                                    - "crosstab": Cross-tabulation heatmap for categorical data
                                    Defaults to "correlation".
        columns (Optional[Union[str, List[str]]], optional): Column name(s) to include.
                                                            If None, uses appropriate columns based on heatmap_type.
                                                            Defaults to None.
        title (Optional[str], optional): Custom title for the heatmap. If None, auto-generated.
                                        Defaults to None.
        figsize (Optional[tuple], optional): Figure size (width, height). If None, auto-calculated.
                                           Defaults to None.
        cmap (str, optional): Colormap for the heatmap. Defaults to "RdYlBu_r".
        annot (bool, optional): Whether to annotate cells with values. Defaults to True.
        fmt (str, optional): String formatting code for annotations. Defaults to ".2f".
        square (bool, optional): Whether to make cells square-shaped. Defaults to True.
        linewidths (float, optional): Width of lines separating cells. Defaults to 0.5.
        cbar_kws (Optional[dict], optional): Keyword arguments for colorbar. Defaults to None.
        method (str, optional): Correlation method for correlation heatmaps.
                               Options: "pearson", "kendall", "spearman". Defaults to "pearson".
        missing_threshold (float, optional): Threshold for missing data highlighting (%).
                                            Only used for missing data heatmaps. Defaults to 5.0.
        verbose (bool, optional): If True, displays detailed information about
                                 the heatmap creation process. Defaults to True.
    
    Returns:
        None: Displays the heatmap visualization
    
    Raises:
        ValueError: If heatmap_type is not supported or no suitable data found.
        KeyError: If specified column(s) don't exist in the DataFrame.
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> 
        >>> # Create sample data
        >>> df = pd.DataFrame({
        ...     'age': [25, 30, 28, 35, 32, 29, 31, 33],
        ...     'income': [50000, 55000, 48000, 62000, 51000, 45000, 53000, 49000],
        ...     'score': [85, 90, 78, 92, 88, 95, 81, 87],
        ...     'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B']
        ... })
        >>> 
        >>> # Correlation heatmap (default)
        >>> edaflow.visualize_heatmap(df)
        >>> 
        >>> # Missing data pattern heatmap
        >>> edaflow.visualize_heatmap(df, heatmap_type="missing")
        >>> 
        >>> # Custom styling
        >>> edaflow.visualize_heatmap(
        ...     df, 
        ...     heatmap_type="correlation",
        ...     method="spearman",
        ...     cmap="viridis",
        ...     title="Spearman Correlation Analysis"
        ... )
    """
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    if verbose:
        print(f"🔥 Creating {heatmap_type} heatmap...")
        print("=" * 50)
    
    # Handle column selection
    if columns is not None:
        if isinstance(columns, str):
            columns = [columns]
        
        # Validate columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Column(s) not found in DataFrame: {missing_cols}")
        
        df_subset = df[columns].copy()
    else:
        df_subset = df.copy()
    
    # Create heatmap based on type
    if heatmap_type == "correlation":
        # Get numerical columns only
        numerical_cols = df_subset.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numerical_cols) < 2:
            raise ValueError("At least 2 numerical columns required for correlation heatmap")
        
        if verbose:
            print(f"📊 Creating correlation matrix for {len(numerical_cols)} numerical columns")
            print(f"📈 Using {method} correlation method")
            print(f"🔢 Columns: {', '.join(numerical_cols)}")
        
        # Calculate correlation matrix
        df_plot = df_subset[numerical_cols]
        corr_matrix = df_plot.corr(method=method)
        
        # Auto-generate title if not provided
        if title is None:
            title = f"{method.capitalize()} Correlation Matrix"
        
        # Set up figure size
        if figsize is None:
            n_cols = len(numerical_cols)
            figsize = (max(8, n_cols * 0.8), max(6, n_cols * 0.7))
        
        # Create the plot
        plt.figure(figsize=figsize)
        
        # Create heatmap
        sns.heatmap(
            corr_matrix,
            annot=annot,
            cmap=cmap,
            fmt=fmt,
            square=square,
            linewidths=linewidths,
            cbar_kws=cbar_kws or {"shrink": 0.8},
            vmin=-1,
            vmax=1,
            center=0
        )
        
        if verbose:
            # Display correlation insights
            print(f"\n📈 Correlation Analysis Summary:")
            print("=" * 40)
            
            # Find strongest positive and negative correlations
            corr_values = corr_matrix.values
            np.fill_diagonal(corr_values, np.nan)  # Remove self-correlations
            
            # Get indices of max/min correlations
            max_idx = np.unravel_index(np.nanargmax(corr_values), corr_values.shape)
            min_idx = np.unravel_index(np.nanargmin(corr_values), corr_values.shape)
            
            max_corr = corr_values[max_idx]
            min_corr = corr_values[min_idx]
            
            max_pair = (corr_matrix.index[max_idx[0]], corr_matrix.columns[max_idx[1]])
            min_pair = (corr_matrix.index[min_idx[0]], corr_matrix.columns[min_idx[1]])
            
            print(f"🔺 Strongest positive correlation: {max_pair[0]} ↔ {max_pair[1]} ({max_corr:.3f})")
            print(f"🔻 Strongest negative correlation: {min_pair[0]} ↔ {min_pair[1]} ({min_corr:.3f})")
            
            # Count strong correlations
            strong_positive = np.sum((corr_values > 0.7) & (corr_values < 1.0))
            strong_negative = np.sum(corr_values < -0.7)
            
            print(f"💪 Strong positive correlations (>0.7): {strong_positive}")
            print(f"💪 Strong negative correlations (<-0.7): {strong_negative}")
    
    elif heatmap_type == "missing":
        if verbose:
            print(f"🕳️  Creating missing data pattern heatmap")
            print(f"⚠️  Highlighting missing values > {missing_threshold}%")
        
        # Calculate missing data percentages
        missing_percent = (df_subset.isnull().sum() / len(df_subset) * 100)
        missing_data = pd.DataFrame({
            'Column': missing_percent.index,
            'Missing_Percentage': missing_percent.values
        })
        
        # Create missing data matrix for visualization
        missing_matrix = df_subset.isnull().astype(int)
        
        # Auto-generate title if not provided
        if title is None:
            title = "Missing Data Pattern Analysis"
        
        # Set up figure size
        if figsize is None:
            n_cols = len(df_subset.columns)
            n_rows = min(50, len(df_subset))  # Limit rows for readability
            figsize = (max(10, n_cols * 0.5), max(6, n_rows * 0.1))
        
        # Create the plot
        plt.figure(figsize=figsize)
        
        # Use a subset of rows if dataset is too large
        if len(df_subset) > 100:
            sample_size = min(100, len(df_subset))
            missing_sample = missing_matrix.sample(n=sample_size, random_state=42)
            if verbose:
                print(f"📊 Showing sample of {sample_size} rows (dataset has {len(df_subset)} rows)")
        else:
            missing_sample = missing_matrix
        
        # Create heatmap
        sns.heatmap(
            missing_sample.T,  # Transpose to show columns on y-axis
            cmap=['lightblue', 'red'],
            cbar_kws={'label': 'Missing Data (1) vs Present Data (0)'},
            yticklabels=True,
            xticklabels=False,
            linewidths=0.1
        )
        
        plt.ylabel("Columns")
        plt.xlabel("Sample Rows")
        
        if verbose:
            print(f"\n🕳️  Missing Data Summary:")
            print("=" * 40)
            for col in missing_percent.index:
                pct = missing_percent[col]
                if pct > 0:
                    status = "🔴 HIGH" if pct > missing_threshold * 2 else "🟡 MEDIUM" if pct > missing_threshold else "🟢 LOW"
                    print(f"{status}: {col} - {pct:.1f}% missing")
            
            total_missing = df_subset.isnull().sum().sum()
            total_values = df_subset.size
            overall_pct = (total_missing / total_values) * 100
            print(f"\n📊 Overall missing data: {overall_pct:.1f}% ({total_missing:,} / {total_values:,} values)")
    
    elif heatmap_type == "values":
        if verbose:
            print(f"🔢 Creating data values heatmap")
            print(f"⚠️  Best for small datasets (showing first 50 rows max)")
        
        # Get numerical columns only
        numerical_cols = df_subset.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numerical_cols) == 0:
            raise ValueError("No numerical columns found for values heatmap")
        
        df_plot = df_subset[numerical_cols]
        
        # Limit rows for readability
        if len(df_plot) > 50:
            df_plot = df_plot.head(50)
            if verbose:
                print(f"📊 Showing first 50 rows (dataset has {len(df_subset)} rows)")
        
        # Auto-generate title if not provided
        if title is None:
            title = "Data Values Heatmap"
        
        # Set up figure size
        if figsize is None:
            n_cols = len(numerical_cols)
            n_rows = len(df_plot)
            figsize = (max(10, n_cols * 0.8), max(8, n_rows * 0.3))
        
        # Create the plot
        plt.figure(figsize=figsize)
        
        # Normalize data for better visualization
        df_normalized = (df_plot - df_plot.min()) / (df_plot.max() - df_plot.min())
        
        # Create heatmap
        sns.heatmap(
            df_normalized,
            annot=annot,
            cmap=cmap,
            fmt=fmt,
            linewidths=linewidths,
            cbar_kws=cbar_kws or {"shrink": 0.8, "label": "Normalized Values (0-1)"},
            yticklabels=True,
            xticklabels=True
        )
        
        plt.ylabel("Rows")
        plt.xlabel("Columns")
        
        if verbose:
            print(f"\n🔢 Values Heatmap Summary:")
            print("=" * 40)
            print(f"📊 Columns included: {', '.join(numerical_cols)}")
            print(f"📏 Data range (original):")
            for col in numerical_cols:
                col_min, col_max = df_plot[col].min(), df_plot[col].max()
                print(f"   {col}: {col_min:.2f} to {col_max:.2f}")
    
    elif heatmap_type == "crosstab":
        # Get categorical columns
        categorical_cols = df_subset.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if len(categorical_cols) < 2:
            raise ValueError("At least 2 categorical columns required for crosstab heatmap")
        
        if verbose:
            print(f"📊 Creating cross-tabulation heatmap")
            print(f"📈 Using first 2 categorical columns: {categorical_cols[:2]}")
        
        # Use first two categorical columns
        col1, col2 = categorical_cols[0], categorical_cols[1]
        
        # Create cross-tabulation
        crosstab = pd.crosstab(df_subset[col1], df_subset[col2])
        
        # Auto-generate title if not provided
        if title is None:
            title = f"Cross-tabulation: {col1} vs {col2}"
        
        # Set up figure size
        if figsize is None:
            figsize = (max(8, len(crosstab.columns) * 0.8), max(6, len(crosstab.index) * 0.5))
        
        # Create the plot
        plt.figure(figsize=figsize)
        
        # Create heatmap
        sns.heatmap(
            crosstab,
            annot=annot,
            cmap=cmap,
            fmt='d' if annot else fmt,
            square=square,
            linewidths=linewidths,
            cbar_kws=cbar_kws or {"shrink": 0.8, "label": "Count"}
        )
        
        plt.ylabel(col1)
        plt.xlabel(col2)
        
        if verbose:
            print(f"\n📊 Cross-tabulation Summary:")
            print("=" * 40)
            print(f"📈 {col1} categories: {len(crosstab.index)}")
            print(f"📈 {col2} categories: {len(crosstab.columns)}")
            print(f"📊 Total combinations: {crosstab.size}")
            print(f"🔢 Total observations: {crosstab.sum().sum()}")
    
    else:
        raise ValueError(f"Unsupported heatmap_type: {heatmap_type}. "
                        f"Supported types: 'correlation', 'missing', 'values', 'crosstab'")
    
    # Apply title and styling
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    if verbose:
        print(f"\n✅ {heatmap_type.capitalize()} heatmap created successfully!")
        print("🎨 Use plt.show() to display the plot")
        print("💾 Use plt.savefig('filename.png') to save")
    
    # Show the plot
    plt.show()


def visualize_histograms(df: pd.DataFrame,
                        columns: Optional[Union[str, List[str]]] = None,
                        title: Optional[str] = None,
                        figsize: Optional[tuple] = None,
                        bins: Union[int, str] = 'auto',
                        kde: bool = True,
                        show_stats: bool = True,
                        show_normal_curve: bool = True,
                        color_palette: str = 'Set2',
                        alpha: float = 0.7,
                        grid_alpha: float = 0.3,
                        rows: Optional[int] = None,
                        cols: Optional[int] = None,
                        statistical_tests: bool = True,
                        verbose: bool = True) -> None:
    """
    Create comprehensive histogram visualizations with distribution analysis and skewness detection.
    
    This function provides detailed histogram analysis for numerical columns, including:
    - Distribution shape visualization with histograms and KDE curves
    - Skewness and kurtosis analysis with interpretation
    - Normal distribution comparison overlay
    - Statistical tests for normality (Shapiro-Wilk, Anderson-Darling)
    - Comprehensive distribution statistics and insights
    
    Args:
        df (pd.DataFrame): The input DataFrame
        columns (Optional[Union[str, List[str]]], optional): Column name(s) to visualize.
                                                            If None, processes all numerical columns.
                                                            Defaults to None.
        title (Optional[str], optional): Main title for the entire plot. If None, auto-generated.
                                        Defaults to None.
        figsize (Optional[tuple], optional): Figure size (width, height). If None, auto-calculated.
                                           Defaults to None.
        bins (Union[int, str], optional): Number of bins or binning strategy.
                                         Options: int, 'auto', 'sturges', 'fd', 'scott', 'sqrt'.
                                         Defaults to 'auto'.
        kde (bool, optional): Whether to show Kernel Density Estimation curve. Defaults to True.
        show_stats (bool, optional): Whether to display statistics on each subplot. Defaults to True.
        show_normal_curve (bool, optional): Whether to overlay normal distribution curve. Defaults to True.
        color_palette (str, optional): Seaborn color palette. Defaults to 'Set2'.
        alpha (float, optional): Transparency of histogram bars (0-1). Defaults to 0.7.
        grid_alpha (float, optional): Transparency of grid lines (0-1). Defaults to 0.3.
        rows (Optional[int], optional): Number of rows in subplot grid. If None, auto-calculated.
                                      Defaults to None.
        cols (Optional[int], optional): Number of columns in subplot grid. If None, auto-calculated.
                                      Defaults to None.
        statistical_tests (bool, optional): Whether to run normality tests (Shapiro-Wilk, etc.).
                                          Defaults to True.
        verbose (bool, optional): If True, displays detailed distribution analysis.
                                 Defaults to True.
    
    Returns:
        None: Displays the histogram visualization
    
    Raises:
        ValueError: If no numerical columns are found or DataFrame is empty.
        KeyError: If specified column(s) don't exist in the DataFrame.
    
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> import edaflow
        >>> 
        >>> # Create sample data with different distributions
        >>> np.random.seed(42)
        >>> df = pd.DataFrame({
        ...     'normal': np.random.normal(100, 15, 1000),
        ...     'skewed_right': np.random.exponential(2, 1000),
        ...     'skewed_left': 10 - np.random.exponential(2, 1000),
        ...     'uniform': np.random.uniform(0, 100, 1000)
        ... })
        >>> 
        >>> # Basic histogram analysis
        >>> edaflow.visualize_histograms(df)
        >>> 
        >>> # Custom analysis with specific columns
        >>> edaflow.visualize_histograms(
        ...     df,
        ...     columns=['normal', 'skewed_right'],
        ...     bins=30,
        ...     show_normal_curve=True,
        ...     statistical_tests=True
        ... )
        >>> 
        >>> # Detailed styling
        >>> edaflow.visualize_histograms(
        ...     df,
        ...     title="Distribution Analysis Dashboard",
        ...     color_palette='viridis',
        ...     alpha=0.8,
        ...     figsize=(15, 10)
        ... )
    """
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    # Handle column selection
    if columns is not None:
        if isinstance(columns, str):
            columns = [columns]
        
        # Validate columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Column(s) not found in DataFrame: {missing_cols}")
        
        numerical_cols = [col for col in columns if col in df.select_dtypes(include=[np.number]).columns]
    else:
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numerical_cols) == 0:
        raise ValueError("No numerical columns found for histogram visualization")
    
    if verbose:
        print("📊 Creating histogram distribution analysis...")
        print("=" * 60)
        print(f"🔢 Analyzing {len(numerical_cols)} numerical column(s): {', '.join(numerical_cols)}")
        print(f"📈 Features: KDE={kde}, Normal Curve={show_normal_curve}, Stats={show_stats}")
        if statistical_tests:
            print("🧪 Statistical normality tests will be performed")
    
    # Calculate subplot grid
    n_cols = len(numerical_cols)
    if rows is None and cols is None:
        cols = min(3, n_cols)
        rows = math.ceil(n_cols / cols)
    elif rows is None:
        rows = math.ceil(n_cols / cols)
    elif cols is None:
        cols = math.ceil(n_cols / rows)
    
    # Set figure size
    if figsize is None:
        width = cols * 5
        height = rows * 4
        figsize = (width, height)
    
    # Auto-generate title
    if title is None:
        title = f"Distribution Analysis - Histograms with Skewness Detection ({n_cols} columns)"
    
    # Set up the plot
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
    
    # Handle single subplot case
    if n_cols == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    # Get colors from palette
    colors = sns.color_palette(color_palette, n_cols)
    
    # Statistical summaries for verbose output
    distribution_stats = {}
    
    # Create histograms
    for idx, col in enumerate(numerical_cols):
        ax = axes[idx]
        data = df[col].dropna()
        
        if len(data) == 0:
            ax.text(0.5, 0.5, f"No data available\nfor {col}", 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title(col, fontweight='bold')
            continue
        
        # Calculate statistics
        mean = data.mean()
        median = data.median()
        std = data.std()
        skewness = data.skew()
        kurt = data.kurtosis()
        
        # Store stats for verbose output
        distribution_stats[col] = {
            'mean': mean,
            'median': median,
            'std': std,
            'skewness': skewness,
            'kurtosis': kurt,
            'min': data.min(),
            'max': data.max(),
            'count': len(data)
        }
        
        # Statistical tests
        normality_tests = {}
        if statistical_tests and len(data) >= 3:
            try:
                from scipy import stats
                
                # Shapiro-Wilk test (best for small samples)
                if len(data) <= 5000:  # Limit for computational efficiency
                    shapiro_stat, shapiro_p = stats.shapiro(data.sample(min(5000, len(data)), random_state=42))
                    normality_tests['shapiro'] = {'statistic': shapiro_stat, 'p_value': shapiro_p}
                
                # Anderson-Darling test
                anderson_result = stats.anderson(data, dist='norm')
                normality_tests['anderson'] = {
                    'statistic': anderson_result.statistic,
                    'critical_values': anderson_result.critical_values,
                    'significance_level': anderson_result.significance_level
                }
                
                # Jarque-Bera test
                jb_stat, jb_p = stats.jarque_bera(data)
                normality_tests['jarque_bera'] = {'statistic': jb_stat, 'p_value': jb_p}
                
            except ImportError:
                if verbose:
                    print("⚠️  scipy not available - skipping statistical tests")
                statistical_tests = False
        
        # Create main histogram
        n, bins_used, patches = ax.hist(data, bins=bins, alpha=alpha, color=colors[idx], 
                                       edgecolor='black', linewidth=0.5, density=True)
        
        # Add KDE curve
        if kde:
            try:
                sns.kdeplot(data=data, ax=ax, color='darkred', linewidth=2, alpha=0.8)
            except Exception:
                pass  # Skip KDE if it fails
        
        # Add normal distribution overlay
        if show_normal_curve:
            x_norm = np.linspace(data.min(), data.max(), 100)
            normal_curve = stats.norm.pdf(x_norm, mean, std)
            ax.plot(x_norm, normal_curve, 'g--', linewidth=2, alpha=0.8, 
                   label=f'Normal(μ={mean:.1f}, σ={std:.1f})')
        
        # Add vertical lines for mean and median
        ax.axvline(mean, color='red', linestyle='--', alpha=0.8, linewidth=2, label=f'Mean: {mean:.2f}')
        ax.axvline(median, color='blue', linestyle='--', alpha=0.8, linewidth=2, label=f'Median: {median:.2f}')
        
        # Interpret skewness
        if abs(skewness) < 0.5:
            skew_interpretation = "Approximately Normal"
            skew_color = 'green'
        elif abs(skewness) < 1:
            skew_interpretation = "Moderately Skewed"
            skew_color = 'orange'
        else:
            skew_interpretation = "Highly Skewed"
            skew_color = 'red'
        
        # Determine skew direction
        if skewness > 0:
            skew_direction = "Right (Positive)"
        elif skewness < 0:
            skew_direction = "Left (Negative)"
        else:
            skew_direction = "Symmetric"
        
        # Add statistics text box
        if show_stats:
            stats_text = f"n = {len(data):,}\n"
            stats_text += f"Mean = {mean:.2f}\n" 
            stats_text += f"Std = {std:.2f}\n"
            stats_text += f"Skewness = {skewness:.3f}\n"
            stats_text += f"Kurtosis = {kurt:.3f}\n"
            stats_text += f"Shape: {skew_interpretation}"
            
            # Add statistical test results
            if statistical_tests and normality_tests:
                stats_text += "\n\nNormality Tests:"
                if 'shapiro' in normality_tests:
                    p_val = normality_tests['shapiro']['p_value']
                    result = "Normal" if p_val > 0.05 else "Non-Normal"
                    stats_text += f"\nShapiro: {result}"
                    stats_text += f"\n(p={p_val:.4f})"
            
            # Position stats box
            ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
                   verticalalignment='top', horizontalalignment='right',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Customize subplot
        ax.set_title(f"{col}\nSkew: {skewness:.3f} ({skew_direction})", 
                    fontweight='bold', color=skew_color)
        ax.grid(True, alpha=grid_alpha)
        ax.set_xlabel('Value')
        ax.set_ylabel('Density')
        
        # Add legend if normal curve is shown
        if show_normal_curve or True:  # Always show legend for mean/median
            ax.legend(loc='upper left', fontsize=8, framealpha=0.8)
    
    # Hide unused subplots
    for idx in range(n_cols, len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    
    # Verbose statistical analysis
    if verbose:
        print(f"\n📈 Distribution Analysis Summary:")
        print("=" * 60)
        
        for col, stats in distribution_stats.items():
            print(f"\n🔢 {col}:")
            print(f"   📊 Basic Stats: μ={stats['mean']:.2f}, σ={stats['std']:.2f}, median={stats['median']:.2f}")
            print(f"   📏 Range: {stats['min']:.2f} to {stats['max']:.2f}")
            print(f"   📈 Sample Size: {stats['count']:,} observations")
            
            # Skewness interpretation
            skew = stats['skewness']
            if abs(skew) < 0.5:
                skew_desc = "🟢 NORMAL - Approximately symmetric distribution"
            elif abs(skew) < 1:
                direction = "right (positive)" if skew > 0 else "left (negative)"
                skew_desc = f"🟡 MODERATE - Moderately skewed {direction}"
            else:
                direction = "right (positive)" if skew > 0 else "left (negative)"
                skew_desc = f"🔴 HIGH - Highly skewed {direction}"
            
            print(f"   ⚖️  Skewness: {skew:.3f} - {skew_desc}")
            
            # Kurtosis interpretation  
            kurt = stats['kurtosis']
            if abs(kurt) < 0.5:
                kurt_desc = "🟢 NORMAL - Normal tail behavior (mesokurtic)"
            elif kurt > 0.5:
                kurt_desc = "🔺 HEAVY - Heavy tails, more outliers (leptokurtic)"
            else:
                kurt_desc = "🔻 LIGHT - Light tails, fewer outliers (platykurtic)" 
            
            print(f"   📊 Kurtosis: {kurt:.3f} - {kurt_desc}")
            
            # Statistical test results
            if statistical_tests and len(df[col].dropna()) >= 3:
                print(f"   🧪 Normality Assessment:")
                data_sample = df[col].dropna()
                
                try:
                    from scipy import stats
                    
                    # Shapiro-Wilk
                    if len(data_sample) <= 5000:
                        test_data = data_sample.sample(min(5000, len(data_sample)), random_state=42)
                        shapiro_stat, shapiro_p = stats.shapiro(test_data)
                        normality = "✅ Likely Normal" if shapiro_p > 0.05 else "❌ Non-Normal"
                        print(f"      Shapiro-Wilk: {normality} (p={shapiro_p:.4f})")
                    
                    # Jarque-Bera
                    jb_stat, jb_p = stats.jarque_bera(data_sample)
                    jb_normality = "✅ Likely Normal" if jb_p > 0.05 else "❌ Non-Normal"
                    print(f"      Jarque-Bera: {jb_normality} (p={jb_p:.4f})")
                    
                except ImportError:
                    print("      ⚠️  Install scipy for normality tests")
        
        # Overall summary
        total_normal = sum(1 for stats in distribution_stats.values() if abs(stats['skewness']) < 0.5)
        total_moderate = sum(1 for stats in distribution_stats.values() if 0.5 <= abs(stats['skewness']) < 1)
        total_high = sum(1 for stats in distribution_stats.values() if abs(stats['skewness']) >= 1)
        
        print(f"\n🎯 Overall Distribution Summary:")
        print("=" * 40)
        print(f"🟢 Normal/Symmetric: {total_normal}/{len(numerical_cols)} columns")
        print(f"🟡 Moderately Skewed: {total_moderate}/{len(numerical_cols)} columns")
        print(f"🔴 Highly Skewed: {total_high}/{len(numerical_cols)} columns")
        
        if total_high > 0:
            print(f"\n💡 Recommendation: Consider data transformation for highly skewed columns")
            print("   📈 Right skew: Try log, sqrt, or Box-Cox transformation")
            print("   📉 Left skew: Try square, exponential, or reflect + transform")
        
        print(f"\n✅ Histogram analysis completed!")
        print("🎨 Use plt.show() to display the plot")
        print("💾 Use plt.savefig('filename.png') to save")
    
    # Show the plot
    plt.show()

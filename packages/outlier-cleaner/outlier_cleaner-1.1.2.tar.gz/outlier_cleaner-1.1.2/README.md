# OutlierCleaner

A Python package for detecting and removing outliers in data using various statistical methods and advanced distribution analysis.

## Features

- **Type Safety**: Comprehensive type hints for enhanced IDE support and code reliability
- Automatic method selection based on data distribution
- Multiple outlier detection methods:
  - IQR (Interquartile Range)
  - Z-score
  - Modified Z-score (robust to non-normal distributions)
- Advanced distribution analysis and method recommendations
- Comprehensive visualization tools:
  - Standalone plotting functions (scatter, distribution, box, Q-Q plots)
  - Integrated analysis plots with 2x2 dashboard view
  - Distribution visualization with KDE
  - Box plots with outlier highlighting
  - Q-Q plots for normality assessment
  - Combined analysis dashboard
- Progress tracking for batch operations
- Index preservation options
- Outlier tracking and statistics
- Method comparison and agreement analysis
- Robust handling of edge cases (zero MAD, constant columns)

## Installation

```bash
pip install outlier-cleaner
```

## Usage

### Basic Usage

```python
import pandas as pd
from outlier_cleaner import OutlierCleaner, plot_outliers, plot_distribution

# Create or load your DataFrame
df = pd.DataFrame({'column1': [1, 2, 3, 100, 4, 5, 6]})

# Using standalone visualization functions
outliers = [False, False, False, True, False, False, False]
plot_outliers(df['column1'], outliers)
plot_distribution(df['column1'], outliers)

# Using OutlierCleaner
cleaner = OutlierCleaner(df)

# Generate comprehensive analysis plots for all numeric columns
figures = cleaner.plot_outlier_analysis()

# Or analyze specific columns
figures = cleaner.plot_outlier_analysis(['column1'])

# Clean the data
cleaned_df, info = cleaner.clean_columns(['column1'], method='auto')
```

### Advanced Example

Here's a comprehensive example using the California Housing dataset:

```python
import pandas as pd
from sklearn.datasets import fetch_california_housing
from outlier_cleaner import OutlierCleaner, plot_outliers, plot_distribution

# Load California Housing dataset
housing = fetch_california_housing()
df = pd.DataFrame(housing.data, columns=housing.feature_names)
df['PRICE'] = housing.target

# Initialize cleaner with index preservation
cleaner = OutlierCleaner(df, preserve_index=True)

# Analyze distributions and get method recommendations
for column in ['MedInc', 'AveRooms', 'PRICE']:
    analysis = cleaner.analyze_distribution(column)
    print(f"\n{column} Analysis:")
    print(f"- Skewness: {analysis['skewness']:.2f}")
    print(f"- Recommended method: {analysis['recommended_method']}")

# Get outlier statistics
stats = cleaner.get_outlier_stats(['MedInc', 'AveRooms', 'PRICE'])
print(f"\nPotential outliers in MedInc: {stats.loc[stats['Column'] == 'MedInc', 'Potential Outliers'].values[0]}")

# Clean data with automatic method selection
cleaned_df, info = cleaner.clean_columns(
    columns=['MedInc', 'AveRooms', 'PRICE'],
    method='auto',
    show_progress=True
)

# Get outlier indices
outliers = cleaner.get_outlier_indices('MedInc')
print(f"\nOutlier indices for MedInc: {outliers['MedInc'][:5]}")

# Generate comprehensive analysis plots
figures = cleaner.plot_outlier_analysis(['MedInc', 'AveRooms', 'PRICE'])

# Compare methods
comparison = cleaner.compare_methods(['MedInc', 'PRICE'])
print(comparison['MedInc']['summary'])
```

## Visualization Tools

### Standalone Functions

#### plot_outliers(data, outliers)
Create a scatter plot highlighting outliers in the data.
- Blue points: Normal data points
- Red points: Outlier points
- Customizable figure size and title

```python
from outlier_cleaner import plot_outliers
plot_outliers(data=df['column'], outliers=outlier_mask, title='My Data')
```

#### plot_distribution(data, outliers)
Plot the distribution of data with optional outlier highlighting.
- Shows kernel density estimation (KDE)
- Separate distributions for normal and outlier points
- Customizable figure size and title

```python
from outlier_cleaner import plot_distribution
plot_distribution(data=df['column'], outliers=outlier_mask)
```

#### plot_boxplot(data, outliers)
Create a box plot with optional outlier highlighting.
- Shows quartiles, median, and whiskers
- Highlights outliers in red
- Customizable figure size and title

```python
from outlier_cleaner import plot_boxplot
plot_boxplot(data=df['column'], outliers=outlier_mask)
```

#### plot_qq(data, outliers)
Create a Q-Q plot to assess normality of the data distribution.
- Compares data quantiles against theoretical normal distribution
- Highlights outliers in red
- Helps identify deviations from normality

```python
from outlier_cleaner import plot_qq
plot_qq(data=df['column'], outliers=outlier_mask)
```

#### plot_outlier_analysis(data, outliers)
Generate a comprehensive 2x2 dashboard combining all plots.
- Scatter plot with outliers (top-left)
- Distribution plot (top-right)
- Box plot (bottom-left)
- Q-Q plot (bottom-right)
- Automatic layout adjustment

```python
from outlier_cleaner import plot_outlier_analysis
plot_outlier_analysis(data=df['column'], outliers=outlier_mask)
```

### Integrated Analysis Plots

#### plot_outlier_analysis(columns=None)
Generate comprehensive outlier analysis plots for specified columns.
- Box Plot: Shows quartiles and outlier points
- Distribution Plot: Shows data distribution with KDE
- Q-Q Plot: Assesses normality of the data
- Automatically analyzes all numeric columns if none specified

```python
cleaner = OutlierCleaner(df)
# Analyze all numeric columns
figures = cleaner.plot_outlier_analysis()
# Or specific columns
figures = cleaner.plot_outlier_analysis(['column1', 'column2'])
```

## Methods

### analyze_distribution(column)
Analyze the distribution of a column and recommend the best outlier detection method.
- Calculates skewness, kurtosis, and normality tests
- Recommends the most appropriate method and thresholds
- Returns detailed distribution analysis

### clean_columns(columns=None, method='auto', show_progress=True)
Clean multiple columns using the most appropriate method for each column.
- Automatic method selection based on distribution analysis
- Progress bar for tracking cleaning operations
- Returns cleaned DataFrame and outlier information

### remove_outliers_modified_zscore(column, threshold=3.5)
Remove outliers using the Modified Z-score method (robust to non-normal distributions).
- Uses Median Absolute Deviation (MAD) instead of standard deviation
- Automatically handles zero MAD cases
- Returns cleaned DataFrame and outlier information

### get_outlier_indices(column=None)
Get the indices of outliers for specified column(s).
- Returns dictionary mapping columns to outlier indices
- Handles missing columns gracefully by returning empty lists
- Useful for tracking and analyzing removed data points
- Can retrieve indices for a specific column or all processed columns

### get_outlier_stats()
Get comprehensive outlier statistics without removing data points.
- Provides potential outlier counts and percentages
- Calculates bounds and thresholds for each method
- Returns detailed statistics for analysis and comparison

### Additional Methods
- `compare_methods()`: Compare different detection methods
- `add_zscore_columns()`: Add Z-score columns for analysis
- `clean_zscore_columns()`: Clean using Z-score thresholds
- `remove_outliers_iqr()`: Clean using IQR method
- `remove_outliers_zscore()`: Clean using Z-score method

## Requirements

- numpy>=1.20.0
- pandas>=1.3.0
- matplotlib>=3.4.0
- seaborn>=0.11.0
- scipy>=1.7.0
- scikit-learn>=0.24.0 (for examples)
- tqdm>=4.62.0

## Changelog

### Version 1.1.2 (2025-08-05)
- **Comprehensive Type Hints**: Added complete type annotations to all methods and functions
  - Enhanced IDE support with better autocomplete and error detection
  - Improved code documentation through type annotations
  - MyPy compatibility for static type checking
  - Better developer experience and code maintainability
- Updated dependency management with complete requirements specification
- Enhanced null safety with proper error handling
- Improved code quality and professional standards
- Full backward compatibility maintained
- Updated requirements.txt with scipy and tqdm dependencies
- Synchronized dependency versions across setup.py and requirements.txt

### Version 1.0.8 (2024-03-24)
- Improved outlier_analysis method with enhanced visualization capabilities
- Added robust error handling for missing columns and non-numeric data
- Optimized plot layout and styling for better readability
- Fixed memory management in visualization functions
- Added comprehensive test suite for visualization features

### Version 1.0.7 (2024-03-24)
- Enhanced visualization tools with improved plot customization
- Added comprehensive docstrings to all visualization functions
- Improved error handling in plotting functions
- Updated documentation with detailed usage examples
- Code optimization and performance improvements

### Version 1.0.6
- Added new standalone visualization functions:
  - plot_boxplot: Box plot with outlier highlighting
  - plot_qq: Q-Q plot for normality assessment
  - plot_outlier_analysis: Comprehensive 2x2 dashboard
- Enhanced visualization features:
  - Improved outlier highlighting in all plots
  - Added grid lines for better readability
  - Automatic layout adjustment in dashboard view
- Updated documentation with new visualization examples
- Improved type hints and error handling

### Version 1.0.5
- Fixed boxplot visualization in plot_outlier_analysis
- Enhanced automatic column handling for visualization functions
- Improved error messages and user feedback
- Updated documentation with clearer examples

### Version 1.0.4
- Added standalone visualization functions in utils.py
- Added comprehensive plot_outlier_analysis method
- Enhanced distribution visualization with KDE
- Added Q-Q plots for normality assessment
- Improved error handling and user feedback
- Updated documentation with visualization examples

### Version 1.0.2
- Enhanced outlier indices tracking in all removal methods
- Improved `get_outlier_indices()` to handle missing columns gracefully
- Optimized outlier statistics calculation
- Removed redundant outlier indices from `get_outlier_stats()` output

### Version 1.0.1
- Fixed author name spelling
- Updated documentation and examples
- Added comprehensive test coverage

### Version 1.0.0
- Initial release with core functionality
- Added distribution analysis and automatic method selection
- Implemented visualization tools and progress tracking

## Author

Subashanan Nair

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
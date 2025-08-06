"""
outlier_cleaner.py - A module for detecting and removing outliers in data

This module provides functions for identifying and removing outliers
using various statistical methods such as IQR and Z-score.
"""

from typing import Optional, List, Dict, Tuple, Union, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from tqdm import tqdm


class OutlierCleaner:
    """
    A class for detecting and removing outliers from pandas DataFrames.
    
    This class provides methods to clean data using different statistical
    approaches, visualize the outliers, and generate reports on the 
    cleaning process.
    """
    
    def __init__(self, df: Optional[pd.DataFrame] = None, preserve_index: bool = True) -> None:
        """
        Initialize the OutlierCleaner with an optional DataFrame.
        
        Parameters:
        -----------
        df : pandas.DataFrame, optional
            The DataFrame to clean
        preserve_index : bool, default=True
            Whether to preserve the original index after cleaning
        """
        self.original_df: Optional[pd.DataFrame] = df.copy() if df is not None else None
        self.clean_df: Optional[pd.DataFrame] = df.copy() if df is not None else None
        self.outlier_info: Dict[str, Dict[str, Any]] = {}
        self.preserve_index: bool = preserve_index
        
    def set_data(self, df: pd.DataFrame, preserve_index: Optional[bool] = None) -> None:
        """
        Set or update the DataFrame to be cleaned.
        
        Parameters:
        -----------
        df : pandas.DataFrame
            The DataFrame to clean
        preserve_index : bool, optional
            Whether to preserve the original index after cleaning.
            If None, uses the value set in __init__
        """
        self.original_df = df.copy()
        self.clean_df = df.copy()
        self.outlier_info = {}
        if preserve_index is not None:
            self.preserve_index = preserve_index
        
    def add_zscore_columns(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Add Z-score columns to the DataFrame for specified columns.
        The new columns will have '_zscore' appended to the original column names.
        
        Parameters:
        -----------
        columns : list or None, default=None
            List of columns to calculate Z-scores for. If None, all numeric columns will be used.
            
        Returns:
        --------
        pandas.DataFrame
            The DataFrame with added Z-score columns
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
            
        # If no columns specified, use all numeric columns
        if columns is None:
            columns = self.clean_df.select_dtypes(include=np.number).columns.tolist()
        
        # Process each column
        for col in columns:
            if col not in self.clean_df.columns:
                print(f"Warning: Column '{col}' not found in DataFrame. Skipping.")
                continue
                
            if not np.issubdtype(self.clean_df[col].dtype, np.number):
                print(f"Warning: Column '{col}' is not numeric. Skipping.")
                continue
            
            # Calculate Z-scores
            zscore_col = f"{col}_zscore"
            self.clean_df[zscore_col] = (self.clean_df[col] - self.clean_df[col].mean()) / self.clean_df[col].std()
        
        return self.clean_df
        
    def clean_zscore_columns(self, threshold: float = 3.0) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
        """
        Clean all columns that have associated Z-score columns.
        This method will remove outliers from all columns that have '_zscore' columns.
        
        Parameters:
        -----------
        threshold : float, default=3.0
            The Z-score threshold above which to consider a point an outlier
            
        Returns:
        --------
        pandas.DataFrame
            A DataFrame with outliers removed from all Z-score columns
        dict
            Information about outliers removed from each column
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
        
        # Find all columns with Z-scores
        zscore_cols = [col for col in self.clean_df.columns if col.endswith('_zscore')]
        original_cols = [col[:-7] for col in zscore_cols]  # Remove '_zscore' suffix
        
        if not zscore_cols:
            print("No Z-score columns found. Use add_zscore_columns() first.")
            return self.clean_df, self.outlier_info
        
        # Clean each column
        for col in original_cols:
            self.remove_outliers_zscore(col, threshold=threshold)
        
        return self.clean_df, self.outlier_info
        
    def remove_outliers_iqr(self, column: str, lower_factor: float = 1.5, upper_factor: float = 1.5) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Remove outliers from a DataFrame column using the IQR method.
        
        Parameters:
        -----------
        column : str
            The name of the column to clean
        lower_factor : float, default=1.5
            The factor to multiply the IQR by for the lower bound
        upper_factor : float, default=1.5
            The factor to multiply the IQR by for the upper bound
            
        Returns:
        --------
        pandas.DataFrame
            A DataFrame with outliers removed
        dict
            Information about the outliers removed
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
            
        # Calculate Q1, Q3, and IQR
        Q1 = self.clean_df[column].quantile(0.25)
        Q3 = self.clean_df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        # Define lower and upper bounds
        lower_bound = Q1 - (lower_factor * IQR)
        upper_bound = Q3 + (upper_factor * IQR)
        
        # Identify outliers
        outlier_mask = (self.clean_df[column] < lower_bound) | (self.clean_df[column] > upper_bound)
        outliers = self.clean_df[outlier_mask]
        
        # Create a clean DataFrame without outliers
        self.clean_df = self.clean_df[~outlier_mask].copy()
        
        # Reset index if not preserving
        if not self.preserve_index:
            self.clean_df.reset_index(drop=True, inplace=True)
        
        # Prepare outlier information
        if self.original_df is None:
            raise ValueError("Original DataFrame is None")
            
        outlier_info = {
            'method': 'IQR',
            'column': column,
            'Q1': Q1,
            'Q3': Q3,
            'IQR': IQR,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'num_outliers': len(outliers),
            'num_outliers_below': len(self.original_df[self.original_df[column] < lower_bound]),
            'num_outliers_above': len(self.original_df[self.original_df[column] > upper_bound]),
            'percent_removed': (len(outliers) / len(self.original_df)) * 100,
            'outlier_indices': outliers.index.tolist()
        }
        
        # Store outlier information
        self.outlier_info[column] = outlier_info
        
        return self.clean_df, outlier_info
    
    def remove_outliers_zscore(self, column: str, threshold: float = 3.0) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Remove outliers from a DataFrame column using the Z-score method.
        If a Z-score column exists (column_zscore), it will use that instead of recalculating.
        
        Parameters:
        -----------
        column : str
            The name of the column to clean
        threshold : float, default=3.0
            The Z-score threshold above which to consider a point an outlier
            
        Returns:
        --------
        pandas.DataFrame
            A DataFrame with outliers removed
        dict
            Information about the outliers removed
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
            
        # Check if Z-score column exists
        zscore_col = f"{column}_zscore"
        if zscore_col in self.clean_df.columns:
            # Use existing Z-scores
            z_scores = np.abs(self.clean_df[zscore_col])
        else:
            # Calculate Z-scores
            mean = self.clean_df[column].mean()
            std = self.clean_df[column].std()
            z_scores = np.abs((self.clean_df[column] - mean) / std)
        
        # Identify outliers
        outlier_mask = z_scores > threshold
        outliers = self.clean_df[outlier_mask]
        
        # Create a clean DataFrame without outliers
        self.clean_df = self.clean_df[~outlier_mask].copy()
        
        # Reset index if not preserving
        if not self.preserve_index:
            self.clean_df.reset_index(drop=True, inplace=True)
        
        # Prepare outlier information
        if self.original_df is None:
            raise ValueError("Original DataFrame is None")
            
        outlier_info = {
            'method': 'Z-score',
            'column': column,
            'mean': self.original_df[column].mean(),
            'std': self.original_df[column].std(),
            'threshold': threshold,
            'num_outliers': len(outliers),
            'percent_removed': (len(outliers) / len(self.original_df)) * 100,
            'outlier_indices': outliers.index.tolist()
        }
        
        # Store outlier information
        self.outlier_info[column] = outlier_info
        
        return self.clean_df, outlier_info
    
    def get_outlier_stats(self, columns: Optional[List[str]] = None, methods: List[str] = ['iqr', 'zscore'], iqr_factor: float = 1.5, zscore_threshold: float = 3.0, include_indices: bool = False) -> pd.DataFrame:
        """
        Get comprehensive statistics about potential outliers without removing them.
        
        Parameters:
        -----------
        columns : list or None, default=None
            List of columns to analyze. If None, all numeric columns will be analyzed.
        methods : list, default=['iqr', 'zscore']
            List of methods to use for outlier detection
        iqr_factor : float, default=1.5
            The factor to multiply the IQR by for the IQR method
        zscore_threshold : float, default=3.0
            The Z-score threshold for the Z-score method
        include_indices : bool, default=False
            Whether to include outlier indices in the output
            
        Returns:
        --------
        pandas.DataFrame
            A DataFrame containing outlier statistics for each column and method
        """
        if self.clean_df is None or len(self.clean_df.columns) == 0:
            raise ValueError("No DataFrame has been set or DataFrame is empty. Use set_data() first.")
            
        # If no columns specified, use all numeric columns
        if columns is None:
            columns = self.clean_df.select_dtypes(include=np.number).columns.tolist()
            
        stats_data = []
        
        for column in columns:
            if not np.issubdtype(self.clean_df[column].dtype, np.number):
                print(f"Warning: Column '{column}' is not numeric. Skipping.")
                continue
                
            for method in methods:
                if method == 'iqr':
                    # Calculate IQR statistics
                    Q1 = self.clean_df[column].quantile(0.25)
                    Q3 = self.clean_df[column].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - (iqr_factor * IQR)
                    upper_bound = Q3 + (iqr_factor * IQR)
                    
                    outlier_mask = (self.clean_df[column] < lower_bound) | (self.clean_df[column] > upper_bound)
                    outlier_indices = self.clean_df[outlier_mask].index.tolist() if include_indices else None
                    
                    stats_data.append({
                        'Column': column,
                        'Method': 'IQR',
                        'Potential Outliers': outlier_mask.sum(),
                        'Percent Outliers': (outlier_mask.sum() / len(self.clean_df)) * 100,
                        'Lower Bound': lower_bound,
                        'Upper Bound': upper_bound,
                        'Q1': Q1,
                        'Q3': Q3,
                        'IQR': IQR,
                        'Outlier Indices': outlier_indices if include_indices else None
                    })
                
                elif method == 'zscore':
                    # Calculate Z-score statistics
                    zscore_col = f"{column}_zscore"
                    if zscore_col in self.clean_df.columns:
                        z_scores = np.abs(self.clean_df[zscore_col])
                    else:
                        mean = self.clean_df[column].mean()
                        std = self.clean_df[column].std()
                        z_scores = np.abs((self.clean_df[column] - mean) / std)
                    
                    outlier_mask = z_scores > zscore_threshold
                    outlier_indices = self.clean_df[outlier_mask].index.tolist() if include_indices else None
                    
                    stats_data.append({
                        'Column': column,
                        'Method': 'Z-score',
                        'Potential Outliers': outlier_mask.sum(),
                        'Percent Outliers': (outlier_mask.sum() / len(self.clean_df)) * 100,
                        'Threshold': zscore_threshold,
                        'Mean': self.clean_df[column].mean(),
                        'Std': self.clean_df[column].std(),
                        'Outlier Indices': outlier_indices if include_indices else None
                    })
        
        # Convert to DataFrame
        stats_df = pd.DataFrame(stats_data)
        
        # Format percentage with 2 decimal places
        if 'Percent Outliers' in stats_df.columns:
            stats_df['Percent Outliers'] = stats_df['Percent Outliers'].round(2)
        
        # Drop the Outlier Indices column if not requested
        if not include_indices and 'Outlier Indices' in stats_df.columns:
            stats_df = stats_df.drop('Outlier Indices', axis=1)
        
        return stats_df
        
    def plot_outlier_analysis(self, columns: Optional[Union[str, List[str]]] = None, methods: Optional[List[str]] = None, figsize: Tuple[int, int] = (15, 5)) -> Dict[str, Any]:
        """
        Generate comprehensive outlier analysis plots for specified columns.
        
        Parameters
        ----------
        columns : str or list of str, optional
            Column(s) to analyze. If None, analyzes all numeric columns.
            Column names are case-insensitive.
        methods : list of str, optional
            Outlier detection methods to use. If None, uses all available methods.
        figsize : tuple, optional
            Base figure size for each subplot (width, height). Default is (15, 5).
            
        Returns
        -------
        dict
            Dictionary of matplotlib figures keyed by column names.
        """
        if not hasattr(self, 'clean_df') or self.clean_df is None:
            raise ValueError("No data available. Please set data using set_data() first.")

        # If no columns specified, use all numeric columns
        if columns is None:
            columns = self.clean_df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        elif isinstance(columns, str):
            columns = [columns]
        
        # Create case-insensitive column mapping
        column_map = {col.lower(): col for col in self.clean_df.columns}
        
        # Validate columns exist in the DataFrame (case-insensitive)
        invalid_columns = []
        resolved_columns = []
        for col in columns:
            col_lower = col.lower()
            if col_lower in column_map:
                resolved_columns.append(column_map[col_lower])
            else:
                invalid_columns.append(col)
        
        if invalid_columns:
            available_cols = "\n".join(self.clean_df.columns)
            raise ValueError(
                f"Column(s) {invalid_columns} not found in the dataset.\n"
                f"Available columns are:\n{available_cols}"
            )

        figures = {}
        for column in resolved_columns:
            if not pd.api.types.is_numeric_dtype(self.clean_df[column]):
                print(f"Warning: Skipping non-numeric column '{column}'")
                continue
            
            fig, axes = plt.subplots(1, 3, figsize=figsize)
            fig.suptitle(f'Outlier Analysis for {column}', fontsize=14)
            
            # Box plot - Fixed to use the correct data parameter format
            sns.boxplot(data=self.clean_df[column], ax=axes[0])
            axes[0].set_title('Box Plot')
            axes[0].set_xlabel(column)
            
            # Distribution plot with outlier thresholds
            sns.histplot(data=self.clean_df[column], ax=axes[1], kde=True)
            axes[1].set_title('Distribution Plot')
            axes[1].set_xlabel(column)
            
            # Q-Q plot
            stats.probplot(self.clean_df[column].dropna(), dist="norm", plot=axes[2])
            axes[2].set_title('Q-Q Plot')
            
            plt.tight_layout()
            figures[column] = fig
        
        return figures
        
    def compare_methods(self, columns=None, methods=['iqr', 'zscore'], iqr_factor=1.5, zscore_threshold=3.0):
        """
        Compare different outlier detection methods and their agreement.
        
        Parameters:
        -----------
        columns : list or None, default=None
            List of columns to analyze. If None, all numeric columns will be analyzed.
        methods : list, default=['iqr', 'zscore']
            List of methods to compare
        iqr_factor : float, default=1.5
            The factor to multiply the IQR by for the IQR method
        zscore_threshold : float, default=3.0
            The Z-score threshold for the Z-score method
            
        Returns:
        --------
        dict
            A dictionary containing comparison metrics:
            {
                'column_name': {
                    'agreement_percentage': float,  # % of points where methods agree
                    'common_outliers': list,  # indices flagged by all methods
                    'method_specific_outliers': {  # indices unique to each method
                        'iqr': list,
                        'zscore': list
                    },
                    'summary': str  # Text summary of the comparison
                }
            }
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
            
        # Get outlier statistics
        stats_df = self.get_outlier_stats(columns, methods, iqr_factor, zscore_threshold)
        comparison = {}
        
        # Get unique columns from the stats DataFrame
        unique_columns = stats_df['Column'].unique()
        
        for column in unique_columns:
            comparison[column] = {}
            outliers_by_method = {}
            
            # Get outlier indices for each method
            if 'iqr' in methods:
                iqr_row = stats_df[(stats_df['Column'] == column) & (stats_df['Method'] == 'IQR')]
                if not iqr_row.empty:
                    Q1 = iqr_row['Q1'].iloc[0]
                    Q3 = iqr_row['Q3'].iloc[0]
                    IQR = iqr_row['IQR'].iloc[0]
                    lower_bound = Q1 - (iqr_factor * IQR)
                    upper_bound = Q3 + (iqr_factor * IQR)
                    outlier_mask = (self.clean_df[column] < lower_bound) | (self.clean_df[column] > upper_bound)
                    outliers_by_method['iqr'] = set(self.clean_df[outlier_mask].index.tolist())
            
            if 'zscore' in methods:
                zscore_row = stats_df[(stats_df['Column'] == column) & (stats_df['Method'] == 'Z-score')]
                if not zscore_row.empty:
                    zscore_col = f"{column}_zscore"
                    if zscore_col in self.clean_df.columns:
                        z_scores = np.abs(self.clean_df[zscore_col])
                    else:
                        mean = zscore_row['Mean'].iloc[0]
                        std = zscore_row['Std'].iloc[0]
                        z_scores = np.abs((self.clean_df[column] - mean) / std)
                    outlier_mask = z_scores > zscore_threshold
                    outliers_by_method['zscore'] = set(self.clean_df[outlier_mask].index.tolist())
            
            # Find common outliers across all methods
            if len(methods) > 1:
                common_outliers = set.intersection(*outliers_by_method.values())
                
                # Calculate method-specific outliers
                method_specific = {}
                for method in methods:
                    if method in outliers_by_method:
                        method_specific[method] = outliers_by_method[method] - common_outliers
                
                # Calculate agreement percentage
                all_outliers = set.union(*outliers_by_method.values())
                agreement_percentage = (len(common_outliers) / len(all_outliers) * 100) if all_outliers else 100.0
                
                comparison[column] = {
                    'agreement_percentage': agreement_percentage,
                    'common_outliers': sorted(list(common_outliers)),
                    'method_specific_outliers': {m: sorted(list(s)) for m, s in method_specific.items()},
                    'summary': f"""
                    Analysis for column '{column}':
                    - Total potential outliers: {len(all_outliers)}
                    - Outliers identified by all methods: {len(common_outliers)}
                    - Method agreement: {agreement_percentage:.1f}%
                    - Method-specific counts: {', '.join(f"{m}: {len(v)}" for m, v in method_specific.items())}
                    """
                }
            else:
                # If only one method, set its outliers as common
                method = methods[0]
                comparison[column] = {
                    'agreement_percentage': 100.0,
                    'common_outliers': sorted(list(outliers_by_method[method])),
                    'method_specific_outliers': {method: []},
                    'summary': f"""
                    Analysis for column '{column}':
                    - Total outliers identified by {method}: {len(outliers_by_method[method])}
                    """
                }
        
        return comparison
        
    def analyze_distribution(self, column: str) -> Dict[str, Any]:
        """
        Analyze the distribution of a column and recommend the best outlier detection method.
        
        Parameters:
        -----------
        column : str
            The name of the column to analyze
            
        Returns:
        --------
        dict
            Distribution analysis results including:
            - skewness
            - kurtosis
            - normality test results
            - recommended method
            - recommended thresholds
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
            
        data = self.clean_df[column]
        
        # Calculate basic statistics
        skewness = data.skew()
        kurtosis = data.kurtosis()
        
        # Perform Shapiro-Wilk test for normality
        _, p_value = stats.shapiro(data.sample(min(len(data), 5000)))  # Sample to handle large datasets
        
        # Calculate robust statistics
        median = data.median()
        mad = stats.median_abs_deviation(data)
        
        # Make recommendations
        recommended_threshold: Union[Dict[str, float], float]
        if abs(skewness) > 2 or abs(kurtosis) > 7:
            recommended_method = 'iqr'
            iqr = data.quantile(0.75) - data.quantile(0.25)
            recommended_threshold = {
                'lower_factor': 2.0 if skewness < -1 else 1.5,
                'upper_factor': 2.0 if skewness > 1 else 1.5
            }
        elif p_value < 0.05:
            recommended_method = 'modified_zscore'
            recommended_threshold = 3.5
        else:
            recommended_method = 'zscore'
            recommended_threshold = 3.0
            
        return {
            'skewness': skewness,
            'kurtosis': kurtosis,
            'normality_p_value': p_value,
            'is_normal': p_value >= 0.05,
            'median': median,
            'mad': mad,
            'recommended_method': recommended_method,
            'recommended_threshold': recommended_threshold
        }
        
    def remove_outliers_modified_zscore(self, column: str, threshold: float = 3.5) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Remove outliers using Modified Z-score method, which is more robust for skewed data.
        Uses Median Absolute Deviation (MAD) instead of standard deviation.
        
        Parameters:
        -----------
        column : str
            The name of the column to clean
        threshold : float, default=3.5
            The modified Z-score threshold above which to consider a point an outlier
            
        Returns:
        --------
        pandas.DataFrame
            A DataFrame with outliers removed
        dict
            Information about the outliers removed
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
            
        # Calculate modified Z-scores
        median = self.clean_df[column].median()
        mad = stats.median_abs_deviation(self.clean_df[column])
        
        # Handle zero MAD case
        if mad == 0:
            print(f"Warning: MAD is zero for column '{column}'. Using standard Z-score method instead.")
            return self.remove_outliers_zscore(column, threshold)
            
        modified_zscores = 0.6745 * (self.clean_df[column] - median) / mad
        
        # Identify outliers
        outlier_mask = np.abs(modified_zscores) > threshold
        outliers = self.clean_df[outlier_mask]
        
        # Create a clean DataFrame without outliers
        self.clean_df = self.clean_df[~outlier_mask].copy()
        
        # Reset index if not preserving
        if not self.preserve_index:
            self.clean_df.reset_index(drop=True, inplace=True)
        
        # Prepare outlier information
        if self.original_df is None:
            raise ValueError("Original DataFrame is None")
            
        outlier_info = {
            'method': 'Modified Z-score',
            'column': column,
            'median': median,
            'mad': mad,
            'threshold': threshold,
            'num_outliers': len(outliers),
            'percent_removed': (len(outliers) / len(self.original_df)) * 100,
            'outlier_indices': outliers.index.tolist()
        }
        
        # Store outlier information
        self.outlier_info[column] = outlier_info
        
        return self.clean_df, outlier_info
        
    def clean_columns(self, columns: Optional[List[str]] = None, method: str = 'auto', show_progress: bool = True, include_indices: bool = False, **kwargs: Any) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Clean multiple columns using the most appropriate method for each column.
        
        Parameters:
        -----------
        columns : list or None, default=None
            List of columns to clean. If None, all numeric columns will be used.
        method : str, default='auto'
            Method to use for cleaning:
            - 'auto': Automatically choose best method based on distribution
            - 'iqr': Use IQR method
            - 'zscore': Use Z-score method
            - 'modified_zscore': Use Modified Z-score method
        show_progress : bool, default=True
            Whether to show a progress bar during cleaning
        include_indices : bool, default=False
            Whether to include outlier indices in the output DataFrame
        **kwargs:
            Additional arguments to pass to the cleaning methods:
            - threshold: for Z-score methods
            - lower_factor, upper_factor: for IQR method
            
        Returns:
        --------
        tuple
            - pandas.DataFrame: The cleaned DataFrame
            - pandas.DataFrame: Summary of outlier statistics for each column
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
            
        # If no columns specified, use all numeric columns
        if columns is None:
            columns = self.clean_df.select_dtypes(include=np.number).columns.tolist()
            
        # Create progress bar if requested
        columns_to_iterate = tqdm(columns, desc="Cleaning columns") if show_progress else columns
            
        cleaning_results = []
        
        for column in columns_to_iterate:
            if method == 'auto':
                # Analyze distribution and get recommended method
                analysis = self.analyze_distribution(column)
                recommended_method = analysis['recommended_method']
                recommended_threshold = analysis['recommended_threshold']
                
                if recommended_method == 'iqr':
                    self.remove_outliers_iqr(column, 
                                           lower_factor=recommended_threshold['lower_factor'],
                                           upper_factor=recommended_threshold['upper_factor'])
                elif recommended_method == 'modified_zscore':
                    self.remove_outliers_modified_zscore(column, threshold=recommended_threshold)
                else:
                    self.remove_outliers_zscore(column, threshold=recommended_threshold)
            else:
                if method == 'iqr':
                    self.remove_outliers_iqr(column, **kwargs)
                elif method == 'zscore':
                    self.remove_outliers_zscore(column, **kwargs)
                elif method == 'modified_zscore':
                    self.remove_outliers_modified_zscore(column, **kwargs)
                else:
                    raise ValueError(f"Unknown method: {method}")
            
            # Get the outlier info for this column
            info = self.outlier_info[column]
            
            # Create a summary row
            summary = {
                'Column': column,
                'Method': info['method'],
                'Outliers Found': info['num_outliers'],
                'Percent Removed': round(info['percent_removed'], 2)
            }
            
            # Add method-specific statistics
            if info['method'] == 'IQR':
                summary.update({
                    'Lower Bound': info['lower_bound'],
                    'Upper Bound': info['upper_bound'],
                    'Q1': info['Q1'],
                    'Q3': info['Q3'],
                    'IQR': info['IQR'],
                    'Below Lower': info.get('num_outliers_below', '-'),
                    'Above Upper': info.get('num_outliers_above', '-')
                })
            elif info['method'] in ['Z-score', 'Modified Z-score']:
                if info['method'] == 'Z-score':
                    summary.update({
                        'Mean': info['mean'],
                        'Std': info['std'],
                        'Threshold': info['threshold']
                    })
                else:
                    summary.update({
                        'Median': info['median'],
                        'MAD': info['mad'],
                        'Threshold': info['threshold']
                    })
            
            # Add outlier indices if requested
            if include_indices:
                summary['Outlier Indices'] = info.get('outlier_indices', [])
                
            cleaning_results.append(summary)
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(cleaning_results)
        
        # Reorder columns for better presentation
        column_order = ['Column', 'Method', 'Outliers Found', 'Percent Removed']
        if 'Lower Bound' in results_df.columns:
            column_order.extend(['Lower Bound', 'Upper Bound', 'Q1', 'Q3', 'IQR', 'Below Lower', 'Above Upper'])
        if 'Mean' in results_df.columns:
            column_order.extend(['Mean', 'Std', 'Threshold'])
        if 'Median' in results_df.columns:
            column_order.extend(['Median', 'MAD', 'Threshold'])
        if include_indices and 'Outlier Indices' in results_df.columns:
            column_order.append('Outlier Indices')
            
        results_df = results_df[column_order]
        
        return self.clean_df, results_df
    
    def visualize_outliers(self, column: str) -> None:
        """
        Visualize the distribution of data and highlight outliers.
        
        Parameters:
        -----------
        column : str
            The name of the column to visualize
        """
        if self.original_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
            
        if column not in self.outlier_info:
            raise ValueError(f"No outlier information found for column '{column}'. Run removal first.")
            
        outlier_info = self.outlier_info[column]
        
        plt.figure(figsize=(12, 6))
        
        # Create subplot for the boxplot
        plt.subplot(1, 2, 1)
        sns.boxplot(y=self.original_df[column])
        plt.title(f'Boxplot of {column}')
        
        # Create subplot for the histogram
        plt.subplot(1, 2, 2)
        sns.histplot(self.original_df[column], kde=True)
        
        if outlier_info['method'] == 'IQR':
            plt.axvline(outlier_info['lower_bound'], color='r', linestyle='--', 
                       label=f"Lower bound: {outlier_info['lower_bound']:.2f}")
            plt.axvline(outlier_info['upper_bound'], color='r', linestyle='--',
                       label=f"Upper bound: {outlier_info['upper_bound']:.2f}")
        else:  # Z-score
            # Calculate bounds for z-score method for visualization
            mean = outlier_info['mean']
            std = outlier_info['std']
            threshold = outlier_info['threshold']
            lower_bound = mean - threshold * std
            upper_bound = mean + threshold * std
            plt.axvline(lower_bound, color='r', linestyle='--',
                       label=f"Lower bound: {lower_bound:.2f}")
            plt.axvline(upper_bound, color='r', linestyle='--',
                       label=f"Upper bound: {upper_bound:.2f}")
        
        plt.title(f'Distribution of {column} with Outlier Bounds')
        plt.legend()
        
        plt.tight_layout()
        plt.show()
        
        self._print_outlier_summary(column)
    
    def _print_outlier_summary(self, column: str) -> None:
        """
        Print a summary of outliers for a specific column.
        
        Parameters:
        -----------
        column : str
            The name of the column to summarize
        """
        if column not in self.outlier_info:
            raise ValueError(f"No outlier information found for column '{column}'")
            
        outlier_info = self.outlier_info[column]
        
        print(f"Outlier Summary ({outlier_info['method']} method):")
        print(f"- Column: {column}")
        print(f"- Number of outliers: {outlier_info['num_outliers']} ({outlier_info['percent_removed']:.2f}%)")
        if outlier_info['method'] == 'IQR':
            print(f"- Outliers below lower bound: {outlier_info['num_outliers_below']}")
            print(f"- Outliers above upper bound: {outlier_info['num_outliers_above']}")
    
    def get_summary_report(self) -> Dict[str, Any]:
        """
        Generate a summary report of all outlier removal operations.
        
        Returns:
        --------
        dict
            Summary report of all operations
        """
        if not self.outlier_info:
            return {"status": "No outlier removal operations performed yet"}
            
        if self.original_df is None or self.clean_df is None:
            raise ValueError("DataFrames are None")
            
        total_rows_before = len(self.original_df)
        total_rows_after = len(self.clean_df)
        percent_removed = ((total_rows_before - total_rows_after) / total_rows_before) * 100
        
        summary = {
            "original_shape": self.original_df.shape,
            "clean_shape": self.clean_df.shape,
            "total_rows_removed": total_rows_before - total_rows_after,
            "percent_removed": percent_removed,
            "columns_processed": list(self.outlier_info.keys()),
            "column_details": self.outlier_info
        }
        
        return summary
    
    def reset(self) -> None:
        """
        Reset the cleaner to the original DataFrame.
        """
        if self.original_df is not None:
            self.clean_df = self.original_df.copy()
            self.outlier_info = {}

    def get_outlier_indices(self, column: Optional[str] = None) -> Dict[str, List[int]]:
        """
        Get the indices of outliers for specified column(s).
        
        Parameters:
        -----------
        column : str or None, default=None
            Column name to get outlier indices for.
            If None, returns indices for all columns that have been cleaned.
            
        Returns:
        --------
        dict
            Dictionary mapping column names to lists of outlier indices.
            For columns without outlier information, returns an empty list.
        """
        if column is not None:
            if column not in self.outlier_info:
                return {column: []}
            info = self.outlier_info[column]
            return {column: info.get('outlier_indices', [])}
        
        return {col: info.get('outlier_indices', []) 
               for col, info in self.outlier_info.items()}


# Example usage:
def example():
    """
    Example demonstrating how to use the OutlierCleaner class.
    """
    # Create a sample DataFrame
    np.random.seed(42)
    data = {
        'normal_data': np.random.normal(0, 1, 1000),
        'skewed_data': np.random.exponential(2, 1000),
        'categorical': np.random.choice(['A', 'B', 'C'], 1000)
    }
    df = pd.DataFrame(data)
    
    # Add some outliers
    df.loc[0, 'normal_data'] = 15  # Add a high outlier
    df.loc[1, 'normal_data'] = -12  # Add a low outlier
    df.loc[2, 'skewed_data'] = 30  # Add a high outlier
    
    # Create an OutlierCleaner instance
    cleaner = OutlierCleaner(df)
    
    # Method 1: Clean a specific column using IQR
    print("Cleaning 'normal_data' with IQR method:")
    cleaner.remove_outliers_iqr('normal_data')
    cleaner.visualize_outliers('normal_data')
    
    # Reset to original data
    cleaner.reset()
    
    # Method 2: Clean a specific column using Z-score
    print("\nCleaning 'normal_data' with Z-score method:")
    cleaner.remove_outliers_zscore('normal_data', threshold=2.5)
    cleaner.visualize_outliers('normal_data')
    
    # Reset to original data
    cleaner.reset()
    
    # Method 3: Clean multiple columns at once
    print("\nCleaning multiple columns with IQR method:")
    cleaner.clean_columns(method='iqr', columns=['normal_data', 'skewed_data'])
    
    # Get a summary report
    report = cleaner.get_summary_report()
    print("\nSummary Report:")
    for key, value in report.items():
        if key != "column_details":
            print(f"- {key}: {value}")
            
    # Visualize the results for all processed columns
    for column in report["columns_processed"]:
        cleaner.visualize_outliers(column)


if __name__ == "__main__":
    example()
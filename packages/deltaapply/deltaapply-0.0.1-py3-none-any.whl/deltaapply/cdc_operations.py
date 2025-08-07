"""CDC operations for detecting and categorizing data changes."""

from typing import List, Set, Tuple, Dict, Any
import polars as pl
from dataclasses import dataclass

from .exceptions import CDCOperationError


@dataclass
class CDCResult:
    """Container for CDC operation results.
    
    Attributes:
        inserts: DataFrame with rows to insert
        updates: DataFrame with rows to update  
        deletes: DataFrame with rows to delete
        unchanged: DataFrame with unchanged rows
    """
    inserts: pl.DataFrame
    updates: pl.DataFrame
    deletes: pl.DataFrame
    unchanged: pl.DataFrame


class CDCOperations:
    """Handles Change Data Capture operations for detecting inserts, updates, and deletes."""
    
    def __init__(self, key_columns: List[str]) -> None:
        """Initialize CDC operations.
        
        Args:
            key_columns: List of column names that form the primary key
            
        Raises:
            CDCOperationError: If key_columns is empty
        """
        if not key_columns:
            raise CDCOperationError("At least one key column must be specified")
        self.key_columns = key_columns
    
    def compare_data(self, source: pl.DataFrame, target: pl.DataFrame) -> CDCResult:
        """Compare source and target data to identify changes.
        
        Args:
            source: Source DataFrame (new state)
            target: Target DataFrame (current state)
            
        Returns:
            CDCResult containing categorized changes
            
        Raises:
            CDCOperationError: If key columns are missing or comparison fails
        """
        try:
            self._validate_key_columns(source, target)
            
            # Get all columns except key columns for comparison
            source_data_cols = [col for col in source.columns if col not in self.key_columns]
            target_data_cols = [col for col in target.columns if col not in self.key_columns]
            
            # Ensure both DataFrames have the same columns
            all_columns = list(set(source.columns) | set(target.columns))
            source = self._align_columns(source, all_columns)
            target = self._align_columns(target, all_columns)
            
            # Create key-based joins
            source_keys = {tuple(sorted(d.items())) for d in self._get_key_tuples(source)}
            target_keys = {tuple(sorted(d.items())) for d in self._get_key_tuples(target)}
            
            # Identify different types of changes
            insert_keys = source_keys - target_keys
            delete_keys = target_keys - source_keys
            common_keys = source_keys & target_keys
            
            # Get DataFrames for each operation type
            inserts = self._filter_by_keys(source, insert_keys)
            deletes = self._filter_by_keys(target, delete_keys)
            
            # For common keys, check if data has changed
            updates, unchanged = self._identify_updates_and_unchanged(source, target, common_keys, source_data_cols)
            
            return CDCResult(
                inserts=inserts,
                updates=updates,
                deletes=deletes,
                unchanged=unchanged
            )
            
        except Exception as e:
            raise CDCOperationError(f"Failed to compare data: {str(e)}") from e
    
    def _validate_key_columns(self, source: pl.DataFrame, target: pl.DataFrame) -> None:
        """Validate that key columns exist in both DataFrames.
        
        Args:
            source: Source DataFrame
            target: Target DataFrame
            
        Raises:
            CDCOperationError: If key columns are missing
        """
        missing_in_source = set(self.key_columns) - set(source.columns)
        missing_in_target = set(self.key_columns) - set(target.columns)
        
        if missing_in_source:
            raise CDCOperationError(f"Key columns missing in source: {missing_in_source}")
        if missing_in_target:
            raise CDCOperationError(f"Key columns missing in target: {missing_in_target}")
    
    def _align_columns(self, df: pl.DataFrame, all_columns: List[str]) -> pl.DataFrame:
        """Ensure DataFrame has all required columns, adding missing ones with null values.
        
        Args:
            df: DataFrame to align
            all_columns: List of all required columns
            
        Returns:
            DataFrame with aligned columns
        """
        missing_cols = set(all_columns) - set(df.columns)
        if missing_cols:
            # Add missing columns with null values
            for col in missing_cols:
                df = df.with_columns(pl.lit(None).alias(col))
        
        return df.select(all_columns)
    
    def _get_key_tuples(self, df: pl.DataFrame) -> List[Dict[str, Any]]:
        """Extract key column values as dictionaries.
        
        Args:
            df: DataFrame to extract keys from
            
        Returns:
            List of key dictionaries
        """
        return df.select(self.key_columns).to_dicts()
    
    def _filter_by_keys(self, df: pl.DataFrame, keys: Set[Tuple[Tuple[str, Any], ...]]) -> pl.DataFrame:
        """Filter DataFrame to only include rows with specified keys.
        
        Args:
            df: DataFrame to filter
            keys: Set of key tuples to include
            
        Returns:
            Filtered DataFrame
        """
        if not keys:
            return df.clear()
        
        # Convert tuple keys back to dictionaries
        key_dicts = [dict(key_tuple) for key_tuple in keys]
        key_df = pl.DataFrame(key_dicts)
        
        return df.join(key_df, on=self.key_columns, how="inner")
    
    def _identify_updates_and_unchanged(
        self, 
        source: pl.DataFrame, 
        target: pl.DataFrame, 
        common_keys: Set[Tuple[Tuple[str, Any], ...]], 
        data_columns: List[str]
    ) -> Tuple[pl.DataFrame, pl.DataFrame]:
        """Identify which common keys represent updates vs unchanged records.
        
        Args:
            source: Source DataFrame
            target: Target DataFrame  
            common_keys: Keys that exist in both DataFrames
            data_columns: Non-key columns to compare for changes
            
        Returns:
            Tuple of (updates_df, unchanged_df)
        """
        if not common_keys:
            return source.clear(), target.clear()
        
        # Filter to common keys only
        source_common = self._filter_by_keys(source, common_keys)
        target_common = self._filter_by_keys(target, common_keys)
        
        if not data_columns:
            # If no data columns to compare, all are unchanged
            return source.clear(), source_common
        
        # Join on keys and compare data columns
        joined = source_common.join(
            target_common, 
            on=self.key_columns, 
            how="inner", 
            suffix="_target"
        )
        
        # Build comparison expression for data columns
        comparison_exprs = []
        for col in data_columns:
            source_col = col
            target_col = f"{col}_target"
            if target_col in joined.columns:
                # Handle null comparisons properly
                comparison_exprs.append(
                    (pl.col(source_col).is_null() & pl.col(target_col).is_null()) |
                    (pl.col(source_col) == pl.col(target_col))
                )
            else:
                # Column doesn't exist in target, so it's a change
                comparison_exprs.append(pl.lit(False))
        
        if comparison_exprs:
            # Rows are unchanged if ALL data columns match
            unchanged_filter = pl.fold(
                pl.lit(True),
                lambda acc, expr: acc & expr,
                comparison_exprs
            )
            
            # Separate unchanged and updated records
            unchanged_mask = joined.select(unchanged_filter).to_series().to_list()
            unchanged_indices = [i for i, unchanged in enumerate(unchanged_mask) if unchanged]
            updated_indices = [i for i, unchanged in enumerate(unchanged_mask) if not unchanged]
            
            unchanged = source_common[unchanged_indices] if unchanged_indices else source_common.clear()
            updates = source_common[updated_indices] if updated_indices else source_common.clear()
        else:
            # No data columns to compare
            unchanged = source_common
            updates = source_common.clear()
        
        return updates, unchanged
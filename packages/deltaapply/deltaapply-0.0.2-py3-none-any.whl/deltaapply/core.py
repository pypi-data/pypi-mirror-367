"""Main DeltaApply class for Change Data Capture operations."""

from typing import Union, List, Optional
from pathlib import Path
import polars as pl
import pandas as pd
from sqlalchemy.engine import Engine

from .data_sources import DataSource
from .cdc_operations import CDCOperations, CDCResult
from .target_writers import TargetWriter
from .exceptions import DeltaApplyError, CDCOperationError


class DeltaApply:
    """Main class for Change Data Capture with automatic application of inserts, updates, and deletes.
    
    Compares source and target data to identify changes, then applies the specified operations
    to synchronize the target with the source state.
    """
    
    def __init__(
        self,
        source: Union[str, Path, pd.DataFrame, pl.DataFrame],
        target: Union[str, Path, pd.DataFrame, pl.DataFrame], 
        key_columns: List[str],
        source_connection: Optional[Union[str, Engine]] = None,
        target_connection: Optional[Union[str, Engine]] = None
    ) -> None:
        """Initialize DeltaApply for CDC operations.
        
        Args:
            source: Source data (CSV path, DataFrame, or DB table name)
            target: Target data (CSV path, DataFrame, or DB table name)
            key_columns: Primary key column names for change detection
            source_connection: Database connection for source (if DB table)
            target_connection: Database connection for target (if DB table)
            
        Raises:
            DeltaApplyError: If initialization fails
        """
        try:
            self.source_data = DataSource(source, source_connection)
            self.target_data = DataSource(target, target_connection)
            self.cdc_ops = CDCOperations(key_columns)
            self.key_columns = key_columns
            
            # Store original target info for result formatting
            self.original_target = target
            self.original_target_type = self.target_data.get_original_type()
            
        except Exception as e:
            raise DeltaApplyError(f"Failed to initialize DeltaApply: {str(e)}") from e
    
    def compare(self) -> CDCResult:
        """Compare source and target data to identify changes.
        
        Returns:
            CDCResult containing categorized changes (inserts, updates, deletes, unchanged)
            
        Raises:
            DeltaApplyError: If comparison fails
        """
        try:
            source_df = self.source_data.load_data()
            target_df = self.target_data.load_data()
            
            return self.cdc_ops.compare_data(source_df, target_df)
            
        except Exception as e:
            raise DeltaApplyError(f"Failed to compare data: {str(e)}") from e
    
    def apply(
        self, 
        operations: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Union[pd.DataFrame, pl.DataFrame, str, CDCResult]:
        """Apply CDC operations to synchronize target with source.
        
        Args:
            operations: List of operations to apply. Options: ["insert", "update", "delete"].
                       If None, applies all operations.
            dry_run: If True, returns CDCResult without applying changes
            
        Returns:
            - CDCResult if dry_run=True
            - Updated DataFrame if target is DataFrame  
            - File path if target is CSV
            - Table name if target is database table
            
        Raises:
            DeltaApplyError: If applying operations fails
        """
        # Default to all operations if none specified
        if operations is None:
            operations = ["insert", "update", "delete"]
        
        # Validate operations
        valid_operations = {"insert", "update", "delete"}
        invalid_ops = set(operations) - valid_operations
        if invalid_ops:
            raise DeltaApplyError(f"Invalid operations: {invalid_ops}. Valid options: {valid_operations}")
        
        try:
            # Compare data to get CDC result
            cdc_result = self.compare()
            
            # Return result without applying if dry run
            if dry_run:
                return cdc_result
            
            # Apply operations to target
            writer = TargetWriter(
                self.original_target,
                self.target_data.connection,
                self.original_target_type
            )
            
            return writer.apply_cdc_result(cdc_result, operations, self.key_columns)
            
        except Exception as e:
            raise DeltaApplyError(f"Failed to apply CDC operations: {str(e)}") from e
    
    def apply_inserts_only(self, dry_run: bool = False) -> Union[pd.DataFrame, pl.DataFrame, str, CDCResult]:
        """Apply only insert operations.
        
        Args:
            dry_run: If True, returns CDCResult without applying changes
            
        Returns:
            Same as apply() method
        """
        return self.apply(operations=["insert"], dry_run=dry_run)
    
    def apply_updates_only(self, dry_run: bool = False) -> Union[pd.DataFrame, pl.DataFrame, str, CDCResult]:
        """Apply only update operations.
        
        Args:
            dry_run: If True, returns CDCResult without applying changes
            
        Returns:
            Same as apply() method
        """
        return self.apply(operations=["update"], dry_run=dry_run)
    
    def apply_deletes_only(self, dry_run: bool = False) -> Union[pd.DataFrame, pl.DataFrame, str, CDCResult]:
        """Apply only delete operations.
        
        Args:
            dry_run: If True, returns CDCResult without applying changes
            
        Returns:
            Same as apply() method
        """
        return self.apply(operations=["delete"], dry_run=dry_run)
    
    def get_summary(self) -> dict:
        """Get a summary of changes without applying them.
        
        Returns:
            Dictionary with counts of each operation type
            
        Raises:
            DeltaApplyError: If comparison fails
        """
        try:
            cdc_result = self.compare()
            
            return {
                "inserts": len(cdc_result.inserts),
                "updates": len(cdc_result.updates), 
                "deletes": len(cdc_result.deletes),
                "unchanged": len(cdc_result.unchanged),
                "total_source": len(cdc_result.inserts) + len(cdc_result.updates) + len(cdc_result.unchanged),
                "total_target": len(cdc_result.updates) + len(cdc_result.deletes) + len(cdc_result.unchanged)
            }
            
        except Exception as e:
            raise DeltaApplyError(f"Failed to get summary: {str(e)}") from e
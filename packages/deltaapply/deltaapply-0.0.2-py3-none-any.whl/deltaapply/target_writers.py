"""Target writers for applying CDC operations to different output formats."""

from typing import Union, Optional, List
from pathlib import Path
import polars as pl
import pandas as pd
from sqlalchemy import create_engine, text, MetaData, Table, Column, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.sql import insert, update, delete

from .exceptions import CDCOperationError, UnsupportedDataSourceError
from .cdc_operations import CDCResult


class TargetWriter:
    """Handles writing CDC results to different target formats.
    
    Supports CSV files, pandas/polars DataFrames, and database tables.
    Maintains type consistency with the original target format.
    """
    
    def __init__(
        self,
        target: Union[str, Path, pd.DataFrame, pl.DataFrame],
        connection: Optional[Union[str, Engine]] = None,
        original_type: Optional[type] = None
    ) -> None:
        """Initialize target writer.
        
        Args:
            target: Target destination (CSV path, DataFrame, or table name)
            connection: Database connection (required for DB targets)
            original_type: Original target type for maintaining consistency
            
        Raises:
            UnsupportedDataSourceError: If target type is not supported
        """
        self.target = target
        self.connection = connection
        self.original_type = original_type or type(target)
        self._engine: Optional[Engine] = None
        self._target_type = self._determine_target_type()
        
        if self._target_type == "database" and connection is None:
            raise UnsupportedDataSourceError("Database connection required for database table targets")
    
    def _determine_target_type(self) -> str:
        """Determine the target type.
        
        Returns:
            Target type: "csv", "pandas", "polars", or "database"
        """
        if isinstance(self.target, (str, Path)):
            if self.connection is not None:
                return "database"
            else:
                # Check if it looks like a table name without connection
                path = Path(self.target)
                if path.suffix.lower() == '.csv' or path.exists():
                    return "csv"
                else:
                    # Could be a table name without connection - check for that case
                    if '.' not in str(self.target) and len(str(self.target)) < 100:
                        # This looks like a table name, should have connection
                        return "database"  # This will trigger the error in __init__
                    else:
                        return "csv"
        elif isinstance(self.target, pd.DataFrame):
            return "pandas"
        elif isinstance(self.target, pl.DataFrame):
            return "polars"
        else:
            raise UnsupportedDataSourceError(f"Unsupported target type: {type(self.target)}")
    
    @property
    def engine(self) -> Engine:
        """Get SQLAlchemy engine (creates if needed)."""
        if self._engine is None and self.connection is not None:
            if isinstance(self.connection, str):
                self._engine = create_engine(self.connection)
            else:
                self._engine = self.connection
        return self._engine
    
    def apply_cdc_result(
        self, 
        cdc_result: CDCResult, 
        operations: List[str],
        key_columns: List[str]
    ) -> Union[pd.DataFrame, pl.DataFrame, str]:
        """Apply CDC operations to the target.
        
        Args:
            cdc_result: CDC result containing categorized changes
            operations: List of operations to apply ("insert", "update", "delete")  
            key_columns: Primary key columns for database operations
            
        Returns:
            Updated target (DataFrame for DF targets, path for CSV/DB)
            
        Raises:
            CDCOperationError: If applying operations fails
        """
        try:
            if self._target_type == "database":
                return self._apply_to_database(cdc_result, operations, key_columns)
            elif self._target_type in ["csv", "pandas", "polars"]:
                return self._apply_to_file_or_dataframe(cdc_result, operations)
            else:
                raise CDCOperationError(f"Unsupported target type: {self._target_type}")
                
        except Exception as e:
            raise CDCOperationError(f"Failed to apply CDC operations: {str(e)}") from e
    
    def _apply_to_database(
        self, 
        cdc_result: CDCResult, 
        operations: List[str],
        key_columns: List[str]
    ) -> str:
        """Apply CDC operations to database table.
        
        Args:
            cdc_result: CDC result with operations
            operations: Operations to apply
            key_columns: Primary key columns
            
        Returns:
            Table name
        """
        table_name = str(self.target)
        
        with self.engine.begin() as conn:
            # Reflect the table structure
            metadata = MetaData()
            try:
                table = Table(table_name, metadata, autoload_with=self.engine)
            except Exception:
                # Table might not exist, we'll need to create it
                raise CDCOperationError(f"Table {table_name} does not exist")
            
            # Apply operations in order: deletes, updates, inserts
            if "delete" in operations and not cdc_result.deletes.is_empty():
                self._execute_deletes(conn, table, cdc_result.deletes, key_columns)
            
            if "update" in operations and not cdc_result.updates.is_empty():
                self._execute_updates(conn, table, cdc_result.updates, key_columns)
            
            if "insert" in operations and not cdc_result.inserts.is_empty():
                self._execute_inserts(conn, table, cdc_result.inserts)
        
        return table_name
    
    def _execute_deletes(self, conn, table: Table, deletes_df: pl.DataFrame, key_columns: List[str]) -> None:
        """Execute delete operations on database table.
        
        Args:
            conn: Database connection
            table: SQLAlchemy table object
            deletes_df: DataFrame with rows to delete
            key_columns: Primary key columns
        """
        for row_dict in deletes_df.select(key_columns).to_dicts():
            delete_stmt = delete(table)
            for key_col in key_columns:
                delete_stmt = delete_stmt.where(getattr(table.c, key_col) == row_dict[key_col])
            conn.execute(delete_stmt)
    
    def _execute_updates(self, conn, table: Table, updates_df: pl.DataFrame, key_columns: List[str]) -> None:
        """Execute update operations on database table.
        
        Args:
            conn: Database connection  
            table: SQLAlchemy table object
            updates_df: DataFrame with rows to update
            key_columns: Primary key columns
        """
        for row_dict in updates_df.to_dicts():
            update_stmt = update(table)
            
            # Build WHERE clause for key columns
            for key_col in key_columns:
                update_stmt = update_stmt.where(getattr(table.c, key_col) == row_dict[key_col])
            
            # Build VALUES clause for non-key columns
            update_values = {col: val for col, val in row_dict.items() if col not in key_columns}
            if update_values:
                update_stmt = update_stmt.values(**update_values)
                conn.execute(update_stmt)
    
    def _execute_inserts(self, conn, table: Table, inserts_df: pl.DataFrame) -> None:
        """Execute insert operations on database table.
        
        Args:
            conn: Database connection
            table: SQLAlchemy table object  
            inserts_df: DataFrame with rows to insert
        """
        insert_data = inserts_df.to_dicts()
        if insert_data:
            conn.execute(insert(table), insert_data)
    
    def _apply_to_file_or_dataframe(self, cdc_result: CDCResult, operations: List[str]) -> Union[pd.DataFrame, pl.DataFrame, str]:
        """Apply CDC operations to CSV file or DataFrame.
        
        For CSV and DataFrame targets, we reconstruct the final state by combining:
        - Unchanged rows
        - Updated rows (if "update" in operations)  
        - Inserted rows (if "insert" in operations)
        - Excluding deleted rows (if "delete" in operations)
        
        Args:
            cdc_result: CDC result with operations
            operations: Operations to apply
            
        Returns:
            Final DataFrame or CSV path
        """
        # Start with unchanged rows
        final_data = cdc_result.unchanged.clone()
        
        # Add updates if requested
        if "update" in operations:
            final_data = pl.concat([final_data, cdc_result.updates], how="vertical")
        
        # Add inserts if requested  
        if "insert" in operations:
            final_data = pl.concat([final_data, cdc_result.inserts], how="vertical")
        
        # Note: deletes are handled by NOT including deleted rows in final_data
        # If "delete" is not in operations AND we have operations to apply, we would need to add them back
        # But if operations is empty, we only want unchanged rows
        if operations and "delete" not in operations:
            final_data = pl.concat([final_data, cdc_result.deletes], how="vertical")
        
        # Convert to target format and write/return
        if self._target_type == "csv":
            final_data.write_csv(str(self.target))
            return str(self.target)
        elif self._target_type == "pandas" or self.original_type == pd.DataFrame:
            return final_data.to_pandas()
        elif self._target_type == "polars" or self.original_type == pl.DataFrame:
            return final_data
        else:
            # Default to pandas for backward compatibility
            return final_data.to_pandas()
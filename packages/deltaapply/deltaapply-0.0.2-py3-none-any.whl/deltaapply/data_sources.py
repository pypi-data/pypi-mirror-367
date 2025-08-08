"""Data source abstractions for handling CSV, DataFrame, and database table inputs."""

from typing import Union, Optional, Any
from pathlib import Path
import polars as pl
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .exceptions import UnsupportedDataSourceError


class DataSource:
    """Abstraction layer for different data source types.
    
    Handles CSV files, pandas/polars DataFrames, and database tables uniformly.
    All data is converted to Polars DataFrames internally for processing.
    """
    
    def __init__(
        self,
        source: Union[str, Path, pd.DataFrame, pl.DataFrame],
        connection: Optional[Union[str, Engine]] = None,
        table_name: Optional[str] = None
    ) -> None:
        """Initialize a data source.
        
        Args:
            source: The data source - can be CSV path, DataFrame, or table name
            connection: Database connection string or SQLAlchemy Engine (required for DB tables)
            table_name: Table name (deprecated, use source parameter instead)
            
        Raises:
            UnsupportedDataSourceError: If source type is not supported
        """
        self.original_source = source
        self.connection = connection
        self._engine: Optional[Engine] = None
        self._data: Optional[pl.DataFrame] = None
        self._source_type = self._determine_source_type(source, connection, table_name)
        
        if self._source_type == "database" and connection is None:
            raise UnsupportedDataSourceError("Database connection required for database table sources")
            
    def _determine_source_type(
        self, 
        source: Union[str, Path, pd.DataFrame, pl.DataFrame], 
        connection: Optional[Union[str, Engine]],
        table_name: Optional[str]
    ) -> str:
        """Determine the type of data source.
        
        Args:
            source: The data source
            connection: Database connection
            table_name: Deprecated table name parameter
            
        Returns:
            Source type: "csv", "pandas", "polars", or "database"
            
        Raises:
            UnsupportedDataSourceError: If source type cannot be determined
        """
        # Handle deprecated table_name parameter
        if table_name is not None and isinstance(source, str) and connection is not None:
            return "database"
            
        if isinstance(source, (str, Path)):
            if connection is not None:
                return "database"  # String is table name
            else:
                # Check if it's a CSV file path
                path = Path(source)
                if path.suffix.lower() == '.csv' or path.exists():
                    return "csv"
                else:
                    # Could be a table name without connection - check for that case
                    if table_name is None and '.' not in str(source) and len(str(source)) < 100:
                        raise UnsupportedDataSourceError("Database connection required for database table sources")
                    else:
                        raise UnsupportedDataSourceError(f"Unsupported file type or file not found: {source}")
        elif isinstance(source, pd.DataFrame):
            return "pandas"
        elif isinstance(source, pl.DataFrame):
            return "polars"
        else:
            raise UnsupportedDataSourceError(f"Unsupported data source type: {type(source)}")
    
    @property
    def source_type(self) -> str:
        """Get the source type."""
        return self._source_type
    
    @property
    def engine(self) -> Engine:
        """Get SQLAlchemy engine (creates if needed)."""
        if self._engine is None and self.connection is not None:
            if isinstance(self.connection, str):
                self._engine = create_engine(self.connection)
            else:
                self._engine = self.connection
        return self._engine
    
    def load_data(self) -> pl.DataFrame:
        """Load data from source into a Polars DataFrame.
        
        Returns:
            Polars DataFrame with the loaded data
            
        Raises:
            UnsupportedDataSourceError: If loading fails
        """
        if self._data is not None:
            return self._data
            
        try:
            if self._source_type == "csv":
                self._data = pl.read_csv(str(self.original_source))
            elif self._source_type == "pandas":
                self._data = pl.from_pandas(self.original_source)
            elif self._source_type == "polars":
                self._data = self.original_source.clone()
            elif self._source_type == "database":
                query = f"SELECT * FROM {self.original_source}"
                with self.engine.connect() as conn:
                    result = conn.execute(text(query))
                    columns = result.keys()
                    data = result.fetchall()
                    self._data = pl.DataFrame(data, schema=list(columns))
            else:
                raise UnsupportedDataSourceError(f"Cannot load data from {self._source_type}")
                
        except Exception as e:
            raise UnsupportedDataSourceError(f"Failed to load data: {str(e)}") from e
            
        return self._data
    
    def get_original_type(self) -> type:
        """Get the original data type for maintaining type consistency.
        
        Returns:
            Original data type (pd.DataFrame, pl.DataFrame, str for CSV/DB)
        """
        if self._source_type == "pandas":
            return pd.DataFrame
        elif self._source_type == "polars":
            return pl.DataFrame
        else:
            return str  # CSV files and DB tables represented as strings
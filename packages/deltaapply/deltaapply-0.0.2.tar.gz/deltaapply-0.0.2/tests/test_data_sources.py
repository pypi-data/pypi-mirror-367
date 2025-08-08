"""Tests for DataSource class."""

import pytest
import pandas as pd
import polars as pl
from pathlib import Path
from deltaapply.data_sources import DataSource
from deltaapply.exceptions import UnsupportedDataSourceError


class TestDataSource:
    """Test cases for DataSource class."""
    
    def test_init_with_pandas_dataframe(self, sample_source_df):
        """Test initialization with pandas DataFrame."""
        ds = DataSource(sample_source_df)
        
        assert ds.source_type == "pandas"
        assert ds.original_source is sample_source_df
        assert ds.get_original_type() == pd.DataFrame
    
    def test_init_with_polars_dataframe(self, sample_source_polars):
        """Test initialization with Polars DataFrame."""
        ds = DataSource(sample_source_polars)
        
        assert ds.source_type == "polars"
        assert ds.original_source is sample_source_polars
        assert ds.get_original_type() == pl.DataFrame
    
    def test_init_with_csv_file(self, temp_csv_files):
        """Test initialization with CSV file path."""
        ds = DataSource(temp_csv_files['source'])
        
        assert ds.source_type == "csv"
        assert ds.original_source == temp_csv_files['source']
        assert ds.get_original_type() == str
    
    def test_init_with_database_table(self, sqlite_engine):
        """Test initialization with database table."""
        ds = DataSource("source_table", connection=sqlite_engine)
        
        assert ds.source_type == "database"
        assert ds.original_source == "source_table"
        assert ds.connection is sqlite_engine
        assert ds.get_original_type() == str
    
    def test_init_with_database_no_connection_raises_error(self):
        """Test that database table without connection raises error."""
        with pytest.raises(UnsupportedDataSourceError, match="Database connection required"):
            DataSource("table_name", connection=None)
    
    def test_init_with_unsupported_type_raises_error(self):
        """Test that unsupported data type raises error."""
        with pytest.raises(UnsupportedDataSourceError, match="Unsupported data source type"):
            DataSource(123)  # Integer is not supported
    
    def test_load_pandas_dataframe(self, sample_source_df):
        """Test loading pandas DataFrame."""
        ds = DataSource(sample_source_df)
        result = ds.load_data()
        
        assert isinstance(result, pl.DataFrame)
        assert result.shape == (4, 3)
        assert list(result.columns) == ['id', 'name', 'value']
        
        # Check data content
        result_pd = result.to_pandas()
        pd.testing.assert_frame_equal(result_pd, sample_source_df)
    
    def test_load_polars_dataframe(self, sample_source_polars):
        """Test loading Polars DataFrame."""
        ds = DataSource(sample_source_polars)
        result = ds.load_data()
        
        assert isinstance(result, pl.DataFrame)
        assert result.shape == (4, 3)
        assert list(result.columns) == ['id', 'name', 'value']
        
        # Check data content (should be a clone)
        assert result.equals(sample_source_polars)
        assert result is not sample_source_polars  # Should be a clone
    
    def test_load_csv_file(self, temp_csv_files, sample_source_df):
        """Test loading CSV file."""
        ds = DataSource(temp_csv_files['source'])
        result = ds.load_data()
        
        assert isinstance(result, pl.DataFrame)
        assert result.shape == (4, 3)
        assert list(result.columns) == ['id', 'name', 'value']
        
        # Check data content
        result_pd = result.to_pandas()
        pd.testing.assert_frame_equal(result_pd, sample_source_df)
    
    def test_load_database_table(self, sqlite_engine):
        """Test loading database table."""
        ds = DataSource("source_table", connection=sqlite_engine)
        result = ds.load_data()
        
        assert isinstance(result, pl.DataFrame)
        assert result.shape == (4, 3)
        assert list(result.columns) == ['id', 'name', 'value']
        
        # Check specific data content
        result_dict = result.sort('id').to_dicts()
        expected = [
            {'id': 1, 'name': 'Alice', 'value': 10},
            {'id': 2, 'name': 'Bob Updated', 'value': 25},
            {'id': 3, 'name': 'Charlie', 'value': 30},
            {'id': 4, 'name': 'David', 'value': 40}
        ]
        assert result_dict == expected
    
    def test_load_nonexistent_csv_raises_error(self):
        """Test that loading nonexistent CSV raises error."""
        ds = DataSource("nonexistent_file.csv")
        
        with pytest.raises(UnsupportedDataSourceError, match="Failed to load data"):
            ds.load_data()
    
    def test_load_nonexistent_table_raises_error(self, sqlite_engine):
        """Test that loading nonexistent table raises error."""
        ds = DataSource("nonexistent_table", connection=sqlite_engine)
        
        with pytest.raises(UnsupportedDataSourceError, match="Failed to load data"):
            ds.load_data()
    
    def test_caching_behavior(self, sample_source_df):
        """Test that data is cached after first load."""
        ds = DataSource(sample_source_df)
        
        # First load
        result1 = ds.load_data()
        # Second load should return cached data
        result2 = ds.load_data()
        
        assert result1 is result2  # Same object reference
    
    def test_engine_property_with_string_connection(self):
        """Test engine property with string connection."""
        ds = DataSource("table_name", connection="sqlite:///:memory:")
        
        engine = ds.engine
        assert engine is not None
        assert str(engine.url) == "sqlite:///:memory:"
    
    def test_engine_property_with_engine_connection(self, sqlite_engine):
        """Test engine property with existing engine."""
        ds = DataSource("table_name", connection=sqlite_engine)
        
        engine = ds.engine
        assert engine is sqlite_engine
    
    def test_path_object_as_csv_source(self, temp_csv_files):
        """Test using Path object for CSV source."""
        csv_path = Path(temp_csv_files['source'])
        ds = DataSource(csv_path)
        
        assert ds.source_type == "csv"
        result = ds.load_data()
        assert isinstance(result, pl.DataFrame)
        assert result.shape == (4, 3)
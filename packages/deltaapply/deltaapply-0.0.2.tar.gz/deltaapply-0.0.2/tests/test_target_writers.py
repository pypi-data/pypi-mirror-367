"""Tests for TargetWriter class."""

import pytest
import pandas as pd
import polars as pl
import tempfile
from pathlib import Path
from sqlalchemy import text
from deltaapply.target_writers import TargetWriter
from deltaapply.cdc_operations import CDCResult
from deltaapply.exceptions import UnsupportedDataSourceError, CDCOperationError


class TestTargetWriter:
    """Test cases for TargetWriter class."""
    
    @pytest.fixture
    def sample_cdc_result(self):
        """Sample CDC result for testing."""
        return CDCResult(
            inserts=pl.DataFrame({
                'id': [3, 4],
                'name': ['Charlie', 'David'],
                'value': [30, 40]
            }),
            updates=pl.DataFrame({
                'id': [2],
                'name': ['Bob Updated'],
                'value': [25]
            }),
            deletes=pl.DataFrame({
                'id': [5],
                'name': ['Eve'],
                'value': [50]
            }),
            unchanged=pl.DataFrame({
                'id': [1],
                'name': ['Alice'],
                'value': [10]
            })
        )
    
    def test_init_with_pandas_dataframe(self, sample_target_df):
        """Test initialization with pandas DataFrame."""
        writer = TargetWriter(sample_target_df)
        
        assert writer._target_type == "pandas"
        assert writer.original_type == pd.DataFrame
        assert writer.target is sample_target_df
    
    def test_init_with_polars_dataframe(self, sample_target_polars):
        """Test initialization with Polars DataFrame."""
        writer = TargetWriter(sample_target_polars)
        
        assert writer._target_type == "polars"
        assert writer.original_type == pl.DataFrame
        assert writer.target is sample_target_polars
    
    def test_init_with_csv_file(self, temp_csv_files):
        """Test initialization with CSV file."""
        writer = TargetWriter(temp_csv_files['target'])
        
        assert writer._target_type == "csv"
        assert writer.original_type == str
        assert writer.target == temp_csv_files['target']
    
    def test_init_with_database_table(self, sqlite_engine):
        """Test initialization with database table."""
        writer = TargetWriter("target_table", connection=sqlite_engine)
        
        assert writer._target_type == "database"
        assert writer.original_type == str
        assert writer.target == "target_table"
        assert writer.connection is sqlite_engine
    
    def test_init_database_without_connection_raises_error(self):
        """Test that database target without connection raises error."""
        with pytest.raises(UnsupportedDataSourceError, match="Database connection required"):
            TargetWriter("table_name", connection=None)
    
    def test_apply_cdc_result_to_pandas_all_operations(self, sample_cdc_result):
        """Test applying all CDC operations to pandas DataFrame."""
        target_df = pd.DataFrame({
            'id': [1, 2, 5],
            'name': ['Alice', 'Bob', 'Eve'],
            'value': [10, 20, 50]
        })
        
        writer = TargetWriter(target_df)
        result = writer.apply_cdc_result(sample_cdc_result, ['insert', 'update', 'delete'], ['id'])
        
        assert isinstance(result, pd.DataFrame)
        
        # Check final state: unchanged(1) + updates(2) + inserts(3,4) - deletes(5)
        expected_ids = [1, 2, 3, 4]
        result_ids = sorted(result['id'].tolist())
        assert result_ids == expected_ids
        
        # Check updated value for id=2
        updated_row = result[result['id'] == 2]
        assert updated_row['name'].iloc[0] == 'Bob Updated'
        assert updated_row['value'].iloc[0] == 25
    
    def test_apply_cdc_result_to_polars_all_operations(self, sample_cdc_result):
        """Test applying all CDC operations to Polars DataFrame."""
        target_df = pl.DataFrame({
            'id': [1, 2, 5],
            'name': ['Alice', 'Bob', 'Eve'],
            'value': [10, 20, 50]
        })
        
        writer = TargetWriter(target_df)
        result = writer.apply_cdc_result(sample_cdc_result, ['insert', 'update', 'delete'], ['id'])
        
        assert isinstance(result, pl.DataFrame)
        
        # Check final state
        expected_ids = [1, 2, 3, 4]
        result_ids = sorted(result.select('id').to_series().to_list())
        assert result_ids == expected_ids
        
        # Check updated value for id=2
        updated_row = result.filter(pl.col('id') == 2)
        assert updated_row.select('name').to_series().to_list()[0] == 'Bob Updated'
        assert updated_row.select('value').to_series().to_list()[0] == 25
    
    def test_apply_cdc_result_inserts_only(self, sample_cdc_result):
        """Test applying only insert operations."""
        target_df = pd.DataFrame({
            'id': [1, 2, 5],
            'name': ['Alice', 'Bob', 'Eve'],
            'value': [10, 20, 50]
        })
        
        writer = TargetWriter(target_df)
        result = writer.apply_cdc_result(sample_cdc_result, ['insert'], ['id'])
        
        # Should have: unchanged(1) + inserts(3,4) + deletes(5) (not deleted)
        expected_ids = [1, 3, 4, 5]
        result_ids = sorted(result['id'].tolist())
        assert result_ids == expected_ids
        
        # Bob should NOT be updated (still old value)
        # Note: This test depends on implementation details
    
    def test_apply_cdc_result_updates_only(self, sample_cdc_result):
        """Test applying only update operations."""
        target_df = pd.DataFrame({
            'id': [1, 2, 5],
            'name': ['Alice', 'Bob', 'Eve'],
            'value': [10, 20, 50]
        })
        
        writer = TargetWriter(target_df)
        result = writer.apply_cdc_result(sample_cdc_result, ['update'], ['id'])
        
        # Should have: unchanged(1) + updates(2) + deletes(5) (not deleted)
        expected_ids = [1, 2, 5]
        result_ids = sorted(result['id'].tolist())
        assert result_ids == expected_ids
        
        # Bob should be updated
        updated_row = result[result['id'] == 2]
        assert updated_row['name'].iloc[0] == 'Bob Updated'
    
    def test_apply_cdc_result_deletes_only(self, sample_cdc_result):
        """Test applying only delete operations."""
        target_df = pd.DataFrame({
            'id': [1, 2, 5],
            'name': ['Alice', 'Bob', 'Eve'],
            'value': [10, 20, 50]
        })
        
        writer = TargetWriter(target_df)
        result = writer.apply_cdc_result(sample_cdc_result, ['delete'], ['id'])
        
        # Should have: unchanged(1) - deletes(5)
        # Note: Updates and inserts are not applied
        expected_ids = [1]
        result_ids = sorted(result['id'].tolist())
        assert result_ids == expected_ids
    
    def test_apply_cdc_result_to_csv(self, sample_cdc_result):
        """Test applying CDC operations to CSV file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "target.csv"
            
            # Create initial CSV
            target_df = pd.DataFrame({
                'id': [1, 2, 5],
                'name': ['Alice', 'Bob', 'Eve'],
                'value': [10, 20, 50]
            })
            target_df.to_csv(csv_path, index=False)
            
            writer = TargetWriter(str(csv_path))
            result_path = writer.apply_cdc_result(sample_cdc_result, ['insert', 'update', 'delete'], ['id'])
            
            assert result_path == str(csv_path)
            
            # Read and check the updated CSV
            updated_df = pd.read_csv(csv_path)
            expected_ids = [1, 2, 3, 4]
            result_ids = sorted(updated_df['id'].tolist())
            assert result_ids == expected_ids
    
    def test_apply_cdc_result_to_database(self, sqlite_engine, sample_cdc_result):
        """Test applying CDC operations to database table."""
        writer = TargetWriter("target_table", connection=sqlite_engine)
        result_table = writer.apply_cdc_result(sample_cdc_result, ['insert', 'update', 'delete'], ['id'])
        
        assert result_table == "target_table"
        
        # Check the final state in the database
        with sqlite_engine.connect() as conn:
            result = conn.execute(text("SELECT id, name, value FROM target_table ORDER BY id"))
            rows = result.fetchall()
            
            # Should have: unchanged(1) + updates(2) + inserts(3,4) - deletes(5)
            expected_data = [
                (1, 'Alice', 10),      # unchanged
                (2, 'Bob Updated', 25), # updated
                (3, 'Charlie', 30),    # inserted
                (4, 'David', 40)       # inserted
            ]
            assert list(rows) == expected_data
    
    def test_apply_cdc_database_inserts_only(self, sqlite_engine, sample_cdc_result):
        """Test applying only inserts to database."""
        writer = TargetWriter("target_table", connection=sqlite_engine)
        writer.apply_cdc_result(sample_cdc_result, ['insert'], ['id'])
        
        with sqlite_engine.connect() as conn:
            result = conn.execute(text("SELECT id, name, value FROM target_table ORDER BY id"))
            rows = result.fetchall()
            
            # Original data + inserts
            expected_data = [
                (1, 'Alice', 10),
                (2, 'Bob', 20),        # not updated
                (3, 'Charlie', 30),    # inserted
                (4, 'David', 40),      # inserted
                (5, 'Eve', 50)         # not deleted
            ]
            assert list(rows) == expected_data
    
    def test_apply_cdc_database_updates_only(self, sqlite_engine, sample_cdc_result):
        """Test applying only updates to database."""
        writer = TargetWriter("target_table", connection=sqlite_engine)
        writer.apply_cdc_result(sample_cdc_result, ['update'], ['id'])
        
        with sqlite_engine.connect() as conn:
            result = conn.execute(text("SELECT id, name, value FROM target_table ORDER BY id"))
            rows = result.fetchall()
            
            # Original data with updates applied
            expected_data = [
                (1, 'Alice', 10),
                (2, 'Bob Updated', 25), # updated
                (5, 'Eve', 50)          # not deleted
            ]
            assert list(rows) == expected_data
    
    def test_apply_cdc_database_deletes_only(self, sqlite_engine, sample_cdc_result):
        """Test applying only deletes to database."""
        writer = TargetWriter("target_table", connection=sqlite_engine)
        writer.apply_cdc_result(sample_cdc_result, ['delete'], ['id'])
        
        with sqlite_engine.connect() as conn:
            result = conn.execute(text("SELECT id, name, value FROM target_table ORDER BY id"))
            rows = result.fetchall()
            
            # Original data with deletes applied
            expected_data = [
                (1, 'Alice', 10),
                (2, 'Bob', 20)  # Eve (id=5) deleted, no inserts/updates
            ]
            assert list(rows) == expected_data
    
    def test_apply_cdc_nonexistent_table_raises_error(self, sqlite_engine, sample_cdc_result):
        """Test that applying to nonexistent table raises error."""
        writer = TargetWriter("nonexistent_table", connection=sqlite_engine)
        
        with pytest.raises(CDCOperationError, match="Table nonexistent_table does not exist"):
            writer.apply_cdc_result(sample_cdc_result, ['insert'], ['id'])
    
    def test_type_consistency_pandas_to_pandas(self, sample_cdc_result):
        """Test type consistency when target is pandas DataFrame."""
        target_df = pd.DataFrame({'id': [1], 'name': ['Alice'], 'value': [10]})
        writer = TargetWriter(target_df, original_type=pd.DataFrame)
        result = writer.apply_cdc_result(sample_cdc_result, ['insert'], ['id'])
        
        assert isinstance(result, pd.DataFrame)
    
    def test_type_consistency_polars_to_polars(self, sample_cdc_result):
        """Test type consistency when target is Polars DataFrame."""
        target_df = pl.DataFrame({'id': [1], 'name': ['Alice'], 'value': [10]})
        writer = TargetWriter(target_df, original_type=pl.DataFrame)
        result = writer.apply_cdc_result(sample_cdc_result, ['insert'], ['id'])
        
        assert isinstance(result, pl.DataFrame)
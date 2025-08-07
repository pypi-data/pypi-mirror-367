"""Integration tests for DeltaApply core class."""

import pytest
import pandas as pd
import polars as pl
import tempfile
from pathlib import Path
from sqlalchemy import text
from deltaapply import DeltaApply
from deltaapply.cdc_operations import CDCResult
from deltaapply.exceptions import DeltaApplyError


class TestDeltaApply:
    """Integration test cases for DeltaApply class."""
    
    def test_init_with_dataframes(self, sample_source_df, sample_target_df, key_columns):
        """Test initialization with DataFrames."""
        cdc = DeltaApply(
            source=sample_source_df,
            target=sample_target_df,
            key_columns=key_columns
        )
        
        assert cdc.key_columns == key_columns
        assert cdc.source_data.source_type == "pandas"
        assert cdc.target_data.source_type == "pandas"
        assert cdc.original_target is sample_target_df
    
    def test_init_with_csv_files(self, temp_csv_files, key_columns):
        """Test initialization with CSV files."""
        cdc = DeltaApply(
            source=temp_csv_files['source'],
            target=temp_csv_files['target'],
            key_columns=key_columns
        )
        
        assert cdc.key_columns == key_columns
        assert cdc.source_data.source_type == "csv"
        assert cdc.target_data.source_type == "csv"
    
    def test_init_with_database_tables(self, sqlite_engine, key_columns):
        """Test initialization with database tables."""
        cdc = DeltaApply(
            source="source_table",
            target="target_table",
            key_columns=key_columns,
            source_connection=sqlite_engine,
            target_connection=sqlite_engine
        )
        
        assert cdc.key_columns == key_columns
        assert cdc.source_data.source_type == "database"
        assert cdc.target_data.source_type == "database"
    
    def test_compare_dataframes(self, sample_source_df, sample_target_df, key_columns):
        """Test comparing DataFrames."""
        cdc = DeltaApply(
            source=sample_source_df,
            target=sample_target_df,
            key_columns=key_columns
        )
        
        result = cdc.compare()
        
        assert isinstance(result, CDCResult)
        assert len(result.inserts) == 2  # id 3, 4
        assert len(result.updates) == 1  # id 2
        assert len(result.deletes) == 1  # id 5
        assert len(result.unchanged) == 1  # id 1
    
    def test_get_summary(self, sample_source_df, sample_target_df, key_columns):
        """Test getting changes summary."""
        cdc = DeltaApply(
            source=sample_source_df,
            target=sample_target_df,
            key_columns=key_columns
        )
        
        summary = cdc.get_summary()
        
        expected_summary = {
            'inserts': 2,
            'updates': 1,
            'deletes': 1,
            'unchanged': 1,
            'total_source': 4,  # inserts + updates + unchanged
            'total_target': 3   # updates + deletes + unchanged
        }
        
        assert summary == expected_summary
    
    def test_apply_all_operations_dataframes(self, sample_source_df, sample_target_df, key_columns):
        """Test applying all CDC operations to DataFrames."""
        cdc = DeltaApply(
            source=sample_source_df,
            target=sample_target_df,
            key_columns=key_columns
        )
        
        result = cdc.apply()
        
        assert isinstance(result, pd.DataFrame)
        
        # Final state should have: unchanged(1) + updates(2) + inserts(3,4) - deletes(5)
        expected_ids = [1, 2, 3, 4]
        result_ids = sorted(result['id'].tolist())
        assert result_ids == expected_ids
        
        # Check updated value
        updated_row = result[result['id'] == 2]
        assert updated_row['name'].iloc[0] == 'Bob Updated'
        assert updated_row['value'].iloc[0] == 25
    
    def test_apply_dry_run(self, sample_source_df, sample_target_df, key_columns):
        """Test dry run mode."""
        cdc = DeltaApply(
            source=sample_source_df,
            target=sample_target_df,
            key_columns=key_columns
        )
        
        result = cdc.apply(dry_run=True)
        
        assert isinstance(result, CDCResult)
        assert len(result.inserts) == 2
        assert len(result.updates) == 1
        assert len(result.deletes) == 1
        assert len(result.unchanged) == 1
    
    def test_apply_specific_operations(self, sample_source_df, sample_target_df, key_columns):
        """Test applying specific operations only."""
        cdc = DeltaApply(
            source=sample_source_df,
            target=sample_target_df,
            key_columns=key_columns
        )
        
        # Test inserts only
        result_inserts = cdc.apply(operations=['insert'])
        expected_ids_inserts = [1, 3, 4, 5]  # unchanged + inserts + deletes (not deleted)
        result_ids_inserts = sorted(result_inserts['id'].tolist())
        assert result_ids_inserts == expected_ids_inserts
        
        # Test updates only
        result_updates = cdc.apply(operations=['update'])
        expected_ids_updates = [1, 2, 5]  # unchanged + updates + deletes (not deleted)
        result_ids_updates = sorted(result_updates['id'].tolist())
        assert result_ids_updates == expected_ids_updates
        
        # Check that Bob was updated
        updated_row = result_updates[result_updates['id'] == 2]
        assert updated_row['name'].iloc[0] == 'Bob Updated'
    
    def test_convenience_methods(self, sample_source_df, sample_target_df, key_columns):
        """Test convenience methods for specific operations."""
        cdc = DeltaApply(
            source=sample_source_df,
            target=sample_target_df,
            key_columns=key_columns
        )
        
        # Test inserts only
        result_inserts = cdc.apply_inserts_only()
        assert isinstance(result_inserts, pd.DataFrame)
        
        # Test updates only
        result_updates = cdc.apply_updates_only()
        assert isinstance(result_updates, pd.DataFrame)
        
        # Test deletes only
        result_deletes = cdc.apply_deletes_only()
        assert isinstance(result_deletes, pd.DataFrame)
        
        # Test dry run versions
        dry_result = cdc.apply_inserts_only(dry_run=True)
        assert isinstance(dry_result, CDCResult)
    
    def test_apply_csv_files(self, temp_csv_files, key_columns):
        """Test applying CDC operations to CSV files."""
        cdc = DeltaApply(
            source=temp_csv_files['source'],
            target=temp_csv_files['target'],
            key_columns=key_columns
        )
        
        result_path = cdc.apply()
        
        assert result_path == temp_csv_files['target']
        
        # Read and verify the updated CSV
        updated_df = pd.read_csv(temp_csv_files['target'])
        expected_ids = [1, 2, 3, 4]
        result_ids = sorted(updated_df['id'].tolist())
        assert result_ids == expected_ids
    
    def test_apply_database_tables(self, sqlite_engine, key_columns):
        """Test applying CDC operations to database tables."""
        cdc = DeltaApply(
            source="source_table",
            target="target_table",
            key_columns=key_columns,
            source_connection=sqlite_engine,
            target_connection=sqlite_engine
        )
        
        result_table = cdc.apply()
        
        assert result_table == "target_table"
        
        # Verify the database state
        with sqlite_engine.connect() as conn:
            result = conn.execute(text("SELECT id, name, value FROM target_table ORDER BY id"))
            rows = result.fetchall()
            
            expected_data = [
                (1, 'Alice', 10),       # unchanged
                (2, 'Bob Updated', 25), # updated
                (3, 'Charlie', 30),     # inserted
                (4, 'David', 40)        # inserted
                # id 5 (Eve) deleted
            ]
            assert list(rows) == expected_data
    
    def test_mixed_source_target_types(self, sample_source_df, sqlite_engine, key_columns):
        """Test with different source and target types."""
        cdc = DeltaApply(
            source=sample_source_df,  # pandas DataFrame
            target="target_table",    # database table
            key_columns=key_columns,
            target_connection=sqlite_engine
        )
        
        result = cdc.apply()
        assert result == "target_table"
    
    def test_polars_dataframes(self, sample_source_polars, sample_target_polars, key_columns):
        """Test with Polars DataFrames."""
        cdc = DeltaApply(
            source=sample_source_polars,
            target=sample_target_polars,
            key_columns=key_columns
        )
        
        result = cdc.apply()
        
        assert isinstance(result, pl.DataFrame)
        
        expected_ids = [1, 2, 3, 4]
        result_ids = sorted(result.select('id').to_series().to_list())
        assert result_ids == expected_ids
    
    def test_invalid_operations_raises_error(self, sample_source_df, sample_target_df, key_columns):
        """Test that invalid operations raise error."""
        cdc = DeltaApply(
            source=sample_source_df,
            target=sample_target_df,
            key_columns=key_columns
        )
        
        with pytest.raises(DeltaApplyError, match="Invalid operations"):
            cdc.apply(operations=['invalid_operation'])
        
        with pytest.raises(DeltaApplyError, match="Invalid operations"):
            cdc.apply(operations=['insert', 'invalid', 'update'])
    
    def test_empty_operations_list(self, sample_source_df, sample_target_df, key_columns):
        """Test with empty operations list."""
        cdc = DeltaApply(
            source=sample_source_df,
            target=sample_target_df,
            key_columns=key_columns
        )
        
        # Empty operations should result in unchanged target
        result = cdc.apply(operations=[])
        assert isinstance(result, pd.DataFrame)
        
        # Should only have unchanged rows
        assert len(result) == 1  # Only unchanged (id=1)
        assert result['id'].iloc[0] == 1
    
    def test_composite_key_columns(self):
        """Test CDC with composite primary keys."""
        source = pd.DataFrame({
            'dept_id': [1, 1, 2, 2],
            'emp_id': [10, 11, 20, 21],
            'name': ['Alice', 'Bob Updated', 'Charlie', 'Diana']
        })
        
        target = pd.DataFrame({
            'dept_id': [1, 1, 2],
            'emp_id': [10, 11, 22],
            'name': ['Alice', 'Bob', 'Eve']
        })
        
        cdc = DeltaApply(
            source=source,
            target=target,
            key_columns=['dept_id', 'emp_id']
        )
        
        summary = cdc.get_summary()
        assert summary['inserts'] == 2  # (2,20), (2,21)
        assert summary['updates'] == 1  # (1,11) Bob -> Bob Updated
        assert summary['deletes'] == 1  # (2,22) Eve
        assert summary['unchanged'] == 1  # (1,10) Alice
    
    def test_error_handling_invalid_initialization(self):
        """Test error handling during initialization."""
        with pytest.raises(DeltaApplyError):
            cdc = DeltaApply(
                source="nonexistent.csv",
                target=pd.DataFrame({'id': [1]}),
                key_columns=['id']
            )
            # Error occurs during data loading/comparison
            cdc.compare()
    
    def test_error_handling_comparison_failure(self, sample_source_df, key_columns):
        """Test error handling during comparison."""
        # Target with missing key column
        bad_target = pd.DataFrame({'name': ['Alice'], 'value': [10]})
        
        cdc = DeltaApply(
            source=sample_source_df,
            target=bad_target,
            key_columns=key_columns
        )
        
        with pytest.raises(DeltaApplyError, match="Failed to compare data"):
            cdc.compare()
        
        with pytest.raises(DeltaApplyError, match="Failed to get summary"):
            cdc.get_summary()
    
    def test_pandas_to_polars_conversion(self):
        """Test automatic pandas to polars conversion and back."""
        source_pd = pd.DataFrame({
            'id': [1, 2],
            'name': ['Alice', 'Bob'],
            'value': [10, 20]
        })
        
        target_pd = pd.DataFrame({
            'id': [1],
            'name': ['Alice'],
            'value': [10]
        })
        
        cdc = DeltaApply(
            source=source_pd,
            target=target_pd,
            key_columns=['id']
        )
        
        result = cdc.apply()
        
        # Result should be pandas DataFrame (preserving target type)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # Alice (unchanged) + Bob (inserted)
        assert sorted(result['id'].tolist()) == [1, 2]
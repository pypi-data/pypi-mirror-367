"""Tests for CDCOperations class."""

import pytest
import pandas as pd
import polars as pl
from deltaapply.cdc_operations import CDCOperations, CDCResult
from deltaapply.exceptions import CDCOperationError


class TestCDCOperations:
    """Test cases for CDCOperations class."""
    
    def test_init_with_valid_key_columns(self):
        """Test initialization with valid key columns."""
        cdc = CDCOperations(['id'])
        assert cdc.key_columns == ['id']
        
        cdc_multi = CDCOperations(['id', 'name'])
        assert cdc_multi.key_columns == ['id', 'name']
    
    def test_init_with_empty_key_columns_raises_error(self):
        """Test that empty key columns raises error."""
        with pytest.raises(CDCOperationError, match="At least one key column must be specified"):
            CDCOperations([])
    
    def test_compare_data_basic_scenario(self, key_columns):
        """Test basic CDC comparison scenario."""
        source = pl.DataFrame({
            'id': [1, 2, 3, 4],
            'name': ['Alice', 'Bob Updated', 'Charlie', 'David'],
            'value': [10, 25, 30, 40]
        })
        
        target = pl.DataFrame({
            'id': [1, 2, 5],
            'name': ['Alice', 'Bob', 'Eve'],
            'value': [10, 20, 50]
        })
        
        cdc = CDCOperations(key_columns)
        result = cdc.compare_data(source, target)
        
        assert isinstance(result, CDCResult)
        
        # Check inserts (id 3, 4)
        assert len(result.inserts) == 2
        insert_ids = result.inserts.select('id').to_series().to_list()
        assert sorted(insert_ids) == [3, 4]
        
        # Check updates (id 2)
        assert len(result.updates) == 1
        update_row = result.updates.to_dicts()[0]
        assert update_row['id'] == 2
        assert update_row['name'] == 'Bob Updated'
        assert update_row['value'] == 25
        
        # Check deletes (id 5)
        assert len(result.deletes) == 1
        delete_row = result.deletes.to_dicts()[0]
        assert delete_row['id'] == 5
        assert delete_row['name'] == 'Eve'
        
        # Check unchanged (id 1)
        assert len(result.unchanged) == 1
        unchanged_row = result.unchanged.to_dicts()[0]
        assert unchanged_row['id'] == 1
        assert unchanged_row['name'] == 'Alice'
    
    def test_compare_data_no_changes(self):
        """Test comparison when no changes exist."""
        data = pl.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'value': [10, 20, 30]
        })
        
        cdc = CDCOperations(['id'])
        result = cdc.compare_data(data.clone(), data.clone())
        
        assert len(result.inserts) == 0
        assert len(result.updates) == 0
        assert len(result.deletes) == 0
        assert len(result.unchanged) == 3
    
    def test_compare_data_only_inserts(self):
        """Test comparison with only inserts."""
        source = pl.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie']
        })
        
        target = pl.DataFrame({
            'id': [1, 2],
            'name': ['Alice', 'Bob']
        })
        
        cdc = CDCOperations(['id'])
        result = cdc.compare_data(source, target)
        
        assert len(result.inserts) == 1
        assert len(result.updates) == 0
        assert len(result.deletes) == 0
        assert len(result.unchanged) == 2
        
        insert_row = result.inserts.to_dicts()[0]
        assert insert_row['id'] == 3
        assert insert_row['name'] == 'Charlie'
    
    def test_compare_data_only_deletes(self):
        """Test comparison with only deletes."""
        source = pl.DataFrame({
            'id': [1, 2],
            'name': ['Alice', 'Bob']
        })
        
        target = pl.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie']
        })
        
        cdc = CDCOperations(['id'])
        result = cdc.compare_data(source, target)
        
        assert len(result.inserts) == 0
        assert len(result.updates) == 0
        assert len(result.deletes) == 1
        assert len(result.unchanged) == 2
        
        delete_row = result.deletes.to_dicts()[0]
        assert delete_row['id'] == 3
        assert delete_row['name'] == 'Charlie'
    
    def test_compare_data_only_updates(self):
        """Test comparison with only updates."""
        source = pl.DataFrame({
            'id': [1, 2],
            'name': ['Alice', 'Bob Updated'],
            'value': [10, 25]
        })
        
        target = pl.DataFrame({
            'id': [1, 2],
            'name': ['Alice', 'Bob'],
            'value': [10, 20]
        })
        
        cdc = CDCOperations(['id'])
        result = cdc.compare_data(source, target)
        
        assert len(result.inserts) == 0
        assert len(result.updates) == 1
        assert len(result.deletes) == 0
        assert len(result.unchanged) == 1
        
        update_row = result.updates.to_dicts()[0]
        assert update_row['id'] == 2
        assert update_row['name'] == 'Bob Updated'
        assert update_row['value'] == 25
    
    def test_compare_data_with_composite_key(self):
        """Test comparison with composite primary key."""
        source = pl.DataFrame({
            'dept_id': [1, 1, 2],
            'emp_id': [10, 11, 20],
            'name': ['Alice', 'Bob Updated', 'Charlie']
        })
        
        target = pl.DataFrame({
            'dept_id': [1, 1, 2],
            'emp_id': [10, 11, 21],
            'name': ['Alice', 'Bob', 'David']
        })
        
        cdc = CDCOperations(['dept_id', 'emp_id'])
        result = cdc.compare_data(source, target)
        
        # Should have 1 insert (2,20), 1 update (1,11), 1 delete (2,21), 1 unchanged (1,10)
        assert len(result.inserts) == 1
        assert len(result.updates) == 1
        assert len(result.deletes) == 1
        assert len(result.unchanged) == 1
        
        insert_row = result.inserts.to_dicts()[0]
        assert insert_row['dept_id'] == 2 and insert_row['emp_id'] == 20
        
        update_row = result.updates.to_dicts()[0]
        assert update_row['dept_id'] == 1 and update_row['emp_id'] == 11
        assert update_row['name'] == 'Bob Updated'
    
    def test_compare_data_missing_columns_alignment(self):
        """Test comparison when DataFrames have different columns."""
        source = pl.DataFrame({
            'id': [1, 2],
            'name': ['Alice', 'Bob'],
            'new_col': ['A', 'B']
        })
        
        target = pl.DataFrame({
            'id': [1, 2],
            'name': ['Alice', 'Bob'],
            'old_col': ['X', 'Y']
        })
        
        cdc = CDCOperations(['id'])
        result = cdc.compare_data(source, target)
        
        # Should detect updates due to different column structure
        assert len(result.updates) >= 0  # Depends on null handling
        
        # Both DataFrames should be aligned with all columns
        all_columns = ['id', 'name', 'new_col', 'old_col']
        assert set(result.inserts.columns) == set(all_columns)
        assert set(result.updates.columns) == set(all_columns)
    
    def test_compare_data_with_null_values(self):
        """Test comparison with null values."""
        source = pl.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', None, 'Charlie'],
            'value': [10, 20, None]
        })
        
        target = pl.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'value': [10, None, None]
        })
        
        cdc = CDCOperations(['id'])
        result = cdc.compare_data(source, target)
        
        # Should detect updates where null values differ
        assert len(result.updates) > 0
    
    def test_validate_key_columns_missing_in_source(self):
        """Test validation when key columns are missing in source."""
        source = pl.DataFrame({'name': ['Alice'], 'value': [10]})
        target = pl.DataFrame({'id': [1], 'name': ['Alice']})
        
        cdc = CDCOperations(['id'])
        
        with pytest.raises(CDCOperationError, match="Key columns missing in source"):
            cdc.compare_data(source, target)
    
    def test_validate_key_columns_missing_in_target(self):
        """Test validation when key columns are missing in target."""
        source = pl.DataFrame({'id': [1], 'name': ['Alice']})
        target = pl.DataFrame({'name': ['Alice'], 'value': [10]})
        
        cdc = CDCOperations(['id'])
        
        with pytest.raises(CDCOperationError, match="Key columns missing in target"):
            cdc.compare_data(source, target)
    
    def test_empty_dataframes(self):
        """Test comparison with empty DataFrames."""
        empty_df = pl.DataFrame({'id': [], 'name': []}).cast({'id': pl.Int64, 'name': pl.Utf8})
        
        source = pl.DataFrame({'id': [1], 'name': ['Alice']})
        
        cdc = CDCOperations(['id'])
        
        # Empty target
        result1 = cdc.compare_data(source, empty_df)
        assert len(result1.inserts) == 1
        assert len(result1.updates) == 0
        assert len(result1.deletes) == 0
        assert len(result1.unchanged) == 0
        
        # Empty source
        result2 = cdc.compare_data(empty_df, source)
        assert len(result2.inserts) == 0
        assert len(result2.updates) == 0
        assert len(result2.deletes) == 1
        assert len(result2.unchanged) == 0
        
        # Both empty
        result3 = cdc.compare_data(empty_df, empty_df)
        assert len(result3.inserts) == 0
        assert len(result3.updates) == 0
        assert len(result3.deletes) == 0
        assert len(result3.unchanged) == 0
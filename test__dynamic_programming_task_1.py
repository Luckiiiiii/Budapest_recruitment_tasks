import os
import unittest
from unittest.mock import patch
import pandas as pd
from DynamicProgrammingTask1 import FileReader, ProportionalAllocation


class TestDynamicProgrammingTask1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))

    def test_read_excel_data_valid(self):
        filepath = os.path.join(self.test_dir, "test_data.xlsx")
        with patch('pandas.read_excel', return_value=pd.DataFrame({
            'PRODUCT': ['A', 'B'],
            'CAPACITY': [50, 60]
        })):
            file_reader = FileReader(filepath, ['PRODUCT', 'CAPACITY'])
            data = file_reader.read_excel_data()
            self.assertIsInstance(data, pd.DataFrame)
            self.assertFalse(data.empty)
            self.assertIn('PRODUCT', data.columns)
            self.assertIn('CAPACITY', data.columns)

    def test_read_excel_data_invalid_path(self):
        filepath = os.path.join(self.test_dir, "non_existent_file.xlsx")
        with patch('pandas.read_excel', side_effect=FileNotFoundError):
            file_reader = FileReader(filepath, ['PRODUCT', 'CAPACITY'])
            data = file_reader.read_excel_data()
            self.assertIsInstance(data, pd.DataFrame)
            self.assertTrue(data.empty)

    @patch('builtins.print')
    def test_read_excel_data_invalid_format(self, mock_print):
        filepath = os.path.join(self.test_dir, "test_wrong_data.xlsx")
        with patch('pandas.read_excel', side_effect=ValueError("Usecols do not match columns")):
            file_reader = FileReader(filepath, ['PRODUCT', 'CAPACITY'])
            data = file_reader.read_excel_data()
            self.assertIsInstance(data, pd.DataFrame)
            self.assertTrue(data.empty)
            mock_print.assert_called_with(
                "An error occurred: Usecols do not match columns. Required columns in Input File are missing"
            )

    def test_allocate_capacity_valid(self):
        data = pd.DataFrame({
            'PRODUCT': ['A', 'B', 'C'],
            'SHARE': [0.3, 0.5, 0.2],
            'GROUP CAPACITY': [100, 100, 100],
            'CAPACITY': [30, 50, 20],
            'INDIVIDUAL LIMIT': [40, 60, 30],
            'OVERLIMIT': [0, 0, 0]
        })

        allocator = ProportionalAllocation()
        result = allocator.allocate(data)
        self.assertIn('ALLOCATION', result.columns)
        self.assertEqual(result['ALLOCATION'].sum(), 100)
        self.assertTrue(all(result['ALLOCATION'] <= result['INDIVIDUAL LIMIT']))

    def test_allocate_capacity_empty_dataframe(self):
        data = pd.DataFrame(columns=['PRODUCT', 'SHARE', 'GROUP CAPACITY', 'CAPACITY', 'INDIVIDUAL LIMIT', 'OVERLIMIT'])
        allocator = ProportionalAllocation()
        result = allocator.allocate(data)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

    def test_allocate_capacity_invalid_columns(self):
        data = pd.DataFrame({
            'WRONG_COLUMN': [1, 2, 3]
        })
        with self.assertRaises(KeyError):
            allocator = ProportionalAllocation()
            allocator.allocate(data)  # {KeyError}KeyError('GROUP CAPACITY',) is thrown here

    def test_allocate_capacity_over_limit(self):
        # Test with a DataFrame where allocation exceeds group capacity
        data = pd.DataFrame({
            'PRODUCT': ['A', 'B'],
            'SHARE': [0.7, 0.4],
            'GROUP CAPACITY': [100, 100],
            'CAPACITY': [70, 40],
            'INDIVIDUAL LIMIT': [80, 50],
            'OVERLIMIT': [0, 0]
        })

        allocator = ProportionalAllocation()
        result = allocator.allocate(data)
        self.assertLessEqual(result['ALLOCATION'].sum(), 100)
        self.assertTrue(all(result['ALLOCATION'] <= result['GROUP CAPACITY']))
        self.assertTrue(all(result['NEW ALLOC. SHARE'] <= 1))
        self.assertTrue(all(result['ALLOCATION'] <= result['INDIVIDUAL LIMIT']))

    def test_allocate_capacity_extreme_easy_case(self):
        # Test for TDD/debuging purposes
        data = pd.DataFrame({
            'PRODUCT': ['A', 'B'],
            'SHARE': [0.5, 0.5],
            'GROUP CAPACITY': [4, 4],
            'CAPACITY': [1, 2],
            'INDIVIDUAL LIMIT': [1, 2],
            'OVERLIMIT': [0, 1]
        })

        allocator = ProportionalAllocation()
        result = allocator.allocate(data)
        print(result)
        self.assertLessEqual(result['ALLOCATION'].sum(), 3)
        self.assertTrue(all(result['ALLOCATION'] <= result['GROUP CAPACITY']))
        self.assertTrue(all(result['NEW ALLOC. SHARE'] <= 1))
        self.assertTrue(all(result['ALLOCATION'] <= result['INDIVIDUAL LIMIT']))


if __name__ == '__main__':
    unittest.main()

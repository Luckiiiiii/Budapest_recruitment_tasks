import os
import unittest
from unittest.mock import patch
import pandas as pd
from dynamic_programming_task_1 import FileReader, ProportionalAllocation, CapacityAllocator, format_output_columns


class TestDynamicProgrammingTask1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))

    @patch.object(FileReader, 'read_excel_data')
    def test_run_with_empty_data(self, mock_read_excel_data):
        mock_read_excel_data.return_value = pd.DataFrame()

        allocator = CapacityAllocator("dummy_path",
                                      ['PRODUCT', 'SHARE', 'GROUP CAPACITY', 'CAPACITY', 'INDIVIDUAL LIMIT',
                                       'OVERLIMIT'], ProportionalAllocation())
        result = allocator.run()

        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

    @patch.object(FileReader, 'read_excel_data')
    def test_run_with_valid_data(self, mock_read_excel_data):
        mock_data = pd.DataFrame({
            'PRODUCT': ['A', 'B'],
            'SHARE': [0.3, 0.7],
            'GROUP CAPACITY': [100, 100],
            'CAPACITY': [30, 70],
            'INDIVIDUAL LIMIT': [50, 80],
            'OVERLIMIT': [0, 0]
        })
        mock_read_excel_data.return_value = mock_data

        allocator = CapacityAllocator("dummy_path",
                                      ['PRODUCT', 'SHARE', 'GROUP CAPACITY', 'CAPACITY', 'INDIVIDUAL LIMIT',
                                       'OVERLIMIT'], ProportionalAllocation())
        result = allocator.run()

        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('ALLOCATION', result.columns)
        self.assertEqual(result['ALLOCATION'].sum(), 100)

    @patch.object(FileReader, 'read_excel_data')
    def test_run_with_invalid_columns(self, mock_read_excel_data):
        mock_data = pd.DataFrame({
            'WRONG_COLUMN': [1, 2, 3]
        })
        mock_read_excel_data.return_value = mock_data

        allocator = CapacityAllocator("dummy_path",
                                      ['PRODUCT', 'SHARE', 'GROUP CAPACITY', 'CAPACITY', 'INDIVIDUAL LIMIT',
                                       'OVERLIMIT'], ProportionalAllocation())
        with self.assertRaises(KeyError):
            allocator.run()

    def test_calculates_remaining_demand_correctly(self):
        allocation_strategy = ProportionalAllocation()
        demands = pd.Series([100, 200, 300])
        remaining_products = [0, 2]
        remaining_demand = allocation_strategy._calculate_remaining_demand(demands, remaining_products)
        self.assertEqual(remaining_demand, 400)

    def test_handles_empty_remaining_products(self):
        allocation_strategy = ProportionalAllocation()
        demands = pd.Series([100, 200, 300])
        remaining_products = []
        remaining_demand = allocation_strategy._calculate_remaining_demand(demands, remaining_products)
        self.assertEqual(remaining_demand, 0)

    def test_handles_single_remaining_product(self):
        allocation_strategy = ProportionalAllocation()
        demands = pd.Series([100, 200, 300])
        remaining_products = [1]
        remaining_demand = allocation_strategy._calculate_remaining_demand(demands, remaining_products)
        self.assertEqual(remaining_demand, 200)

    def test_handles_all_remaining_products(self):
        allocation_strategy = ProportionalAllocation()
        demands = pd.Series([100, 200, 300])
        remaining_products = [0, 1, 2]
        remaining_demand = allocation_strategy._calculate_remaining_demand(demands, remaining_products)
        self.assertEqual(remaining_demand, 600)

    def test_calculates_remaining_demand_correctly(self):
        allocation_strategy = ProportionalAllocation()
        demands = pd.Series([100, 200, 300])
        remaining_products = [0, 2]
        remaining_demand = allocation_strategy._calculate_remaining_demand(demands, remaining_products)
        self.assertEqual(remaining_demand, 400)

    def test_handles_empty_remaining_products(self):
        allocation_strategy = ProportionalAllocation()
        demands = pd.Series([100, 200, 300])
        remaining_products = []
        remaining_demand = allocation_strategy._calculate_remaining_demand(demands, remaining_products)
        self.assertEqual(remaining_demand, 0)

    def test_handles_single_remaining_product(self):
        allocation_strategy = ProportionalAllocation()
        demands = pd.Series([100, 200, 300])
        remaining_products = [1]
        remaining_demand = allocation_strategy._calculate_remaining_demand(demands, remaining_products)
        self.assertEqual(remaining_demand, 200)

    def test_handles_all_remaining_products(self):
        allocation_strategy = ProportionalAllocation()
        demands = pd.Series([100, 200, 300])
        remaining_products = [0, 1, 2]
        remaining_demand = allocation_strategy._calculate_remaining_demand(demands, remaining_products)
        self.assertEqual(remaining_demand, 600)

    def test_distributes_surplus_correctly(self):
        allocation_strategy = ProportionalAllocation()
        allocation = [50, 100, 150]
        demands = pd.Series([100, 200, 300])
        limits = pd.Series([100, 200, 300])
        remaining_products = [0, 1, 2]
        remaining_demand = 600
        surplus = 100
        updated_allocation = allocation_strategy._distribute_surplus(allocation, demands, limits, remaining_products,
                                                                     remaining_demand, surplus)
        self.assertAlmostEqual(updated_allocation[0], 66.67, places=2)
        self.assertAlmostEqual(updated_allocation[1], 133.33, places=2)
        self.assertAlmostEqual(updated_allocation[2], 200.0, places=2)

    def test_handles_no_remaining_products(self):
        allocation_strategy = ProportionalAllocation()
        allocation = [100, 200, 300]
        demands = pd.Series([100, 200, 300])
        limits = pd.Series([100, 200, 300])
        remaining_products = []
        remaining_demand = 0
        surplus = 100
        updated_allocation = allocation_strategy._distribute_surplus(allocation, demands, limits, remaining_products,
                                                                     remaining_demand, surplus)
        self.assertEqual(updated_allocation, [100, 200, 300])

    def test_respects_individual_limits(self):
        allocation_strategy = ProportionalAllocation()
        allocation = [50, 100, 150]
        demands = pd.Series([100, 200, 300])
        limits = pd.Series([60, 150, 200])
        remaining_products = [0, 1, 2]
        remaining_demand = 600
        surplus = 100
        updated_allocation = allocation_strategy._distribute_surplus(allocation, demands, limits, remaining_products,
                                                                     remaining_demand, surplus)
        self.assertEqual(updated_allocation[0], 60)
        self.assertAlmostEqual(updated_allocation[1], 133.33, places=2)
        self.assertEqual(updated_allocation[2], 200)

    def test_handles_zero_surplus(self):
        allocation_strategy = ProportionalAllocation()
        allocation = [50, 100, 150]
        demands = pd.Series([100, 200, 300])
        limits = pd.Series([100, 200, 300])
        remaining_products = [0, 1, 2]
        remaining_demand = 600
        surplus = 0
        updated_allocation = allocation_strategy._distribute_surplus(allocation, demands, limits, remaining_products,
                                                                     remaining_demand, surplus)
        self.assertEqual(updated_allocation, [50, 100, 150])

    def test_calculates_additional_capacity_correctly(self):
        allocation_strategy = ProportionalAllocation()
        additional_capacity = allocation_strategy._calculate_additional_capacity(100, 300, 90)
        self.assertEqual(additional_capacity, 30)

    def test_handles_zero_remaining_demand(self):
        allocation_strategy = ProportionalAllocation()
        additional_capacity = allocation_strategy._calculate_additional_capacity(100, 0, 90)
        self.assertEqual(additional_capacity, 0)

    def test_handles_zero_surplus(self):
        allocation_strategy = ProportionalAllocation()
        additional_capacity = allocation_strategy._calculate_additional_capacity(100, 300, 0)
        self.assertEqual(additional_capacity, 0)

    def test_handles_zero_demand(self):
        allocation_strategy = ProportionalAllocation()
        additional_capacity = allocation_strategy._calculate_additional_capacity(0, 300, 90)
        self.assertEqual(additional_capacity, 0)

    def test_handles_negative_values(self):
        allocation_strategy = ProportionalAllocation()
        additional_capacity = allocation_strategy._calculate_additional_capacity(-100, 300, 90)
        self.assertEqual(additional_capacity, -30)

    # TestFormatOutputColumns(unittest.TestCase):
    def test_formats_share_and_new_alloc_share_as_percentages(self):
        data = pd.DataFrame({
            'SHARE': [0.1, 0.2, 0.3],
            'NEW ALLOC. SHARE': [0.1, 0.2, None],
            'OVERLIMIT': [True, False, True],
            'ALLOCATION': [10, 20, 30]
        })
        formatted_data = format_output_columns(data)
        self.assertEqual(formatted_data['SHARE'].tolist(), ['10.0%', '20.0%', '30.0%'])
        self.assertEqual(formatted_data['NEW ALLOC. SHARE'].tolist(), ['10.0%', '20.0%', None])

    def test_formats_overlimit_as_true_or_false(self):
        data = pd.DataFrame({
            'SHARE': [0.1, 0.2],
            'NEW ALLOC. SHARE': [0.1, 0.2],
            'OVERLIMIT': [True, False],
            'ALLOCATION': [10, 20]
        })
        formatted_data = format_output_columns(data)
        self.assertEqual(formatted_data['OVERLIMIT'].tolist(), ['True', 'False'])

    def test_formats_allocation_to_one_decimal_place(self):
        data = pd.DataFrame({
            'SHARE': [0.1, 0.2],
            'NEW ALLOC. SHARE': [0.1, 0.2],
            'OVERLIMIT': [True, False],
            'ALLOCATION': [10.123, 20.456]
        })
        formatted_data = format_output_columns(data)
        self.assertEqual(formatted_data['ALLOCATION'].tolist(), ['10.1', '20.5'])

    def test_handles_empty_dataframe(self):
        data = pd.DataFrame(columns=['SHARE', 'NEW ALLOC. SHARE', 'OVERLIMIT', 'ALLOCATION'])
        formatted_data = format_output_columns(data)
        self.assertTrue(formatted_data.empty)

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

from unittest.mock import patch
from material_balance_task_2 import FileReader
import unittest
import pandas as pd
from material_balance_task_2 import MaterialProcessor


class TestFileReader(unittest.TestCase):

    @patch('pandas.read_excel')
    def test_read_excel_data_file_not_found(self, mock_read_excel):
        mock_read_excel.side_effect = FileNotFoundError

        file_reader = FileReader("dummy_path")
        data, product_no, production_backlog, stock_at_hand = file_reader.read_excel_data()

        self.assertTrue(data.empty)
        self.assertIsNone(product_no)
        self.assertIsNone(production_backlog)
        self.assertIsNone(stock_at_hand)

    @patch('pandas.read_excel')
    def test_read_excel_data_invalid_format(self, mock_read_excel):
        mock_read_excel.side_effect = ValueError("Invalid format")

        file_reader = FileReader("dummy_path")
        data, product_no, production_backlog, stock_at_hand = file_reader.read_excel_data()

        self.assertTrue(data.empty)
        self.assertIsNone(product_no)
        self.assertIsNone(production_backlog)
        self.assertIsNone(stock_at_hand)


class TestMaterialProcessor(unittest.TestCase):

    def test_calculates_correct_material_balance(self):
        # Input data
        data = pd.DataFrame({
            'Demand': [100, 200, 300],
            'Confirmed Delivery Sum': [50, 150, 250]
        })

        # Initialize processor with inputs
        processor = MaterialProcessor(data, 'Product1', 1000, 500)

        # Calculate material balance
        result = processor.calculate_material_balance()

        # Expected results (calculated based on the implemented method logic)
        expected = [-600, -750, -900]

        # Assert the calculated values match the expected values
        self.assertEqual(result['New Material Balance'].tolist(), expected)

    def test_handles_missing_required_columns(self):
        data = pd.DataFrame({
            'Demand': [100, 200, 300]
        })
        processor = MaterialProcessor(data, 'Product1', 1000, 500)
        with self.assertRaises(ValueError):
            processor.calculate_material_balance()

    def test_handles_empty_dataframe(self):
        # Create an empty DataFrame with necessary columns
        data = pd.DataFrame(columns=['Demand', 'Confirmed Delivery Sum'])

        # Initialize processor with empty DataFrame
        processor = MaterialProcessor(data, 'Product1', 1000, 500)

        # Perform material balance calculation
        result = processor.calculate_material_balance()

        # Assert the result is an empty DataFrame
        self.assertTrue(result.empty, "The method should return an empty DataFrame when input is empty.")

    # def test_handles_zero_demand_and_delivery(self):
    #     data = pd.DataFrame({
    #         'Demand': [0, 0, 0],
    #         'Confirmed Delivery Sum': [0, 0, 0]
    #     })
    #     processor = MaterialProcessor(data, 'Product1', 1000, 500)
    #     result = processor.calculate_material_balance()
    #     expected = [1500, 1500, 1500]
    #     self.assertEqual(result['New Material Balance'].tolist(), expected)
    #
    # def test_handles_negative_values(self):
    #     data = pd.DataFrame({
    #         'Demand': [-100, -200, -300],
    #         'Confirmed Delivery Sum': [-50, -150, -250]
    #     })
    #     processor = MaterialProcessor(data, 'Product1', 1000, 500)
    #     result = processor.calculate_material_balance()
    #     expected = [1400, 1350, 1300]
    #     self.assertEqual(result['New Material Balance'].tolist(), expected)

    # def test_handles_zero_demand_and_delivery2(self):
    #     data = pd.DataFrame({
    #         'Demand': [0, 0, 0],
    #         'Confirmed Delivery Sum': [0, 0, 0]
    #     })
    #     processor = MaterialProcessor(data, 'Product1', 1000, 500)
    #     result = processor.calculate_material_balance()
    #     expected = [1500, 1500, 1500]
    #     self.assertEqual(result['New Material Balance'].tolist(), expected)
    #
    # def test_handles_negative_value2(self):
    #     data = pd.DataFrame({
    #         'Demand': [100, 150, 200],
    #         'Confirmed Delivery Sum': [200, 100, 50]
    #     })
    #     processor = MaterialProcessor(data, 'Product1', 1000, 500)
    #     result = processor.calculate_material_balance()
    #     expected = [1400, 1350, 1300]
    #     self.assertEqual(result['New Material Balance'].tolist(), expected)


if __name__ == '__main__':
    unittest.main()

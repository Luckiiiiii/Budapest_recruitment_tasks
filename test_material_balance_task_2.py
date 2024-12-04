import argparse
import os
from unittest import mock
from unittest.mock import patch
from material_balance_task_2 import FileReader, parse_arguments, process_workflow, ChartPlotter
import unittest
import pandas as pd
from material_balance_task_2 import MaterialProcessor


class TestFileReader(unittest.TestCase):

    @patch('material_balance_task_2.pd.read_excel')
    def test_read_and_validate_excel_valid_data(self, mock_read_excel):
        mock_data = pd.DataFrame([[1] * 30] * 26)
        mock_read_excel.return_value = mock_data
        file_reader = FileReader('dummy_path')
        result = file_reader.read_and_validate_excel()
        self.assertFalse(result.empty)

    @patch('material_balance_task_2.pd.read_excel')
    def test_read_and_validate_excel_insufficient_data(self, mock_read_excel):
        mock_data = pd.DataFrame([[1] * 30] * 25)
        mock_read_excel.return_value = mock_data
        file_reader = FileReader('dummy_path')
        result = file_reader.read_and_validate_excel()
        self.assertTrue(result.empty)

    @patch('material_balance_task_2.pd.read_excel')
    def test_read_and_validate_excel_file_not_found(self, mock_read_excel):
        mock_read_excel.side_effect = FileNotFoundError
        file_reader = FileReader('dummy_path')
        result = file_reader.read_and_validate_excel()
        self.assertTrue(result.empty)

    @patch('material_balance_task_2.pd.read_excel')
    def test_read_and_validate_excel_general_exception(self, mock_read_excel):
        mock_read_excel.side_effect = Exception
        file_reader = FileReader('dummy_path')
        result = file_reader.read_and_validate_excel()
        self.assertTrue(result.empty)

    def test_extract_data_valid_data(self):
        data = pd.DataFrame([[1] * 30] * 26)
        file_reader = FileReader('dummy_path')
        final_data, product_no, production_backlog, stock_at_hand = file_reader.extract_data(data)
        self.assertFalse(final_data.empty)
        self.assertIsNotNone(product_no)
        self.assertIsNotNone(production_backlog)
        self.assertIsNotNone(stock_at_hand)

    def test_extract_data_empty_data(self):
        data = pd.DataFrame()
        file_reader = FileReader('dummy_path')
        final_data, product_no, production_backlog, stock_at_hand = file_reader.extract_data(data)
        self.assertTrue(final_data.empty)
        self.assertIsNone(product_no)
        self.assertIsNone(production_backlog)
        self.assertIsNone(stock_at_hand)


class TestMaterialProcessor(unittest.TestCase):

    def test_validates_empty_dataframe(self):
        data = pd.DataFrame()
        processor = MaterialProcessor(data, "FG-AA123456", 50000, 300000)
        result = processor.prepare_data_for_calculation()
        self.assertTrue(result.empty)

    def test_raises_error_for_missing_columns(self):
        data = pd.DataFrame({'Date': [202448, 202449], 'Demand': [1000, 2000]})
        processor = MaterialProcessor(data, "FG-AA123456", 50000, 300000)
        with self.assertRaises(ValueError):
            processor.prepare_data_for_calculation()

    def test_converts_date_correctly(self):
        data = pd.DataFrame(
            {'Date': [202448, 202449], 'Demand': [1000, 2000], 'Confirmed Delivery Sum': [500, 600]})
        processor = MaterialProcessor(data, "FG-AA123456", 50000, 300000)
        result = processor.prepare_data_for_calculation()
        expected_dates = ['2024-48', '2024-49']
        self.assertEqual(result['Date'].tolist(), expected_dates)

    def test_calculates_material_balance_correctly(self):
        data = pd.DataFrame({'Date': [202448, 202449], 'Demand': [1000, 2000], 'Confirmed Delivery Sum': [500, 600]})
        processor = MaterialProcessor(data, "FG-AA123456", 50000, 300000)
        processor.prepare_data_for_calculation()
        result = processor.perform_material_balance_calculation()
        expected_balance = [249000, 247500]
        self.assertEqual(result['New Material Balance'].tolist(), expected_balance)

    def test_handles_no_date_column(self):
        data = pd.DataFrame({'Demand': [1000, 2000], 'Confirmed Delivery Sum': [500, 600]})
        processor = MaterialProcessor(data, "FG-AA123456", 50000, 300000)
        result = processor.prepare_data_for_calculation()
        self.assertNotIn('Date', result.columns)


class TestChartPlotter(unittest.TestCase):
    @patch('matplotlib.pyplot.show')
    def test_plots_chart_with_valid_data(self, mock_show):
        data = pd.DataFrame({
            'Date': ['202448', '202449'],
            'New Material Balance': [249000, 249100],
            'Demand': [50000, 60000],
            'Confirmed Delivery Sum': [300000, 310000]
        })
        plotter = ChartPlotter(data)
        plotter.plot_line_chart()
        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_does_not_plot_chart_with_empty_data(self, mock_show):
        data = pd.DataFrame()
        plotter = ChartPlotter(data)
        plotter.plot_line_chart()
        mock_show.assert_not_called()

    @patch('matplotlib.pyplot.show')
    def test_does_not_plot_chart_with_missing_columns(self, mock_show):
        data = pd.DataFrame({
            'Date': ['202448', '202449'],
            'New Material Balance': [249000, 249100]
        })
        plotter = ChartPlotter(data)
        plotter.plot_line_chart()
        mock_show.assert_not_called()


class TestArgumentParsing(unittest.TestCase):

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(filepath=None))
    @patch('os.path.exists', return_value=True)
    def test_returns_default_filepath_when_no_argument_provided(self, mock_exists, mock_args):
        expected_path = os.path.abspath("./Input_data_task_2/2. Task.xlsx")
        result = parse_arguments()
        self.assertEqual(result, expected_path)

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(filepath='./custom_path.xlsx'))
    @patch('os.path.exists', return_value=True)
    def test_returns_provided_filepath_when_argument_provided(self, mock_exists, mock_args):
        result = parse_arguments()
        self.assertEqual(result, './custom_path.xlsx')

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(filepath='./non_existent_path.xlsx'))
    @patch('os.path.exists', return_value=False)
    def test_returns_none_when_filepath_does_not_exist(self, mock_exists, mock_args):
        result = parse_arguments()
        self.assertIsNone(result)


class TestProcessWorkflow(unittest.TestCase):

    @patch('material_balance_task_2.MaterialBalanceWorkflow.run')
    @patch('material_balance_task_2.ChartPlotter.plot_line_chart')
    def test_processes_valid_workflow(self, mock_plot, mock_run):
        mock_run.return_value = (
            pd.DataFrame({'Date': ['202448', '202449'], 'New Material Balance': [249000, 249100]}), 'FG-AA123456',
            50000, 300000)
        with patch('builtins.print') as mock_print:
            process_workflow('valid_path.xlsx')
            mock_print.assert_called_with(mock.ANY)
            mock_plot.assert_called_once()

    @patch('material_balance_task_2.MaterialBalanceWorkflow.run')
    def test_handles_empty_result(self, mock_run):
        mock_run.return_value = (pd.DataFrame(), None, None, None)
        with patch('builtins.print') as mock_print:
            process_workflow('empty_path.xlsx')
            mock_print.assert_called_with("No valid data to process.")

    @patch('material_balance_task_2.MaterialBalanceWorkflow.run')
    @patch('material_balance_task_2.ChartPlotter.plot_line_chart')
    def test_processes_workflow_with_missing_columns(self, mock_plot, mock_run):
        mock_run.return_value = (pd.DataFrame({'Date': ['202448', '202449']}), 'FG-AA123456', 50000, 300000)
        with patch('builtins.print') as mock_print:
            process_workflow('missing_columns_path.xlsx')
            mock_print.assert_called_with(mock.ANY)
            mock_plot.assert_not_called()


if __name__ == '__main__':
    unittest.main()

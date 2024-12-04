import argparse
import os
import logging
import warnings

import pandas as pd
import matplotlib.pyplot as plt

# Configure logging
warnings.filterwarnings("ignore", message="Using categorical units to plot a list of strings.*")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class FileReader:
    """
    Handles file reading and basic preprocessing for an Excel file.
    """

    def __init__(self, filepath):
        self.filepath = filepath

    def read_and_validate_excel(self):
        """
        Reads an Excel file and validates its content.

        Returns:
            pd.DataFrame: DataFrame containing the Excel data.
        """
        try:
            data = pd.read_excel(self.filepath, header=None)
            if data.empty or len(data) < 26:
                logging.error("The input data is insufficient or empty.")
                return pd.DataFrame()
            return data
        except FileNotFoundError:
            logging.error(f"Error: The file at {self.filepath} was not found.")
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"An error occurred: {e}. Please ensure the data format is correct.")
            return pd.DataFrame()

    def extract_data(self, data):
        """
        Extracts specific rows and columns from the DataFrame.

        Args:
            data (pd.DataFrame): DataFrame containing the Excel data.

        Returns:
            tuple: A tuple containing:
                - pd.DataFrame: Transposed DataFrame with relevant data for product analysis.
                - str: Product No.
                - float: Production Backlog.
                - float: Stock at Hand.
        """
        if data.empty:
            return pd.DataFrame(), None, None, None

        product_no = data.iloc[0, 0]
        production_backlog = data.iloc[1, 3]
        stock_at_hand = data.iloc[2, 3]

        final_data = pd.DataFrame({
            'Date': data.iloc[2, 4:].values,
            'Demand': data.iloc[3, 4:].values,
            'Confirmed Delivery ETA (Smith Ltd)': data.iloc[4, 4:].values,
            'Confirmed Delivery ETA (Common Ltd)': data.iloc[5, 4:].values,
            'Confirmed Delivery Sum': data.iloc[24, 4:].values
        })

        whole_table_ETA_sum = data.iloc[4:23, 4:].apply(pd.to_numeric, errors='coerce').sum(axis=0)
        final_data['Confirmed Delivery Sum'] = whole_table_ETA_sum.values

        logging.info(f"Data extraction successful for product: {product_no}")
        logging.info(f"Production Backlog: {production_backlog}")
        logging.info(f"Stock at Hand: {stock_at_hand}")
        return final_data, product_no, production_backlog, stock_at_hand


class MaterialProcessor:
    """
    Processes the data and performs calculations for material balance.
    """

    def __init__(self, data, product_no, production_backlog, stock_at_hand):
        self.data = data
        self.product_no = product_no
        self.production_backlog = production_backlog
        self.stock_at_hand = stock_at_hand

    def prepare_data_for_calculation(self):
        """
        Prepares the data by validating inputs and preprocessing for material balance calculations.

        Returns:
            pd.DataFrame: Validated and preprocessed DataFrame.
        """
        if self.data.empty:
            logging.warning("The input DataFrame is empty. Returning without preparation.")
            return self.data

        required_columns = ['Demand', 'Confirmed Delivery Sum']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in data: {missing_columns}")

        self.data = self.data.apply(pd.to_numeric, errors='coerce').fillna(0).astype(int, errors='ignore')

        if 'Date' in self.data.columns:
            self.data['Date'] = pd.to_datetime(self.data['Date'].astype(str) + '0', format='%Y%W%w').dt.strftime(
                '%Y-%U')

        self.data['New Material Balance'] = None
        logging.info(f"Data preparation complete for product: {self.product_no}")

        return self.data

    def perform_material_balance_calculation(self):
        """
        Calculates the 'New Material Balance' column based on given inputs.

        Returns:
            pd.DataFrame: DataFrame with updated material balance calculations.
        """
        if self.data.empty:
            logging.warning("The input DataFrame is empty. Returning without calculation.")
            return self.data

        logging.info(f"Starting material balance calculations for product: {self.product_no}")

        self.data.loc[0, 'New Material Balance'] = self.stock_at_hand - self.production_backlog - \
                                                   self.data['Demand'].iloc[0]

        for i in range(1, len(self.data)):
            previous_new_balance = self.data.loc[i - 1, 'New Material Balance']
            confirmed_delivery_sum = self.data.loc[i - 1, 'Confirmed Delivery Sum']
            current_demand = self.data.loc[i, 'Demand']
            self.data.loc[i, 'New Material Balance'] = previous_new_balance + confirmed_delivery_sum - current_demand

        logging.info("Material balance calculations completed.")
        return self.data


class MaterialBalanceWorkflow:
    """
    Orchestrates the reading, processing, and calculation of material balance.
    """

    def __init__(self, filepath):
        self.file_reader = FileReader(filepath)

    def run(self):
        """
        Reads data and applies preprocessing and calculations.

        Returns:
            tuple: Processed DataFrame and product parameters.
        """
        excel_data = self.file_reader.read_and_validate_excel()

        # Pass excel_data explicitly to extract_data
        data, product_no, production_backlog, stock_at_hand = self.file_reader.extract_data(excel_data)

        if data.empty:
            logging.warning("No valid data or parameters to process.")
            return pd.DataFrame(), None, None, None

        processor = MaterialProcessor(data, product_no, production_backlog, stock_at_hand)
        preprocessed_data = processor.prepare_data_for_calculation()
        if preprocessed_data.empty:
            return pd.DataFrame(), None, None, None

        return processor.perform_material_balance_calculation(), product_no, production_backlog, stock_at_hand


class ChartPlotter:
    """
    Handles plotting charts for the given data.
    """

    def __init__(self, data):
        self.data = data

    def plot_line_chart(self):
        """
        Plots a line chart with:
        - X-axis: 'Date'
        - Y-axis: 'New Material Balance', 'Demand', 'Confirmed Delivery Sum'
        """
        if self.data.empty:
            logging.warning("The input DataFrame is empty. Cannot plot chart.")
            return

        required_columns = ['Date', 'New Material Balance', 'Demand', 'Confirmed Delivery Sum']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            logging.error(f"Missing required columns for plotting: {missing_columns}")
            return

        try:
            self._prepare_data_for_plotting()
            self._plot_lines()
            self._annotate_max_min_values()
            plt.tight_layout()
            plt.show()
        except Exception as e:
            logging.error(f"An error occurred while plotting the chart: {e}")

    def _prepare_data_for_plotting(self):
        """
        Prepares the data for plotting by converting types and setting up the figure.
        """
        self.data['Date'] = self.data['Date'].astype(str)
        for column in ['New Material Balance', 'Demand', 'Confirmed Delivery Sum']:
            self.data[column] = pd.to_numeric(self.data[column], errors='coerce')
        plt.figure(figsize=(15, 8))

    def _plot_lines(self):
        """
        Plots the lines for 'New Material Balance', 'Demand', and 'Confirmed Delivery Sum'.
        """
        plt.plot(self.data['Date'], self.data['New Material Balance'], label='New Material Balance', marker='o')
        plt.plot(self.data['Date'], self.data['Demand'], label='Demand', linestyle='--')
        plt.plot(self.data['Date'], self.data['Confirmed Delivery Sum'], label='Confirmed Delivery Sum', linestyle='-.')

        plt.title('Material Balance and Related Metrics Over Time', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Values', fontsize=12)
        plt.xticks(rotation=45, fontsize=10)

        min_y = min(self.data['New Material Balance'].min(), self.data['Demand'].min(),
                    self.data['Confirmed Delivery Sum'].min())
        max_y = max(self.data['New Material Balance'].max(), self.data['Demand'].max(),
                    self.data['Confirmed Delivery Sum'].max())
        plt.ylim(min_y - 5000, max_y + 5000)
        plt.yticks(fontsize=10)
        plt.legend(fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)

    def _annotate_max_min_values(self):
        """
        Annotates the maximum and minimum values on the plot.
        """
        for column in ['New Material Balance', 'Demand', 'Confirmed Delivery Sum']:
            max_value = self.data[column].max()
            min_value = self.data[column].min()
            max_date = self.data.loc[self.data[column].idxmax(), 'Date']
            min_date = self.data.loc[self.data[column].idxmin(), 'Date']
            plt.annotate(f'Max: {max_value}', xy=(max_date, max_value), xytext=(max_date, max_value + 0.05 * max_value),
                         arrowprops=dict(facecolor='green', shrink=0.05), fontsize=10, color='green')
            plt.annotate(f'Min: {min_value}', xy=(min_date, min_value), xytext=(min_date, min_value - 0.05 * max_value),
                         arrowprops=dict(facecolor='red', shrink=0.05), fontsize=10, color='red')


def parse_arguments():
    """
    Parses command line arguments.

    Returns:
        str: The file path to the input Excel file.
    """
    parser = argparse.ArgumentParser(description="Run the Material Balance Workflow with a specified file path.")
    parser.add_argument(
        "--filepath", type=str,
        help="Path to the input Excel file. If not provided, the default path will be used.",
    )
    args = parser.parse_args()

    default_filepath = os.path.abspath("./Input_data_task_2/2. Task.xlsx")
    filepath = args.filepath if args.filepath else default_filepath

    if not os.path.exists(filepath):
        logging.error(f"File path does not exist: {filepath}")
        print(f"Error: The specified file path does not exist: {filepath}")
        return None

    logging.info(f"Using file path: {filepath}")
    print(f"Using file path: {filepath}")
    return filepath


def process_workflow(filepath):
    """
    Processes the workflow for material balance calculations.

    Args:
        filepath (str): The file path to the input Excel file.
    """
    workflow = MaterialBalanceWorkflow(filepath)
    result, product_no, production_backlog, stock_at_hand = workflow.run()

    if not result.empty and 'New Material Balance' in result.columns:
        transposed_data = result.transpose()
        transposed_data.columns = transposed_data.iloc[0]
        transposed_data = transposed_data[1:]

        pd.set_option('display.max_columns', 56)
        pd.set_option('display.width', 255)
        logging.info("Final Parsed Data:")
        print(transposed_data)

        ChartPlotter(result).plot_line_chart()
    else:
        logging.warning("No valid data to process.")
        print("No valid data to process.")


def main():
    filepath = parse_arguments()
    if filepath:
        process_workflow(filepath)


if __name__ == "__main__":
    main()
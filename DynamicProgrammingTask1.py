import os

import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class FileReader:
    """
    Handles file reading and basic preprocessing.
    """

    def __init__(self, filepath, columns_to_extract):
        self.filepath = filepath
        self.columns_to_extract = columns_to_extract

    def read_excel_data(self):
        """
        Reads an Excel file and filters rows based on the columns_to_extract.

        Returns:
            pd.DataFrame: Processed DataFrame.
        """
        try:
            data = pd.read_excel(self.filepath, usecols=self.columns_to_extract)

            data = data[data['PRODUCT'].notnull()]

            return data
        except FileNotFoundError:
            print(f"Error: The file at {self.filepath} was not found.")
            return pd.DataFrame()
        except Exception as e:
            print(f"An error occurred: {e}. Required columns in Input File are missing")
            return pd.DataFrame()


def format_output_columns(data):
    # Format 'SHARE' and 'NEW ALLOC. SHARE' as percentages with one decimal place
    data['SHARE'] = (data['SHARE'] * 100).apply(lambda x: f"{x:.1f}%")
    data['NEW ALLOC. SHARE'] = data['NEW ALLOC. SHARE'].apply(lambda x: f"{x * 100:.1f}%" if pd.notnull(x) else None)

    # Format 'OVERLIMIT' to display as 'True' or 'False'
    data['OVERLIMIT'] = data['OVERLIMIT'].apply(lambda x: 'True' if x else 'False')

    # Format 'ALLOCATION' to one decimal place for display
    data['ALLOCATION'] = data['ALLOCATION'].apply(lambda x: f"{x:.1f}")

    return data


class AllocationStrategy:
    """
    Abstract base class for allocation strategies.
    """

    def allocate(self, data):
        raise NotImplementedError("Subclasses should implement the allocate method.")


class ProportionalAllocation(AllocationStrategy):
    """
    Implements proportional allocation based on demand.
    """

    def allocate(self, data):
        required_columns = {'GROUP CAPACITY', 'CAPACITY', 'INDIVIDUAL LIMIT'}
        if not required_columns.issubset(data.columns):
            missing_columns = required_columns - set(data.columns)
            logging.error(
                f"Missing required columns. Expected columns: {required_columns}, but got: {set(data.columns)}")
            raise KeyError(
                f"Missing required columns. Expected columns: {required_columns}, "
                f"but got: {set(data.columns)}"
            )

        logging.info("All required columns are present.")

        if data.empty:
            logging.warning("The input DataFrame is empty. Returning an empty DataFrame with an 'ALLOCATION' column.")
            return pd.DataFrame(columns=data.columns.tolist() + ['ALLOCATION'])

        logging.info("Input DataFrame is not empty. Proceeding with allocation process.")

        # Extract necessary columns
        group_capacity = data['GROUP CAPACITY'].iloc[0]
        demands = data['CAPACITY']
        limits = data['INDIVIDUAL LIMIT'].fillna(float('inf'))

        logging.debug(f"Group capacity: {group_capacity}")
        logging.debug(f"Demands: {demands.tolist()}")
        logging.debug(f"Limits: {limits.tolist()}")

        # Step 1: Initialize allocation based on proportional demand
        total_demand = demands.sum()
        logging.debug(f"Total demand: {total_demand}")

        allocation = [
            min((demand / total_demand) * group_capacity, limit)
            for demand, limit in zip(demands, limits)
        ]

        logging.debug(f"Initial allocation based on proportional demand: {allocation}")

        # Step 2: Adjust allocation iteratively to account for surplus
        allocated_capacity = sum(allocation)
        logging.debug(f"Initial allocated capacity: {allocated_capacity}")

        while allocated_capacity < group_capacity:
            surplus = group_capacity - allocated_capacity
            logging.info(f"Surplus capacity to be allocated: {surplus}")

            remaining_products = [
                i for i in range(len(allocation)) if allocation[i] < limits.iloc[i]
            ]

            if not remaining_products:
                logging.info("All products have reached their limits. Ending allocation process.")
                break  # All products have reached their limits

            logging.debug(f"Products that can still receive allocation: {remaining_products}")

            # Distribute surplus proportionally among products under their limits
            remaining_demand = sum(demands.iloc[i] for i in remaining_products)
            logging.debug(f"Remaining demand for allocation: {remaining_demand}")

            for i in remaining_products:
                additional_capacity = (demands.iloc[i] / remaining_demand) * surplus
                new_allocation = min(allocation[i] + additional_capacity, limits.iloc[i])
                logging.debug(
                    f"Product {i}: Adding {additional_capacity:.2f} to allocation, new allocation: {new_allocation:.2f}")
                allocation[i] = new_allocation

            allocated_capacity = sum(allocation)
            logging.debug(f"Updated allocated capacity after adjustment: {allocated_capacity}")

        # Add the allocation as a new column to the DataFrame
        data['ALLOCATION'] = allocation
        logging.info("Allocation process completed successfully.")
        logging.debug(f"Final allocation: {allocation}")

        # Step 3: Calculate the allocation share relative to the total CAPACITY
        total_capacity = data['CAPACITY'].sum()
        if total_capacity == 0:
            logging.warning("Total capacity is zero, so allocation share cannot be calculated.")
            data['NEW ALLOC. SHARE'] = None
        else:
            data['NEW ALLOC. SHARE'] = (data['ALLOCATION'] / total_capacity)
            logging.debug(f"Allocation share added to the DataFrame: {data['NEW ALLOC. SHARE'].tolist()}")

        # Create 'New OVERLIMIT' column based on condition
        data['NEW OVERLIMIT'] = data['ALLOCATION'] < data['INDIVIDUAL LIMIT']

        return data


class CapacityAllocator:
    """
    Main class for orchestrating the capacity allocation workflow.
    """

    def __init__(self, filepath, columns_to_extract, allocation_strategy):
        self.file_reader = FileReader(filepath, columns_to_extract)
        self.allocation_strategy = allocation_strategy

    def run(self):
        """
        Reads data and applies the allocation strategy.

        Returns:
            pd.DataFrame: DataFrame with allocation results.
        """
        # Step 1: Read the data
        data = self.file_reader.read_excel_data()
        if data.empty:
            print("No data to process.")
            return pd.DataFrame()

        return self.allocation_strategy.allocate(data)


if __name__ == "__main__":
    # Configuration

    # Hardcoded path to the Excel file
    filepath = os.path.abspath("./Input_data_task_1/Dynamic Programming Homework.xlsx")
    print(filepath)
    columns_to_extract = ['PRODUCT', 'SHARE', 'GROUP CAPACITY', 'CAPACITY', 'INDIVIDUAL LIMIT', 'OVERLIMIT']

    allocator = CapacityAllocator(filepath, columns_to_extract, ProportionalAllocation())

    result = allocator.run()

    pd.set_option('display.max_columns', 10)
    pd.set_option('display.width', 160)
    print(format_output_columns(result))

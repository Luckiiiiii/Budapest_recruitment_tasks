# Budapest_recruitment_tasks

To run on GitHub Codespace:
Task 1: 
python dynamic_programming_task_1.py
Task 2:
python material_balance_task_2.py
or: 
python material_balance_task_2.py --filepath Input_data_task_2/custom_data_material_balance_Task.xlsx

Unit tests:
Task 1:
python test_material_balance_task_2.py 
Task 2:
python test_dynamic_programming_task_1.py 




Budapest recruitment tasks
Hi Lukasz,

I hope you are well. I am happy to inform you that we would like to continue the interviewing process with you with the
second part which is the homework/test. Please find attached and below described tasks.

1. task

    Create a code preferably in python or sql (or the language of your choice) that allocates capacities dynamically to
    products A B C D E, while making sure they don't exceed their individual limit (if they exist):
    
    1. The initial allocation is based on the demand share * group capacity
    2. There could be situations where the initial allocation exceeds the individual limit, this will need to be cut back to
       the limit amount
    3. The difference that remains after the cut back, has to be allocated among the other products (that don't exceed their
       limits)  base on their demand share
    4. The code is succesful if the re-allocation of the full group capacity is done (without any remainder), there are no
       over-limit situations and the demand share is honored


2. task

    Description:
    
    The attached Excel file represents data for a single component, allowing us to track how the Material Balance changes
    over time. The component, identified as FG-AA123456, is a part of an end product.
    
    Definitions:
    
    Production Backlog: The quantity of the component that the manufacturer has yet to produce. The data corresponds to the
    current week's Monday.
    
    Stock at Hand: The current inventory available in the factory, recorded as of the current week's Monday.
    
    Demand: The quantity required for production.
    
    Confirmed Deliveries: The quantity the supplier is expected to deliver to the manufacturer.
    
    Material Balance: This value indicates the future availability of the component in inventory.
    
    A negative Material Balance signifies insufficient inventory for production.
    
    A positive Material Balance indicates sufficient inventory for production.
    
    Example to Illustrate:
    
    Suppose a manufacturer produces tables as the end product. One of the components required for the table is chair legs,
    identified as FG-AA123456.
    
    Task:
    
    Using the data provided, calculate the Material Balance using any programming language of your choice (e.g., SQL, Power
    Query, Python).

Let me know if you have any question.

Thank you very much

Best Regards,

Patrik
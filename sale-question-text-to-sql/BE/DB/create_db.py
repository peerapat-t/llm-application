import pandas as pd
import sqlalchemy
from datetime import datetime

engine = sqlalchemy.create_engine(f"sqlite:///store_main.db")

products_data = {
    'ProductID': [1, 2, 3, 4, 5],
    'ProductName': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Webcam'],
    'Category': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Peripherals'],
    'Price': [1200, 25, 75, 300, 50],
    'StockQuantity': [50, 200, 150, 80, 300]
}
products_df = pd.DataFrame(products_data)
products_df.to_sql("products", engine, index=False, if_exists='replace')

orders_data = {
    'OrderID': [101, 102, 103, 104],
    'ProductID': [1, 2, 2, 4],
    'QuantityOrdered': [1, 2, 1, 1],
    'OrderDate': [datetime(2023, 1, 15), datetime(2023, 1, 17), datetime(2023, 2, 5), datetime(2023, 2, 20)]
}
orders_df = pd.DataFrame(orders_data)
orders_df.to_sql("orders", engine, index=False, if_exists='replace')
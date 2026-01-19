import os
import time
import ast
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from enum import Enum
from datetime import datetime, timedelta
import json

from flask import request
from matplotlib import category
import pandas as pd
import numpy as np

from sqlalchemy.sql import text
from sqlalchemy import create_engine, Engine

from dotenv import load_dotenv
from smolagents import OpenAIServerModel, ToolCallingAgent, tool, Tool
from pydantic import BaseModel, Field

# Create an SQLite database
db_engine = create_engine("sqlite:///munder_difflin.db")

# List containing the different kinds of papers 
paper_supplies = [
    # Paper Types (priced per sheet unless specified)
    {"item_name": "A4 paper",                         "category": "paper",        "unit_price": 0.05},
    {"item_name": "Letter-sized paper",              "category": "paper",        "unit_price": 0.06},
    {"item_name": "Cardstock",                        "category": "paper",        "unit_price": 0.15},
    {"item_name": "Colored paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Glossy paper",                     "category": "paper",        "unit_price": 0.20},
    {"item_name": "Matte paper",                      "category": "paper",        "unit_price": 0.18},
    {"item_name": "Recycled paper",                   "category": "paper",        "unit_price": 0.08},
    {"item_name": "Eco-friendly paper",               "category": "paper",        "unit_price": 0.12},
    {"item_name": "Poster paper",                     "category": "paper",        "unit_price": 0.25},
    {"item_name": "Banner paper",                     "category": "paper",        "unit_price": 0.30},
    {"item_name": "Kraft paper",                      "category": "paper",        "unit_price": 0.10},
    {"item_name": "Construction paper",               "category": "paper",        "unit_price": 0.07},
    {"item_name": "Wrapping paper",                   "category": "paper",        "unit_price": 0.15},
    {"item_name": "Glitter paper",                    "category": "paper",        "unit_price": 0.22},
    {"item_name": "Decorative paper",                 "category": "paper",        "unit_price": 0.18},
    {"item_name": "Letterhead paper",                 "category": "paper",        "unit_price": 0.12},
    {"item_name": "Legal-size paper",                 "category": "paper",        "unit_price": 0.08},
    {"item_name": "Crepe paper",                      "category": "paper",        "unit_price": 0.05},
    {"item_name": "Photo paper",                      "category": "paper",        "unit_price": 0.25},
    {"item_name": "Uncoated paper",                   "category": "paper",        "unit_price": 0.06},
    {"item_name": "Butcher paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Heavyweight paper",                "category": "paper",        "unit_price": 0.20},
    {"item_name": "Standard copy paper",              "category": "paper",        "unit_price": 0.04},
    {"item_name": "Bright-colored paper",             "category": "paper",        "unit_price": 0.12},
    {"item_name": "Patterned paper",                  "category": "paper",        "unit_price": 0.15},

    # Product Types (priced per unit)
    {"item_name": "Paper plates",                     "category": "product",      "unit_price": 0.10},  # per plate
    {"item_name": "Paper cups",                       "category": "product",      "unit_price": 0.08},  # per cup
    {"item_name": "Paper napkins",                    "category": "product",      "unit_price": 0.02},  # per napkin
    {"item_name": "Disposable cups",                  "category": "product",      "unit_price": 0.10},  # per cup
    {"item_name": "Table covers",                     "category": "product",      "unit_price": 1.50},  # per cover
    {"item_name": "Envelopes",                        "category": "product",      "unit_price": 0.05},  # per envelope
    {"item_name": "Sticky notes",                     "category": "product",      "unit_price": 0.03},  # per sheet
    {"item_name": "Notepads",                         "category": "product",      "unit_price": 2.00},  # per pad
    {"item_name": "Invitation cards",                 "category": "product",      "unit_price": 0.50},  # per card
    {"item_name": "Flyers",                           "category": "product",      "unit_price": 0.15},  # per flyer
    {"item_name": "Party streamers",                  "category": "product",      "unit_price": 0.05},  # per roll
    {"item_name": "Decorative adhesive tape (washi tape)", "category": "product", "unit_price": 0.20},  # per roll
    {"item_name": "Paper party bags",                 "category": "product",      "unit_price": 0.25},  # per bag
    {"item_name": "Name tags with lanyards",          "category": "product",      "unit_price": 0.75},  # per tag
    {"item_name": "Presentation folders",             "category": "product",      "unit_price": 0.50},  # per folder

    # Large-format items (priced per unit)
    {"item_name": "Large poster paper (24x36 inches)", "category": "large_format", "unit_price": 1.00},
    {"item_name": "Rolls of banner paper (36-inch width)", "category": "large_format", "unit_price": 2.50},

    # Specialty papers
    {"item_name": "100 lb cover stock",               "category": "specialty",    "unit_price": 0.50},
    {"item_name": "80 lb text paper",                 "category": "specialty",    "unit_price": 0.40},
    {"item_name": "250 gsm cardstock",                "category": "specialty",    "unit_price": 0.30},
    {"item_name": "220 gsm poster paper",             "category": "specialty",    "unit_price": 0.35},
]

# Given below are some utility functions you can use to implement your multi-agent system

def generate_sample_inventory(paper_supplies: list, coverage: float = 0.4, seed: int = 137) -> pd.DataFrame:
    """
    Generate inventory for exactly a specified percentage of items from the full paper supply list.

    This function randomly selects exactly `coverage` × N items from the `paper_supplies` list,
    and assigns each selected item:
    - a random stock quantity between 200 and 800,
    - a minimum stock level between 50 and 150.

    The random seed ensures reproducibility of selection and stock levels.

    Args:
        paper_supplies (list): A list of dictionaries, each representing a paper item with
                               keys 'item_name', 'category', and 'unit_price'.
        coverage (float, optional): Fraction of items to include in the inventory (default is 0.4, or 40%).
        seed (int, optional): Random seed for reproducibility (default is 137).

    Returns:
        pd.DataFrame: A DataFrame with the selected items and assigned inventory values, including:
                      - item_name
                      - category
                      - unit_price
                      - current_stock
                      - min_stock_level
    """
    # Ensure reproducible random output
    np.random.seed(seed)

    # Calculate number of items to include based on coverage
    num_items = int(len(paper_supplies) * coverage)

    # Randomly select item indices without replacement
    selected_indices = np.random.choice(
        range(len(paper_supplies)),
        size=num_items,
        replace=False
    )

    # Extract selected items from paper_supplies list
    selected_items = [paper_supplies[i] for i in selected_indices]

    # Construct inventory records
    inventory = []
    for item in selected_items:
        inventory.append({
            "item_name": item["item_name"],
            "category": item["category"],
            "unit_price": item["unit_price"],
            "current_stock": np.random.randint(200, 800),  # Realistic stock range
            "min_stock_level": np.random.randint(50, 150)  # Reasonable threshold for reordering
        })

    # Return inventory as a pandas DataFrame
    return pd.DataFrame(inventory)

def init_database(db_engine: Engine, seed: int = 137) -> Engine:    
    """
    Set up the Munder Difflin database with all required tables and initial records.

    This function performs the following tasks:
    - Creates the 'transactions' table for logging stock orders and sales
    - Loads customer inquiries from 'quote_requests.csv' into a 'quote_requests' table
    - Loads previous quotes from 'quotes.csv' into a 'quotes' table, extracting useful metadata
    - Generates a random subset of paper inventory using `generate_sample_inventory`
    - Inserts initial financial records including available cash and starting stock levels

    Args:
        db_engine (Engine): A SQLAlchemy engine connected to the SQLite database.
        seed (int, optional): A random seed used to control reproducibility of inventory stock levels.
                              Default is 137.

    Returns:
        Engine: The same SQLAlchemy engine, after initializing all necessary tables and records.

    Raises:
        Exception: If an error occurs during setup, the exception is printed and raised.
    """
    try:
        # ----------------------------
        # 1. Create an empty 'transactions' table schema
        # ----------------------------
        transactions_schema = pd.DataFrame({
            "id": [],
            "item_name": [],
            "transaction_type": [],  # 'stock_orders' or 'sales'
            "units": [],             # Quantity involved
            "price": [],             # Total price for the transaction
            "transaction_date": [],  # ISO-formatted date
        })
        transactions_schema.to_sql("transactions", db_engine, if_exists="replace", index=False)

        # Set a consistent starting date
        initial_date = datetime(2025, 1, 1).isoformat()

        # ----------------------------
        # 2. Load and initialize 'quote_requests' table
        # ----------------------------
        quote_requests_df = pd.read_csv("quote_requests.csv")
        quote_requests_df["id"] = range(1, len(quote_requests_df) + 1)
        quote_requests_df.to_sql("quote_requests", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 3. Load and transform 'quotes' table
        # ----------------------------
        quotes_df = pd.read_csv("quotes.csv")
        quotes_df["request_id"] = range(1, len(quotes_df) + 1)
        quotes_df["order_date"] = initial_date

        # Unpack metadata fields (job_type, order_size, event_type) if present
        if "request_metadata" in quotes_df.columns:
            quotes_df["request_metadata"] = quotes_df["request_metadata"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
            quotes_df["job_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("job_type", ""))
            quotes_df["order_size"] = quotes_df["request_metadata"].apply(lambda x: x.get("order_size", ""))
            quotes_df["event_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("event_type", ""))

        # Retain only relevant columns
        quotes_df = quotes_df[[
            "request_id",
            "total_amount",
            "quote_explanation",
            "order_date",
            "job_type",
            "order_size",
            "event_type"
        ]]
        quotes_df.to_sql("quotes", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 4. Generate inventory and seed stock
        # ----------------------------
        inventory_df = generate_sample_inventory(paper_supplies, seed=seed)
        # inventory_df = generate_sample_inventory(paper_supplies, coverage=1.0, seed=seed)

        # Seed initial transactions
        initial_transactions = []

        # Add a starting cash balance via a dummy sales transaction
        initial_transactions.append({
            "item_name": None,
            "transaction_type": "sales",
            "units": None,
            "price": 50000.0,
            "transaction_date": initial_date,
        })

        # Add one stock order transaction per inventory item
        for _, item in inventory_df.iterrows():
            initial_transactions.append({
                "item_name": item["item_name"],
                "transaction_type": "stock_orders",
                "units": item["current_stock"],
                "price": item["current_stock"] * item["unit_price"],
                "transaction_date": initial_date,
            })

        # Commit transactions to database
        pd.DataFrame(initial_transactions).to_sql("transactions", db_engine, if_exists="append", index=False)

        # Save the inventory reference table
        inventory_df.to_sql("inventory", db_engine, if_exists="replace", index=False)

        return db_engine

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def create_transaction(
    item_name: str,
    transaction_type: str,
    quantity: int,
    price: float,
    date: Union[str, datetime],
) -> int:
    """
    This function records a transaction of type 'stock_orders' or 'sales' with a specified
    item name, quantity, total price, and transaction date into the 'transactions' table of the database.

    Args:
        item_name (str): The name of the item involved in the transaction.
        transaction_type (str): Either 'stock_orders' or 'sales'.
        quantity (int): Number of units involved in the transaction.
        price (float): Total price of the transaction.
        date (str or datetime): Date of the transaction in ISO 8601 format.

    Returns:
        int: The ID of the newly inserted transaction.

    Raises:
        ValueError: If `transaction_type` is not 'stock_orders' or 'sales'.
        Exception: For other database or execution errors.
    """
    try:
        # Convert datetime to ISO string if necessary
        date_str = date.isoformat() if isinstance(date, datetime) else date

        # Validate transaction type
        if transaction_type not in {"stock_orders", "sales"}:
            raise ValueError("Transaction type must be 'stock_orders' or 'sales'")

        # Prepare transaction record as a single-row DataFrame
        transaction = pd.DataFrame([{
            "item_name": item_name,
            "transaction_type": transaction_type,
            "units": quantity,
            "price": price,
            "transaction_date": date_str,
        }])

        # Insert the record into the database
        transaction.to_sql("transactions", db_engine, if_exists="append", index=False)

        # Fetch and return the ID of the inserted row
        result = pd.read_sql("SELECT last_insert_rowid() as id", db_engine)
        return int(result.iloc[0]["id"])

    except Exception as e:
        print(f"Error creating transaction: {e}")
        raise

def get_all_inventory(as_of_date: str) -> Dict[str, int]:
    """
    Retrieve a snapshot of available inventory as of a specific date.

    This function calculates the net quantity of each item by summing 
    all stock orders and subtracting all sales up to and including the given date.

    Only items with positive stock are included in the result.

    Args:
        as_of_date (str): ISO-formatted date string (YYYY-MM-DD) representing the inventory cutoff.

    Returns:
        Dict[str, int]: A dictionary mapping item names to their current stock levels.
    """
    # SQL query to compute stock levels per item as of the given date
    query = """
        SELECT
            item_name,
            SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END) as stock
        FROM transactions
        WHERE item_name IS NOT NULL
        AND transaction_date <= :as_of_date
        GROUP BY item_name
        HAVING stock > 0
    """

    # Execute the query with the date parameter
    result = pd.read_sql(query, db_engine, params={"as_of_date": as_of_date})

    # Convert the result into a dictionary {item_name: stock}
    return dict(zip(result["item_name"], result["stock"]))

def get_stock_level(item_name: str, as_of_date: Union[str, datetime]) -> pd.DataFrame:
    """
    Retrieve the stock level of a specific item as of a given date.

    This function calculates the net stock by summing all 'stock_orders' and 
    subtracting all 'sales' transactions for the specified item up to the given date.

    Args:
        item_name (str): The name of the item to look up.
        as_of_date (str or datetime): The cutoff date (inclusive) for calculating stock.

    Returns:
        pd.DataFrame: A single-row DataFrame with columns 'item_name' and 'current_stock'.
    """
    # Convert date to ISO string format if it's a datetime object
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # SQL query to compute net stock level for the item
    stock_query = """
        SELECT
            item_name,
            COALESCE(SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END), 0) AS current_stock
        FROM transactions
        WHERE item_name = :item_name
        AND transaction_date <= :as_of_date
    """

    # Execute query and return result as a DataFrame
    return pd.read_sql(
        stock_query,
        db_engine,
        params={"item_name": item_name, "as_of_date": as_of_date},
    )

def get_supplier_delivery_date(input_date_str: str, quantity: int) -> str:
    """
    Estimate the supplier delivery date based on the requested order quantity and a starting date.

    Delivery lead time increases with order size:
        - ≤10 units: same day
        - 11–100 units: 1 day
        - 101–1000 units: 4 days
        - >1000 units: 7 days

    Args:
        input_date_str (str): The starting date in ISO format (YYYY-MM-DD).
        quantity (int): The number of units in the order.

    Returns:
        str: Estimated delivery date in ISO format (YYYY-MM-DD).
    """
    # Debug log (comment out in production if needed)
    print(f"FUNC (get_supplier_delivery_date): Calculating for qty {quantity} from date string '{input_date_str}'")

    # Attempt to parse the input date
    try:
        input_date_dt = datetime.fromisoformat(input_date_str.split("T")[0])
    except (ValueError, TypeError):
        # Fallback to current date on format error
        print(f"WARN (get_supplier_delivery_date): Invalid date format '{input_date_str}', using today as base.")
        input_date_dt = datetime.now()

    # Determine delivery delay based on quantity
    if quantity <= 10:
        days = 0
    elif quantity <= 100:
        days = 1
    elif quantity <= 1000:
        days = 4
    else:
        days = 7

    # Add delivery days to the starting date
    delivery_date_dt = input_date_dt + timedelta(days=days)

    # Return formatted delivery date
    return delivery_date_dt.strftime("%Y-%m-%d")

def get_cash_balance(as_of_date: Union[str, datetime]) -> float:
    """
    Calculate the current cash balance as of a specified date.

    The balance is computed by subtracting total stock purchase costs ('stock_orders')
    from total revenue ('sales') recorded in the transactions table up to the given date.

    Args:
        as_of_date (str or datetime): The cutoff date (inclusive) in ISO format or as a datetime object.

    Returns:
        float: Net cash balance as of the given date. Returns 0.0 if no transactions exist or an error occurs.
    """
    try:
        # Convert date to ISO format if it's a datetime object
        if isinstance(as_of_date, datetime):
            as_of_date = as_of_date.isoformat()

        # Query all transactions on or before the specified date
        transactions = pd.read_sql(
            "SELECT * FROM transactions WHERE transaction_date <= :as_of_date",
            db_engine,
            params={"as_of_date": as_of_date},
        )

        # Compute the difference between sales and stock purchases
        if not transactions.empty:
            total_sales = transactions.loc[transactions["transaction_type"] == "sales", "price"].sum()
            total_purchases = transactions.loc[transactions["transaction_type"] == "stock_orders", "price"].sum()
            return float(total_sales - total_purchases)

        return 0.0

    except Exception as e:
        print(f"Error getting cash balance: {e}")
        return 0.0


def generate_financial_report(as_of_date: Union[str, datetime]) -> Dict:
    """
    Generate a complete financial report for the company as of a specific date.

    This includes:
    - Cash balance
    - Inventory valuation
    - Combined asset total
    - Itemized inventory breakdown
    - Top 5 best-selling products

    Args:
        as_of_date (str or datetime): The date (inclusive) for which to generate the report.

    Returns:
        Dict: A dictionary containing the financial report fields:
            - 'as_of_date': The date of the report
            - 'cash_balance': Total cash available
            - 'inventory_value': Total value of inventory
            - 'total_assets': Combined cash and inventory value
            - 'inventory_summary': List of items with stock and valuation details
            - 'top_selling_products': List of top 5 products by revenue
    """
    # Normalize date input
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # Get current cash balance
    cash = get_cash_balance(as_of_date)

    # Get current inventory snapshot
    inventory_df = pd.read_sql("SELECT * FROM inventory", db_engine)
    inventory_value = 0.0
    inventory_summary = []

    # Compute total inventory value and summary by item
    for _, item in inventory_df.iterrows():
        stock_info = get_stock_level(item["item_name"], as_of_date)
        stock = stock_info["current_stock"].iloc[0]
        item_value = stock * item["unit_price"]
        inventory_value += item_value

        inventory_summary.append({
            "item_name": item["item_name"],
            "stock": stock,
            "unit_price": item["unit_price"],
            "value": item_value,
        })

    # Identify top-selling products by revenue
    top_sales_query = """
        SELECT item_name, SUM(units) as total_units, SUM(price) as total_revenue
        FROM transactions
        WHERE transaction_type = 'sales' AND transaction_date <= :date
        GROUP BY item_name
        ORDER BY total_revenue DESC
        LIMIT 5
    """
    top_sales = pd.read_sql(top_sales_query, db_engine, params={"date": as_of_date})
    top_selling_products = top_sales.to_dict(orient="records")

    return {
        "as_of_date": as_of_date,
        "cash_balance": cash,
        "inventory_value": inventory_value,
        "total_assets": cash + inventory_value,
        "inventory_summary": inventory_summary,
        "top_selling_products": top_selling_products,
    }


def search_quote_history(search_terms: List[str], limit: int = 5) -> List[Dict]:
    """
    Retrieve a list of historical quotes that match any of the provided search terms.

    The function searches both the original customer request (from `quote_requests`) and
    the explanation for the quote (from `quotes`) for each keyword. Results are sorted by
    most recent order date and limited by the `limit` parameter.

    Args:
        search_terms (List[str]): List of terms to match against customer requests and explanations.
        limit (int, optional): Maximum number of quote records to return. Default is 5.

    Returns:
        List[Dict]: A list of matching quotes, each represented as a dictionary with fields:
            - original_request
            - total_amount
            - quote_explanation
            - job_type
            - order_size
            - event_type
            - order_date
    """
    conditions = []
    params = {}

    # Build SQL WHERE clause using LIKE filters for each search term
    for i, term in enumerate(search_terms):
        param_name = f"term_{i}"
        conditions.append(
            f"(LOWER(qr.response) LIKE :{param_name} OR "
            f"LOWER(q.quote_explanation) LIKE :{param_name})"
        )
        params[param_name] = f"%{term.lower()}%"

    # Combine conditions with OR so ANY term matching returns results
    where_clause = " OR ".join(conditions) if conditions else "1=1"

    # Final SQL query to join quotes with quote_requests
    query = f"""
        SELECT
            qr.response AS original_request,
            q.total_amount,
            q.quote_explanation,
            q.job_type,
            q.order_size,
            q.event_type,
            q.order_date
        FROM quotes q
        JOIN quote_requests qr ON q.request_id = qr.id
        WHERE {where_clause}
        ORDER BY q.order_date DESC
        LIMIT {limit}
    """

    # Execute parameterized query
    with db_engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row._mapping) for row in result]

########################
########################
########################
# YOUR MULTI AGENT STARTS HERE
########################
########################
########################


# Set up and load your env parameters and instantiate your model.

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# server_model = OpenAIServerModel(
#     model_id="gpt-4o-mini",
#     api_key=openai_api_key,
# )

worker_model = OpenAIServerModel(
    model_id="gpt-4.1",
    api_key=openai_api_key,
)

orchestrator_model = OpenAIServerModel(
    model_id="gpt-4.1",
    api_key=openai_api_key,
)

"""Set up tools for your agents to use, these should be methods that combine the database functions above
 and apply criteria to them to ensure that the flow of the system is correct."""


# Tools for inventory agent

def get_complete_inventory() -> List[str]:
    """
    Tool to retrieve the complete list of item names in the inventory.

    Returns:
        List[str]: A list of all item names currently in the inventory.
    """
    inventory_df = pd.read_sql("SELECT item_name FROM inventory", db_engine)
    return inventory_df["item_name"].tolist()


def is_item_in_inventory(item_name: str) -> bool:
    """
    Tool to check if a specific item is present in the inventory.

    Args:
        item_name (str): The name of the item to check.
    Returns:
        bool: True if the item is in inventory, False otherwise.
    """
    inventory_df = pd.read_sql(
        "SELECT COUNT(*) as count FROM inventory WHERE item_name = :item_name",
        db_engine,
        params={"item_name": item_name},
    )
    return inventory_df["count"].iloc[0] > 0


def check_restock_needed(item_name: str, requested_amount: int, as_of_date: str) -> int:
    """
    Tool to check if a specific item needs restocking as of a given date.
    
    Args:
        item_name (str): The name of the item to check.
        requested_amount (int): The amount requested by a customer.
        as_of_date (str): The date to check stock levels against (ISO format).
    Returns:
        int: The amount that needs to be restocked. Returns 0 if no restocking is needed.
    """
    stock_info = get_stock_level(item_name, as_of_date)
    current_stock = stock_info["current_stock"].iloc[0]

    # Fetch minimum stock level from inventory table
    inventory_df = pd.read_sql(
        "SELECT min_stock_level FROM inventory WHERE item_name = :item_name",
        db_engine,
        params={"item_name": item_name},
    )
    if inventory_df.empty:
        return 0  # Item not found, no restock needed

    min_stock_level = inventory_df["min_stock_level"].iloc[0]

    restock_amount = (min_stock_level + requested_amount) - current_stock
    return restock_amount if restock_amount > 0 else 0


class OrderItem(BaseModel):
    item_name: str = Field(..., description="Name of the item to order")
    requested_amount: int = Field(..., description="Amount of the item requested")


class OrderRequest(BaseModel):
    items: List[OrderItem] = Field(..., description="List of items requested in the order")
    event: Optional[str] = Field(None, description="Type of event for which the order is placed")
    order_date: str = Field(..., description="Date the order is placed (ISO format)")
    latest_delivery_date: Optional[str] = Field(None, description="Latest acceptable delivery date (ISO format)")


class OrderParser(Tool):
    name = "order_parser"
    description = "Parses customer order requests into structured data."
    inputs = {
        "order_request": {
            "type": "string",
            "description": "The raw customer order request text.",
        }
    }
    output_type = "object"
    output_schema = OrderRequest.model_json_schema()


    def __init__(self, model: OpenAIServerModel):
        super().__init__()
        self.model = model

    def forward(self, order_request: str) -> OrderRequest:
        inventory_items = get_complete_inventory()
        response = self.model.generate([
            {
                "role": "system",
                "content": (
                    "You are an expert at parsing customer order requests into structured data.\n"
                    "You have access to the current inventory items to help map requested items accurately.\n"
                    f"Items in inventory: {inventory_items}\n\n"
                    "Items which are not found in the inventory should still be included in the output.\n"
                    "When parsing the order request, ensure that each item includes the requested amount.\n"
                    "Determine the order date from the request, and if a latest acceptable delivery date is mentioned, include that as well.\n\n"
                    "If mentioned, determine the type of event for which the order is placed (e.g., wedding, corporate event, birthday party, etc.) and include it in the output.\n\n"
                    "Ensure that the output strictly adheres to the provided JSON schema: \n"
                    f"{json.dumps(OrderRequest.model_json_schema(), indent=2)}"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Parse the following customer order request into a structured format:\n\n{order_request}"
                )
            }
        ])
        parsed_data = response.content.strip()
        #Strip content before first { and after last }
        first_brace = parsed_data.find("{")
        last_brace = parsed_data.rfind("}")
        parsed_data = parsed_data[first_brace:last_brace+1]
        # Debug log (comment out in production if needed)
        # print(f"DEBUG (OrderParser): Parsed data: {parsed_data}")
        return OrderRequest.model_validate_json(parsed_data)


class ItemStockStatus(BaseModel):
    item_name: str = Field(..., description="Name of the item")
    in_inventory: bool = Field(..., description="Whether the item is in inventory")
    current_stock: Optional[int] = Field(None, description="Current stock level of the item, if in inventory")
    restock_needed: Optional[int] = Field(None, description="Amount that needs to be restocked, if any")
    supplier_delivery_date: Optional[str] = Field(None, description="Expected delivery date from supplier, if restocking is needed")


class InventoryAnalysisResult(BaseModel):
    order_request: OrderRequest = Field(..., description="The original order request")
    item_stocks: List[ItemStockStatus] = Field(..., description="List of stock status for each item in the order")
    can_fulfill_order: bool = Field(..., description="Whether the order can be fulfilled based on current inventory")
    earliest_delivery_date: Optional[str] = Field(None, description="Earliest delivery date for the order")


def get_item_stock_status(item_name: str, requested_amount: int, as_of_date: str) -> ItemStockStatus:
    """
    Tool to get the stock status of a specific item as of a given date.

    Args:
        item_name (str): The name of the item to check.
        requested_amount (int): The amount requested by a customer.
        as_of_date (str): The date to check stock levels against (ISO format).
    Returns:
        ItemStockStatus: The stock status of the item.
    """
    in_inventory = is_item_in_inventory(item_name)
    current_stock = None
    restock_needed = None
    supplier_delivery_date = None

    if in_inventory:
        stock_info = get_stock_level(item_name, as_of_date)
        current_stock = stock_info["current_stock"].iloc[0]
        restock_needed = check_restock_needed(
            item_name,
            requested_amount,
            as_of_date,
        )
        if restock_needed > 0:
            supplier_delivery_date = get_supplier_delivery_date(
                as_of_date,
                restock_needed,
            )

    return ItemStockStatus(
        item_name=item_name,
        in_inventory=in_inventory,
        current_stock=current_stock,
        restock_needed=restock_needed,
        supplier_delivery_date=supplier_delivery_date,
    )


@tool
def analyze_order_inventory(order: dict) -> dict:
    """
    Tool to analyze if the requested order can be fulfilled based on current inventory.

    Args:
        order (dict): The structured order request as a dictionary.
    Returns:
        dict: Analysis of each item's stock status and overall fulfillment capability.
    """
    # Parse order dict into OrderRequest object
    if isinstance(order, str):
        order_obj = OrderRequest.model_validate_json(order)
    elif isinstance(order, dict):
        order_obj = OrderRequest.model_validate(order)
    else:
        order_obj = order
    
    item_stocks = []
    can_fulfill_order = True
    earliest_delivery_date = order_obj.order_date

    for order_item in order_obj.items:
        stock_status = get_item_stock_status(order_item.item_name, order_item.requested_amount, order_obj.order_date)
        item_stocks.append(stock_status)
        if not stock_status.in_inventory:
            can_fulfill_order = False
            continue
        if stock_status.restock_needed and stock_status.restock_needed > 0:
            if stock_status.supplier_delivery_date and (stock_status.supplier_delivery_date > earliest_delivery_date):
                earliest_delivery_date = stock_status.supplier_delivery_date

    if order_obj.latest_delivery_date:
        if earliest_delivery_date > order_obj.latest_delivery_date:
            can_fulfill_order = False

    result = InventoryAnalysisResult(
            order_request=order_obj,
            item_stocks=item_stocks,
            can_fulfill_order=can_fulfill_order,
            earliest_delivery_date=earliest_delivery_date,
    )
    return result.model_dump()


# Tools for quoting agent

def fetch_historical_quotes(order_request: OrderRequest) -> List[Dict]:
    """
    Tool to extract keywords from the order request and fetch historical quotes.

    Args:
        order_request (OrderRequest): The structured order request.
    Returns:
        List[Dict]: A list of matching historical quotes.
    """
    keywords = set()
    for item in order_request.items:
        keywords.update(item.item_name.lower().split())
    if order_request.event:
        keywords.update(order_request.event.lower().split())
    search_terms = list(keywords)
    return search_quote_history(search_terms, limit=5)


class DiscountAnalysisResult(BaseModel):
    need_size: str = Field(..., description="Size of the order needed")
    discount_percentage: float = Field(..., description="Discount percentage to apply")
    discount_reason: str = Field(..., description="Reason for the discount")


class DiscountAnalyzer(Tool):
    name = "discount_analyzer"
    description = "Analyzes customer order for applicable discounts based on historical quotes."
    inputs = {
        "inventory_analysis": {
            "type": "object",
            "description": "The inventory analysis as a InventoryAnalysisResult object.",
        }
    }
    output_type = "object"

    def __init__(self, model: OpenAIServerModel):
        super().__init__()
        self.model = model

    def forward(self, inventory_analysis: InventoryAnalysisResult) -> DiscountAnalysisResult:
        if isinstance(inventory_analysis, str):
            inventory_obj = InventoryAnalysisResult.model_validate_json(inventory_analysis)
        elif isinstance(inventory_analysis, dict):
            inventory_obj = InventoryAnalysisResult.model_validate(inventory_analysis)
        else:
            inventory_obj = inventory_analysis
        order_obj = inventory_obj.order_request
        historical_quotes = fetch_historical_quotes(order_obj)
        response = self.model.generate([
            {
                "role": "system",
                "content": (
                    "You are an expert at analyzing customer order requests and historical quotes to determine discount strategies.\n"
                    "Based on the historical quotes and the current order request, identify the size of the order needed.\n"
                    "Using the need size and event type, determine an appropriate discount percentage and reason for the discount.\n\n"
                    "Ensure that the output strictly adheres to the provided JSON schema: \n"
                    f"{json.dumps(DiscountAnalysisResult.model_json_schema(), indent=2)}"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Analyze the following customer order request and historical quotes to determine discount strategies:\n\n"
                    f"Order Request: {order_obj.model_dump_json(indent=2)}\n\n"
                    f"Historical Quotes: {historical_quotes}"
                )
            }
        ])
        parsed_data = response.content.strip()
        #Strip content before first { and after last }
        first_brace = parsed_data.find("{")
        last_brace = parsed_data.rfind("}")
        parsed_data = parsed_data[first_brace:last_brace+1]
        result = DiscountAnalysisResult.model_validate_json(parsed_data)
        return result


class QuoteItem(BaseModel):
    item_name: str = Field(..., description="Name of the item to quote")
    requested_amount: int = Field(..., description="Amount of the item requested")
    unit_price: float = Field(..., description="Unit price of the item")
    total_price: float = Field(..., description="Total price for the requested amount")


class Quote(BaseModel):
    quote_items: List[QuoteItem] = Field(..., description="List of items in the quote")
    total_amount: float = Field(..., description="Total amount for the entire quote")
    delivery_date: str = Field(..., description="Estimated delivery date for the quote")
    discount_applied: Optional[float] = Field(None, description="Total discount applied to the quote")
    discount_reason: Optional[str] = Field(None, description="Reason for the discount")
    comments: Optional[str] = Field(None, description="Additional comments regarding the quote")


def get_item_price(item_name: str) -> float:
    """
    Tool to get the unit price of a specific item.

    Args:
        item_name (str): The name of the item.
    Returns:
        float: The unit price of the item.
    """
    price_df = pd.read_sql(
        "SELECT unit_price FROM inventory WHERE item_name = :item_name",
        db_engine,
        params={"item_name": item_name},
    )
    if price_df.empty:
        return 0.0  # Item not found
    return float(price_df["unit_price"].iloc[0])


def generate_quote(inventory_analysis: InventoryAnalysisResult, discount_analysis: DiscountAnalysisResult) -> Quote:
    """
    Tool to generate a quote based on inventory analysis and discount recommendations.

    Args:
        inventory_analysis (InventoryAnalysisResult): The result of the inventory analysis.
        discount_analysis (DiscountAnalysisResult): The result of the discount analysis.
    Returns:
        Quote: The generated quote.
    """
    quote_items = []
    total_amount = 0.0

    # Check if order can be fulfilled
    if not inventory_analysis.can_fulfill_order:
        return {
            "quote_items": [],
            "total_amount": 0.0,
            "delivery_date": "N/A",
            "comments": "Order cannot be fulfilled based on current inventory levels.",
        }

    # Get items from the inventory_analysis
    items = inventory_analysis.order_request.items
    
    for order_item in items:
        unit_price = get_item_price(order_item.item_name)
        sales_price = unit_price * 1.3  # Assuming a 30% markup for sales
        unit_price = round(sales_price, 2)
        item_total = unit_price * order_item.requested_amount
        quote_items.append(QuoteItem(
            item_name=order_item.item_name,
            requested_amount=order_item.requested_amount,
            unit_price=unit_price,
            total_price=item_total,
        ))
        total_amount += item_total
    
    discount_percentage = discount_analysis.discount_percentage
    if not discount_percentage or discount_percentage < 0:
        discount_percentage = 0.0
    discount_applied = (discount_percentage / 100.0) * total_amount
    total_amount_after_discount = total_amount - discount_applied
    
    return Quote(
        quote_items=quote_items,
        total_amount=total_amount_after_discount,
        delivery_date=inventory_analysis.earliest_delivery_date,
        discount_applied=discount_applied,
        discount_reason=discount_analysis.discount_reason,
        comments="Quote generated successfully.",
    )

class QuoteGenerator(Tool):
    name = "generate_quote"
    description = "Generates a quote based on inventory analysis and discount recommendations."
    inputs = {
        "inventory_analysis": {
            "type": "object",
            "description": "The inventory analysis result as a InventoryAnalysisResult object.",
        },
        "discount_analysis": {
            "type": "object",
            "description": "The discount analysis result as DiscountAnalysisResult object.",
        },
    }
    output_type = "object"
    output_schema = Quote.model_json_schema()

    def forward(self, inventory_analysis: InventoryAnalysisResult, discount_analysis: DiscountAnalysisResult) -> Quote:
        if isinstance(inventory_analysis, str):
            inventory_analysis = InventoryAnalysisResult.model_validate_json(inventory_analysis)
        elif isinstance(inventory_analysis, dict):
            inventory_analysis = InventoryAnalysisResult.model_validate(inventory_analysis)
        if isinstance(discount_analysis, str):
            discount_analysis = DiscountAnalysisResult.model_validate_json(discount_analysis)
        elif isinstance(discount_analysis, dict):
            discount_analysis = DiscountAnalysisResult.model_validate(discount_analysis)
        result = generate_quote(inventory_analysis, discount_analysis)
        return result



# Tools for ordering agent

def order_stock(item_name: str, quantity: int, original_order_date: str) -> str:
    """
    Tool to place an order for stock replenishment.

    Args:
        item_name (str): The name of the item to order.
        quantity (int): The quantity of the item to order.
        original_order_date (str): The date the original order was placed (ISO format).
    """
    unit_price_df = pd.read_sql(
        "SELECT unit_price FROM inventory WHERE item_name = :item_name",
        db_engine,
        params={"item_name": item_name},
    )
    if unit_price_df.empty:
        return f"Item '{item_name}' not found in inventory."
    unit_price = unit_price_df["unit_price"].iloc[0]
    create_transaction(
        item_name=item_name,
        transaction_type="stock_orders",
        quantity=quantity,
        price=unit_price * quantity,
        date=original_order_date,
    )
    return f"Ordered {quantity} units of {item_name} on {original_order_date}."


def schedule_delivery(item_name: str, quantity: int, total_price: float, earliest_delivery_date: str) -> str:
    """
    Tool to schedule delivery for an ordered item.

    Args:
        item_name (str): The name of the item.
        quantity (int): The quantity ordered.
        total_price (float): The total price for the ordered quantity.
        earliest_delivery_date (str): The earliest possible delivery date (ISO format).
    Returns:
        str: Estimated delivery date.
    """
    create_transaction(
        item_name=item_name,
        transaction_type="sales",
        quantity=quantity,
        price=total_price,
        date=earliest_delivery_date,
    )
    return f"Estimated delivery date for {quantity} units of {item_name} is {earliest_delivery_date}."


class StockOrder(Tool):
    name = "order_stock"
    description = "Places an order for stock replenishment."
    inputs = {
        "inventory_analysis": {
            "type": "object",
            "description": "The inventory analysis as a InventoryAnalysisResult object.",
        }
    }
    output_type = "string"
    
    def forward(self, inventory_analysis: InventoryAnalysisResult) -> str:
        if isinstance(inventory_analysis, str):
            inventory_obj = InventoryAnalysisResult.model_validate_json(inventory_analysis)
        elif isinstance(inventory_analysis, dict):
            inventory_obj = InventoryAnalysisResult.model_validate(inventory_analysis)
        else:
            inventory_obj = inventory_analysis
        
        if not inventory_obj.can_fulfill_order:
            return "Order cannot be fulfilled; no stock orders placed."

        order_date = inventory_obj.order_request.order_date
        result_items = []
        for item_status in inventory_obj.item_stocks:
            if item_status.restock_needed and item_status.restock_needed > 0:
                result = order_stock(
                    item_name=item_status.item_name,
                    quantity=item_status.restock_needed,
                    original_order_date=order_date,
                )
                result_items.append(result)
        return "\n".join(result_items)


class DeliveryScheduler(Tool):
    name = "schedule_delivery"
    description = "Schedules delivery for an ordered item."
    inputs = {
        "quote": {
            "type": "object",
            "description": "The generated quote as a Quote object.",
        }
    }
    output_type = "string"

    def forward(self, quote: Quote) -> str:
        if isinstance(quote, str):
            quote = Quote.model_validate_json(quote)
        elif isinstance(quote, dict):
            quote = Quote.model_validate(quote)
        else:
            quote = quote

        if not quote.quote_items:
            return "No items in quote; no deliveries scheduled."

        result_items = []
        for item in quote.quote_items:
            result = schedule_delivery(
                item_name=item.item_name,
                quantity=item.requested_amount,
                total_price=item.total_price,
                earliest_delivery_date=quote.delivery_date,
            )
            result_items.append(result)
        return "\n".join(result_items)




# Set up your agents and create an orchestration agent that will manage them.

class InventoryAgent(ToolCallingAgent):
    def __init__(self, model: OpenAIServerModel):
        super().__init__(
            tools=[OrderParser(model=model), analyze_order_inventory],
            model=worker_model,
            name="inventory_processor",
            description="Agent responsible for tracking inventory stock levels.",
            instructions=(
                "You are an inventory management agent for Munder Difflin. "
                "Your job is to process customer orders and check inventory levels to determine if orders can be fulfilled.\n",
                "Use the provided tools to parse orders and analyze inventory.\n",
                "Always include the full customer request when using the order_parser tool.\n",
                "Always return tool outputs as final output."
            )
        )

class QuotingAgent(ToolCallingAgent):
    def __init__(self, model: OpenAIServerModel):
        super().__init__(
            tools=[DiscountAnalyzer(model=model), QuoteGenerator()],
            model=worker_model,
            name="quote_processor",
            description="Agent responsible for generating quotes based on customer requests.",
            instructions=(
                "You are a quoting agent for Munder Difflin. "
                "Your job is to analyze customer orders and historical quotes to determine appropriate discounts and pricing strategies.\n",
                "Use the provided tools to analyze discounts and generate quotes.\n",
                "Always return tool outputs as final output."
            )
        )

class OrderingAgent(ToolCallingAgent):
    def __init__(self, model: OpenAIServerModel):
        super().__init__(
            tools=[StockOrder(), DeliveryScheduler()],
            model=worker_model,
            name="order_processor",
            description="Agent responsible for placing stock orders with suppliers and scheduling deliveries.",
            instructions=(
                "You are an ordering agent for Munder Difflin. "
                "Your job is to place stock orders with suppliers and schedule deliveries based on customer orders.\n",
                "Use the provided tools to order stock and schedule deliveries.\n",
                "Always return tool outputs as final output."
            )
        )

class OrchestrationAgent(ToolCallingAgent):
    def __init__(self, model: OpenAIServerModel):
        self.inventory_agent = InventoryAgent(model)
        self.quoting_agent = QuotingAgent(model)
        self.ordering_agent = OrderingAgent(model)

        @tool
        def process_request(original_request: str) -> InventoryAnalysisResult:
            """
            Process the original customer request to extract requested items and order date.

            Args:
                original_request: The raw customer order request text.
            Returns:
                InventoryAnalysisResult object with parsed order details.
            """
            parsed_order = self.inventory_agent.run(
                f"The original customer request is: {original_request}"
                "Use the order_parser tool to parse the request into structured data."
                "Then use the analyze_order_inventory tool to analyze if the requested order can be fulfilled based on current inventory."
                "Return the InventoryAnalysisResult object returned by the analyze_order_inventory tool as final output."
            )

            return parsed_order
        
        @tool
        def analyze_discount(inventory_analysis: InventoryAnalysisResult) -> DiscountAnalysisResult:
            """
            Generate a discount analysis based on the inventory analysis result.

            Args:
                inventory_analysis: The result from the inventory analysis.
            Returns:
                DiscountAnalysisResult object with discount details.
            """
            discount_analysis = self.quoting_agent.run(
                f"The inventory analysis is: {inventory_analysis}\n"
                "Use the discount_analyzer tool to generate a discount analysis using the exact format of the inventory analysis.\n"
                "Return the DiscountAnalysisResult returned by the tool as final output."
            )

            return discount_analysis
        
        @tool
        def generate_quote(inventory_analysis: InventoryAnalysisResult, discount_analysis: DiscountAnalysisResult) -> Quote:
            """
            Generate the quote based on inventory analysis and discount analysis.

            Args:
                inventory_analysis: The result from the inventory analysis.
                discount_analysis: The result from the discount analysis.
            Returns:
                Quote object with the quote details.
            """
            quote = self.quoting_agent.run(
                f"The inventory analysis result is: {inventory_analysis}\n"
                f"The discount analysis result is: {discount_analysis}\n"
                "Use the generate_quote tool with the exact format of these inputs.\n"
                "Return the Quote object returned by the tool as final output."
            )
            return quote
        

        @tool
        def place_stock_orders(inventory_analysis: InventoryAnalysisResult) -> str:
            """
            Place stock orders based on the quote and inventory analysis.

            Args:
                inventory_analysis: The result from the inventory analysis.
            Returns:
                str: Confirmation of stock orders placed.
            """
            order_confirmation = self.ordering_agent.run(
                f"The inventory analysis result is: {inventory_analysis}\n"
                "Use the order_stock tool to place stock orders using the exact format of the inventory analysis.\n"
                "Return the output of the tool as final output."
            )
            return order_confirmation
        
        @tool
        def create_formatted_quote(quote: dict) -> str:
            """
            Create a formatted string representation of the quote.

            Args:
                quote: The generated quote.
            Returns:
                str: Formatted quote details.
            """
            quote_obj = Quote.model_validate(quote)
            if not quote_obj.quote_items:
                return "No items in quote; cannot create formatted quote."
            formatted_quote = f"Quote Details:\n"
            for item in quote_obj.quote_items:
                formatted_quote += (
                    f"- Item: {item.item_name}, "
                    f"Requested Amount: {item.requested_amount}, "
                    f"Unit Price: ${item.unit_price:.2f}, "
                    f"Total Price: ${item.total_price:.2f}\n"
                )
            formatted_quote += f"Total Amount before Discount: ${sum(i.total_price for i in quote_obj.quote_items):.2f}\n"
            formatted_quote += f"Total Amount with Discount: ${quote_obj.total_amount:.2f}\n"
            formatted_quote += f"Estimated Delivery Date: {quote_obj.delivery_date}\n"
            if quote_obj.discount_applied:
                formatted_quote += f"Discount Applied: ${quote_obj.discount_applied:.2f} ({quote_obj.discount_reason})\n"
            if quote_obj.comments:
                formatted_quote += f"Comments: {quote_obj.comments}\n"
            return formatted_quote
        

        @tool
        def schedule_deliveries(quote: Quote) -> str:
            """
            Schedule deliveries based on the generated quote.

            Args:
                quote: The generated quote.
            Returns:
                str: Confirmation of deliveries scheduled.
            """
            delivery_confirmation = self.ordering_agent.run(
                f"The generated quote is: {quote}\n"
                "Use the schedule_delivery tool to schedule deliveries using the exact format of the quote.\n"
                "Return the output of the tool as final output."
            )
            return delivery_confirmation

        super().__init__(
            tools=[
                process_request,
                analyze_discount,
                generate_quote,
                place_stock_orders,
                schedule_deliveries,
                create_formatted_quote
            ],
            model=model,
            name="orchestration_agent",
            description="Orchestrator agent coordinating inventory, quoting, and ordering agents.",
            instructions=(
                "You are the orchestrator for processing orders for a paper supply company.\n"
                "You coordinate between the inventory, quoting, and ordering agents to fulfill customer requests.\n\n"
                "Use the provided tools to process the original customer request and delegate tasks to the appropriate agents.\n"
                "Follow these steps:\n"

                "1. Use the process_request tool to parse and analyze the full original customer request.\n"
                "2.1 If the order can be fulfilled, proceed to step 3.\n"
                "2.2 If the order cannot be fulfilled, stop processing and return a final output message indicating that the order cannot be fulfilled and give a reason.\n"

                "3. Use the analyze_discount tool to generate a discount analysis based on the full inventory analysis.\n"
                "4. Use the generate_quote tool to create the quote based on the full inventory analysis and discount analysis.\n"
                "5. Use the place_stock_orders tool to place stock orders using the exact format of the inventory analysis.\n"
                "6. Use the schedule_deliveries tool to schedule deliveries using the exact format of the generated quote.\n"
                "7. Use the create_formatted_quote tool to generate a formatted string using the exact format of the generated quote.\n"
                "8. Return the exact formatted quote as the final output."
            )
        )



    # Define methods to coordinate between agents as needed

# Run your test scenarios by writing them here. Make sure to keep track of them.

def run_test_scenarios():
    
    print("Initializing Database...")
    init_database(db_engine=db_engine)
    try:
        quote_requests_sample = pd.read_csv("quote_requests_sample.csv")
        quote_requests_sample["request_date"] = pd.to_datetime(
            quote_requests_sample["request_date"], format="%m/%d/%y", errors="coerce"
        )
        quote_requests_sample.dropna(subset=["request_date"], inplace=True)
        quote_requests_sample = quote_requests_sample.sort_values("request_date")
    except Exception as e:
        print(f"FATAL: Error loading test data: {e}")
        return

    # Get initial state
    initial_date = quote_requests_sample["request_date"].min().strftime("%Y-%m-%d")
    report = generate_financial_report(initial_date)
    current_cash = report["cash_balance"]
    current_inventory = report["inventory_value"]

    ############
    ############
    ############
    # INITIALIZE YOUR MULTI AGENT SYSTEM HERE
    ############
    ############
    ############

    orchestration_agent = OrchestrationAgent(orchestrator_model)
    # orchestration_agent = InventoryAgent(worker_model)  # Placeholder until multi-agent system is set up

    results = []
    for idx, row in quote_requests_sample.iterrows():
        request_date = row["request_date"].strftime("%Y-%m-%d")

        print(f"\n=== Request {idx+1} ===")
        print(f"Context: {row['job']} organizing {row['event']}")
        print(f"Request Date: {request_date}")
        print(f"Cash Balance: ${current_cash:.2f}")
        print(f"Inventory Value: ${current_inventory:.2f}")

        # Process request
        request_with_date = f"{row['request']} (Date of request: {request_date})"

        ############
        ############
        ############
        # USE YOUR MULTI AGENT SYSTEM TO HANDLE THE REQUEST
        ############
        ############
        ############

        response = orchestration_agent.run(request_with_date)

        # Update state
        report = generate_financial_report(request_date)
        current_cash = report["cash_balance"]
        current_inventory = report["inventory_value"]

        print(f"Response: {response}")
        print(f"Updated Cash: ${current_cash:.2f}")
        print(f"Updated Inventory: ${current_inventory:.2f}")

        results.append(
            {
                "request_id": idx + 1,
                "request_date": request_date,
                "cash_balance": current_cash,
                "inventory_value": current_inventory,
                "response": response,
            }
        )

        time.sleep(1)

    # Final report
    final_date = quote_requests_sample["request_date"].max().strftime("%Y-%m-%d")
    final_report = generate_financial_report(final_date)
    print("\n===== FINAL FINANCIAL REPORT =====")
    print(f"Final Cash: ${final_report['cash_balance']:.2f}")
    print(f"Final Inventory: ${final_report['inventory_value']:.2f}")

    # Save results
    pd.DataFrame(results).to_csv("test_results.csv", index=False)
    return results


if __name__ == "__main__":
    results = run_test_scenarios()

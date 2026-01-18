import os
import time
import ast
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from enum import Enum
from datetime import datetime, timedelta

from matplotlib import category
import pandas as pd
import numpy as np

from sqlalchemy.sql import text
from sqlalchemy import create_engine, Engine

from dotenv import load_dotenv
from smolagents import OpenAIServerModel, ToolCallingAgent, tool

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

    # Combine conditions; fallback to always-true if no terms provided
    where_clause = " AND ".join(conditions) if conditions else "1=1"

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

server_model = OpenAIServerModel(
    model_id="gpt-4o-mini",
    api_key=openai_api_key,
)

"""Set up tools for your agents to use, these should be methods that combine the database functions above
 and apply criteria to them to ensure that the flow of the system is correct."""


# Tools for inventory agent

@tool
def get_inventory_snapshot(as_of_date: str) -> Dict[str, int]:
    """
    Tool to get a snapshot of the current inventory as of a specific date.

    Args:
        as_of_date (str): The date to check inventory against (ISO format).
    Returns:
        Dict[str, int]: A dictionary mapping item names to their current stock levels.
    """
    return get_all_inventory(as_of_date)

@tool
def check_restock_needed(item_name: str, requested_amount: int, as_of_date: str) -> bool:
    """
    Tool to check if a specific item needs restocking as of a given date.
    
    Args:
        item_name (str): The name of the item to check.
        requested_amount (int): The amount requested by a customer.
        as_of_date (str): The date to check stock levels against (ISO format).
    Returns:
        bool: True if restocking is needed, False otherwise.
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
        return False  # Item not found in inventory

    min_stock_level = inventory_df["min_stock_level"].iloc[0]

    return current_stock < min_stock_level + requested_amount


@tool
def is_product_in_inventory(item_name: str) -> bool:
    """
    Tool to check if a specific product is in the inventory.

    Args:
        item_name (str): The name of the item to check.
    Returns:
        bool: True if the product is in the inventory, False otherwise.
    """
    inventory = get_all_inventory(as_of_date=datetime.now().isoformat())
    return item_name in inventory


# Tools for quoting agent

@tool
def fetch_historical_quotes(search_terms: List[str], limit: int = 5) -> List[Dict]:
    """
    Tool to fetch historical quotes based on search terms.
    Args:
        search_terms (List[str]): List of terms to search for.
        limit (int, optional): Maximum number of quotes to return. Default is 5.
    Returns:
        List[Dict]: A list of matching historical quotes.
    """
    return search_quote_history(search_terms, limit)


@tool
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

# Tools for ordering agent

@tool
def get_delivery_date(item_name: str, quantity: int, order_date: str) -> str:
    """
    Tool to get the estimated delivery date for an ordered item.

    Args:
        item_name (str): The name of the item.
        quantity (int): The quantity ordered.
        order_date (str): The date the order is placed (ISO format).
    Returns:
        str: Estimated delivery date.
    """
    return get_supplier_delivery_date(order_date, quantity)

@tool
def order_stock(item_name: str, quantity: int, order_date: str) -> str:
    """
    Tool to place an order for stock replenishment.

    Args:
        item_name (str): The name of the item to order.
        quantity (int): The quantity of the item to order.
        order_date (str): The date the order is placed (ISO format).
    """
    delivery_date = get_supplier_delivery_date(order_date, quantity)
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
        date=order_date,
    )
    return f"Ordered {quantity} units of {item_name} on {order_date}. Estimated delivery date: {delivery_date}."


@tool
def schedule_delivery(item_name: str, quantity: int, unit_price: float, order_date: str, supplier_delivery_date: Optional[str]) -> str:
    """
    Tool to schedule delivery for an ordered item.

    Args:
        item_name (str): The name of the item.
        quantity (int): The quantity ordered.
        unit_price (float): The unit price of the item.
        order_date (str): The date the order was placed (ISO format).
        supplier_delivery_date (Optional[str]): The supplier's estimated delivery date (ISO format).
    Returns:
        str: Estimated delivery date.
    """
    delivery_date = supplier_delivery_date if supplier_delivery_date else order_date
    create_transaction(
        item_name=item_name,
        transaction_type="sales",
        quantity=quantity,
        price=unit_price * quantity,
        date=delivery_date,
    )
    return f"Estimated delivery date for {quantity} units of {item_name} ordered on {order_date} is {delivery_date}."


# Set up your agents and create an orchestration agent that will manage them.
class InventoryAgent(ToolCallingAgent):
    def __init__(self, model: OpenAIServerModel):
        super().__init__(
            tools=[get_inventory_snapshot, is_product_in_inventory, check_restock_needed],
            model=model,
            name="inventory_processor",
            description="Agent responsible for tracking inventory stock levels.",
            max_tool_threads=1,
        )

class QuotingAgent(ToolCallingAgent):
    def __init__(self, model: OpenAIServerModel):
        super().__init__(
            tools=[fetch_historical_quotes, get_item_price],
            model=model,
            name="quote_processor",
            description="Agent responsible for generating quotes based on customer requests.",
            max_tool_threads=1,
        )

class OrderingAgent(ToolCallingAgent):
    def __init__(self, model: OpenAIServerModel):
        super().__init__(
            tools=[order_stock, schedule_delivery],
            model=model,
            name="order_processor",
            description="Agent responsible for placing stock orders with suppliers and scheduling deliveries.",
            max_tool_threads=1,
        )

@dataclass
class ItemQuantity:
    item_name: str
    quantity: int

class ItemAvailability(Enum):
    IN_STOCK = "in_stock"
    NEEDS_RESTOCK = "needs_restock"
    UNAVAILABLE = "unavailable"

@dataclass
class InventoryResult:
    item_name: str
    availability: ItemAvailability

@dataclass
class PriceInfo:
    item_name: str
    unit_price: float


class OrderSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

@dataclass
class DiscountInfo:
    item_name: str
    sales_price: float
    discount_price: float
    reason: str

@dataclass
class DeliveryInfo:
    item_name: str
    quantity: int
    delivery_date: str


class OrchestrationAgent(ToolCallingAgent):
    def __init__(self, model: OpenAIServerModel):
        self.inventory_agent = InventoryAgent(model)
        self.quoting_agent = QuotingAgent(model)
        self.ordering_agent = OrderingAgent(model)
        
        # Initialize state storage for intermediate results
        self.state = {
            "original_request": None,
            "request_date": None,
            "latest_date": None,
            "requested_items": None,
            "inventory_result": None,
            "price_info": None,
            "order_size": None,
            "discount_info": None,
            "delivery_info": None,
            "final_quote": None
        }

        @tool
        def process_request(original_request: str, request_date: str, latest_date: Optional[str] = None) -> List[ItemQuantity]:
            """
            Process the original customer request to extract requested items and quantities.
            Stores results in agent state for use by subsequent tools.

            Args:
                original_request: The original customer request string.
                request_date: Date to check stock levels against (ISO format).
                latest_date: Latest acceptable date for order fulfillment (ISO format, optional).
            Returns:
                List of RequestedItem objects.
            """
            # Store original request for later reference
            self.state["original_request"] = original_request
            self.state["request_date"] = request_date
            self.state["latest_date"] = latest_date
            
            result = self.inventory_agent.run(f"""
            The customer request is: "{original_request}"
            The date of the request is: "{request_date}"
            Determine items and quantities requested by the customer.
            Use get_inventory_snapshot to get the current inventory.
            Map names in the request to inventory item names if possible.
            
            Return the requested items as a list of ItemQuantity objects.
            """)
            
            # Store intermediate result
            self.state["requested_items"] = result
            return result
        
        @tool
        def check_inventory(requested_items: List[ItemQuantity] = None, request_date: str = None) -> InventoryResult:
            """
            Check inventory for requested items and determine availability.
            Can use stored values from previous process_request if parameters not provided.

            Args:
                requested_items: List of RequestedItem objects (optional - uses stored if not provided).
                request_date: Date to check stock levels against (ISO format, optional - uses stored if not provided).
            Returns:
                InventoryResult object with list of item availabilities.
            """
            # Use stored values if not provided
            if requested_items is None:
                requested_items = self.state["requested_items"]
            if request_date is None:
                request_date = self.state["request_date"]
                
            result = self.inventory_agent.run(f"""
            The requested items are: "{requested_items}"
            The date to check inventory is: "{request_date}"
            For each item, check if it is in inventory using is_product_in_inventory.
            For each requested item that is in inventory, check if restocking is needed using check_restock_needed.
            Return an InventoryResult object with list of item availabilities.
            """)
            
            # Store result
            self.state["inventory_result"] = result
            return result
        
        @tool
        def can_order_be_fulfilled(inventory_result: InventoryResult = None, request_date: str = None, latest_date: str = None) -> bool:
            """
            Determine if the order can be fulfilled based on inventory results.
            Can use stored values if parameters not provided.

            Args:
                inventory_result: The result from check_inventory (optional - uses stored if not provided).
                request_date: The date the order is placed (ISO format, optional - uses stored if not provided).
                latest_date: Latest acceptable date for order fulfillment (ISO format, optional - uses stored if not provided).
            Returns:
                bool: True if all items can be fulfilled, False otherwise.
            """
            # Use stored value if not provided
            if inventory_result is None:
                inventory_result = self.state["inventory_result"]
            if request_date is None:
                request_date = self.state["request_date"]
            if latest_date is None:
                latest_date = self.state["latest_date"]
                
            result = self.inventory_agent.run(f"""
            The inventory result is: "{inventory_result}"
            The latest acceptable date for order fulfillment is: "{latest_date}"
            Determine if all requested items can be fulfilled (either in stock or can be restocked).
            For each item that needs restocking, check if it can be delivered by the latest acceptable date using get_delivery_date.
            Return True if all items can be fulfilled, otherwise return False.
            """)
            
            return result

        
        @tool
        def calculate_prices(inventory_result: InventoryResult = None) -> List[PriceInfo]:
            """
            Calculate prices for requested items based on inventory results.
            Can use stored values if parameters not provided.

            Args:
                inventory_result: The result from check_inventory (optional - uses stored if not provided).
            Returns:
                List of PriceInfo objects with item names, unit price and any discounts applied with reasons.
            """
            # Use stored values if not provided
            if inventory_result is None:
                inventory_result = self.state["inventory_result"]
                
            result = self.quoting_agent.run(f"""
            The inventory result is: "{inventory_result}"
            For each item in stock or in need of restocking, get the unit price using get_item_price.
            Apply a standard markup of 20% to determine the sales price.
            Return a list of PriceInfo objects with item names and unit prices.
            """)
            
            # Store result
            self.state["price_info"] = result
            return result
        
        @tool
        def determine_order_size(requested_items: List[ItemQuantity] = None) -> OrderSize:
            """
            Determine the order size (small, medium, large) based on the original customer request.

            Args:
                requested_items: List of ItemQuantity objects (optional - uses stored if not provided).
            Returns:
                OrderSize enum value.
            """
            # Use stored value if not provided
            if requested_items is None:
                requested_items = self.state["requested_items"]

            result = self.quoting_agent.run(f"""
            The customer request is: "{requested_items}"
            Analyze the request to determine the order size as small, medium, or large.
            Use historical quotes as reference if needed by fetching them using fetch_historical_quotes using item names as search terms.
            Return the order size as an OrderSize enum value.
            """)

            # Store result
            self.state["order_size"] = result
            return result

        @tool
        def calculate_discounted_prices(price_info: List[PriceInfo] = None, order_size: OrderSize = None) -> List[DiscountInfo]:
            """
            Calculate discounted prices for items based on historical quotes and original request.

            Args:
                price_info: List of PriceInfo objects (optional - uses stored if not provided).
                order_size: The determined order size (optional - uses stored if not provided).
            Returns:
                List of PriceInfo objects with updated discounted prices and reasons.
            """
            # Use stored values if not provided
            if price_info is None:
                price_info = self.state["price_info"]
            if order_size is None:
                order_size = self.state["order_size"]
            
            result = self.quoting_agent.run(f"""
            The price information is: "{price_info}"
            The order size is: "{order_size}"
            Based on the order size, determine if any discounts should be applied to the sales prices.
            For small orders, apply no discount.
            For medium orders, apply a 5% discount.
            For large orders, apply a 10% discount.
            """)

            # Store result
            self.state["discounted_prices_info"] = result
            return result

        @tool
        def get_delivery_schedule(requested_items: List[ItemQuantity] = None, inventory_result: List[InventoryResult] = None, order_date: str = None) -> List[DeliveryInfo]:
            """
            Get delivery schedule for items based on inventory results.
            Can use stored values if parameters not provided.

            Args:
                requested_items: List of ItemQuantity objects (optional - uses stored if not provided).
                inventory_result: The result from check_inventory (optional - uses stored if not provided).
                order_date: The date the order is placed (ISO format, optional - uses stored if not provided).
            Returns:
                List of DeliveryInfo objects with item names, quantities, and delivery dates.
            """
            # Use stored values if not provided
            if requested_items is None:
                requested_items = self.state["requested_items"]
            if inventory_result is None:
                inventory_result = self.state["inventory_result"]
            if order_date is None:
                order_date = self.state["request_date"]
                
            result = self.ordering_agent.run(f"""
            The requested items are: "{requested_items}"
            The inventory result is: "{inventory_result}"
            The order date is: "{order_date}"
            For each item that needs restocking, place an order for the requested quantity using order_stock.
            For each item in the inventory, schedule delivery for the requested quantity using schedule_delivery.
            """)
            
            # Store result
            self.state["delivery_info"] = result
            return result
        
        @tool
        def create_quote(delivery_info: List[DeliveryInfo] = None, discounted_prices_info: List[DiscountInfo] = None) -> str:
            """
            Create a quote for the customer based on delivery and discounted price information.
            Can use stored values if parameters not provided.

            Args:
                delivery_info: List of DeliveryInfo objects (optional - uses stored if not provided).
                discounted_prices_info: List of DiscountInfo objects (optional - uses stored if not provided).
            Returns:
                str: Formatted quote for the customer.
            """
            # Use stored values if not provided
            if delivery_info is None:
                delivery_info = self.state["delivery_info"]
            if discounted_prices_info is None:
                discounted_prices_info = self.state["discounted_prices_info"]
                
            result = self.quoting_agent.run(f"""
            The delivery information is: "{delivery_info}"
            The discounted price information is: "{discounted_prices_info}"
            Generate a quote based on the delivery and discounted price information.
            
            Use the following formatting for the quote:

            Thanks for your request! Here is your quote:

            Item Name | Quantity | Sales Price | Discounted Price | Delivery Date

            Total amount: $X.XX

            Provide a clear explanation of the quote including any discounts applied.
            """)
            
            # Store final quote
            self.state["final_quote"] = result
            return result
        
        @tool
        def get_state(key: str = None) -> dict:
            """
            Retrieve stored state for debugging or accessing previous results.

            Args:
                key: Optional specific state key to retrieve. If None, returns all state.
            Returns:
                dict: The requested state value(s).
            """
            if key:
                return {key: self.state.get(key)}
            return self.state.copy()
        
        @tool
        def reset_state() -> str:
            """
            Clear all stored intermediate results and prepare for a new request.

            Returns:
                str: Confirmation message.
            """
            self.state = {
                "original_request": None,
                "request_date": None,
                "latest_date": None,
                "requested_items": None,
                "inventory_result": None,
                "price_info": None,
                "order_size": None,
                "discount_info": None,
                "delivery_info": None,
                "final_quote": None
            }
            return "State cleared successfully - ready for new request"

        super().__init__(
            tools=[
                process_request,
                check_inventory,
                can_order_be_fulfilled,
                calculate_prices,
                determine_order_size,
                calculate_discounted_prices,
                get_delivery_schedule,
                create_quote,
                get_state,
                reset_state
            ],
            model=model,
            name="orchestration_agent",
            description="""
            You are the orchestrator for processing orders for a paper supply company.
            You coordinate between the inventory, quoting, and ordering agents to fulfill customer requests.
            
            For customer requests, follow this exact workflow:
            1. Extract the date of the request and the latest delivery date (if provided) from the request.
            2. Determine requested items and quantities using process_request (stores results in state)
            3. Use check_inventory to verify wether items are in inventory and wether they need restocking (stores results in state)
            4. Use can_order_be_fulfilled to check if the order can be fulfilled based on inventory and delivery dates
               If the order cannot be fulfilled, inform the customer accordingly and stop processing.
            5. Use calculate_prices to get pricing information for requested items (stores results in state)
            6. Use determine_order_size to classify the order size (stores results in state)
            7. Use calculate_discounted_prices to apply any discounts based on historical quotes (stores results in state)
            8. Use get_delivery_schedule to arrange deliveries (stores results in state)
            9. Use create_quote to generate a final quote for the customer (stores results in state)

            Output the final quote as the response to the customer.
            
            Note: Most tools can use stored state values automatically if parameters are not provided.
            Use get_state to inspect intermediate results if needed.
            Use reset_state when starting a new customer request.
            """,
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

    orchestration_agent = OrchestrationAgent(server_model)
    orchestration_agent.max_tool_threads = 1

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

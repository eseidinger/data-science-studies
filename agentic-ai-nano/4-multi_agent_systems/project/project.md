# Munder Difflin Multi-Agent System Workflow

## Overview

The Munder Difflin paper supply company uses a multi-agent system to process customer orders. The system consists of four specialized agents coordinated by an orchestration agent to handle inventory management, pricing, ordering, and quote generation.

![Workflow Diagram](project.png)

## Agent Architecture

### OrchestrationAgent

The central coordinator that manages the entire workflow from customer request to final quote. It delegates tasks to specialized agents and coordinates their activities to fulfill customer orders.

### InventoryAgent

Responsible for tracking and managing inventory stock levels. This agent has access to three key tools:

- `get_inventory_snapshot` - Retrieves current inventory status as of a specific date
- `is_product_in_inventory` - Checks if a product exists in inventory
- `check_restock_needed` - Determines if an item requires restocking based on minimum stock levels

### QuotingAgent

Handles pricing and quote generation. This agent utilizes:

- `get_item_price` - Retrieves the unit price for items from inventory
- `fetch_historical_quotes` - Searches past quotes to determine competitive pricing
- Quote generation capabilities to create final customer quotes

### OrderingAgent

Manages stock replenishment and delivery scheduling. This agent uses:

- `order_stock` - Places orders with suppliers for restocking items
- `schedule_delivery` - Arranges delivery dates based on order quantity and supplier lead times

## Workflow Steps

### 1. Process Request

The orchestration agent receives a customer request and delegates to the **InventoryAgent** to:

- Call `get_inventory_snapshot` to retrieve current inventory
- Parse the customer request to extract requested items and quantities
- Match requested items to actual inventory item names
- Return a list of `ItemQuantity` objects

### 2. Check Inventory

The **InventoryAgent** verifies availability for each requested item:

- Uses `is_product_in_inventory` to confirm items exist in the catalog
- Calls `check_restock_needed` to compare current stock against minimum levels
- Returns an `InventoryResult` containing:
  - `items_available` - Items with sufficient stock
  - `items_to_restock` - Items needing replenishment

### 3. Calculate Prices

The **QuotingAgent** determines pricing for all items:

- Retrieves unit prices using `get_item_price` for each item
- Searches historical quotes with `fetch_historical_quotes` using item names as search terms
- Analyzes historical pricing data to determine competitive prices
- Falls back to current unit prices if no historical data exists
- Returns a list of `PriceInfo` objects with item names and unit prices

### 4. Get Delivery Schedule

For items requiring restocking, the **OrderingAgent**:

- Places orders using `order_stock` for each item needing replenishment
  - Records stock order transaction in database
  - Calculates total order cost based on unit price and quantity
- Schedules deliveries with `schedule_delivery`
  - Determines delivery dates based on order quantity:
    - ≤10 units: same day
    - 11-100 units: 1 day
    - 101-1000 units: 4 days
    - >1000 units: 7 days
  - Records sales transaction for customer order
- Returns a list of `DeliveryInfo` objects with item names, quantities, and delivery dates

### 5. Create Quote

The **QuotingAgent** generates the final customer quote:

- Combines delivery information and pricing data
- Formats a comprehensive quote including:
  - Item names and quantities
  - Unit prices and total costs
  - Estimated delivery dates
  - Total order amount
- Returns formatted quote string for customer

## Data Flow

1. **Customer Request** → OrchestrationAgent receives and initiates workflow
2. **Item Extraction** → InventoryAgent identifies requested items from inventory
3. **Availability Check** → InventoryAgent categorizes items as available or needing restocking
4. **Pricing Analysis** → QuotingAgent determines competitive prices using historical data
5. **Order Placement** → OrderingAgent handles restocking for low-inventory items
6. **Delivery Scheduling** → OrderingAgent calculates delivery dates based on quantity
7. **Quote Generation** → QuotingAgent creates final customer quote with all details
8. **Customer Quote** → Final quote delivered to customer with pricing and delivery information

## Database Integration

The system maintains transactional integrity through the SQLite database:

- **transactions** table - Records all stock orders and sales with dates and amounts
- **inventory** table - Maintains item catalog with unit prices and minimum stock levels
- **quotes** table - Stores historical quotes for pricing analysis
- **quote_requests** table - Archives customer inquiries

All inventory calculations are date-aware, allowing the system to compute stock levels as of any specific date by summing stock orders and subtracting sales transactions.

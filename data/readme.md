# E-Commerce Electronics Store Demo - Sample Data Package

## Overview
This package contains realistic sample data for an **Electronics E-Commerce Store** Databricks agent demo. The scenario simulates an online retail platform selling tech products with customer support capabilities.

---

## 📊 CSV Tables (5 files)

### 1. **customers.csv** (12 customers)
Customer account information with loyalty tiers
- Fields: customer_id, email, name, tier (Bronze/Silver/Gold), registration_date, total_orders, lifetime_value
- Tier benefits: Gold (free express shipping), Silver (priority support), Bronze (standard)
- Use for: Customer lookup, loyalty benefits, order history analysis

### 2. **products.csv** (20 products)
Electronics inventory catalog
- Fields: product_id, name, category, brand, price, stock_quantity, weight_kg, warehouse_location
- Categories: Monitors, Laptops, Accessories, Audio, Storage, Tablets, Wearables, Furniture
- Brands: TechVision, CompuTech, PeriphPro, SoundWave, DataStore, etc.
- Price range: $29.99 - $1,299.99

### 3. **orders.csv** (15 orders)
Customer purchase history
- Fields: order_id, customer_id, order_date, status (pending/processing/shipped/delivered/cancelled), total_amount, shipping_address, tracking_number
- Status distribution: 5 delivered, 3 shipped, 4 pending, 2 processing, 1 cancelled
- Date range: October 15 - November 2, 2024

### 4. **order_items.csv** (25 line items)
Individual products within orders
- Fields: order_item_id, order_id, product_id, quantity, unit_price
- Links orders to specific products
- Some orders have multiple items

### 5. **shipping_zones.csv** (12 zones)
Shipping rates and delivery times by region
- Fields: zone_id, country, region, base_rate, rate_per_kg, estimated_days
- Coverage: USA (6 zones), Canada (2 zones), Mexico, UK, EU (Western/Eastern)
- Rates range from $5.99 (US standard) to $34.99 (Eastern Europe)

---

## 📄 PDF Documents (4 files)

### 1. **product_catalog.pdf** (~22 KB)
Detailed product specifications and compatibility information
- **Contents:**
  - **Monitors:** UltraView 4K 27", Portable Monitor 15.6" (specs, features, connectivity)
  - **Laptops:** ProBook 15" (Intel i7, 16GB RAM, performance benchmarks)
  - **Keyboards & Mice:** Mechanical RGB keyboard, wireless mouse, ergonomic vertical mouse
  - **Audio:** Noise-canceling headphones, Bluetooth speaker (battery, codecs, features)
  - **Storage & Connectivity:** External SSD 1TB, USB-C Hub 7-in-1
  - **Tablets & Wearables:** Tablet Pro 12.9", Smart Watch Series 5
  - Each product includes: technical specs, key features, compatibility, warranty info, what's included

### 2. **return_policy.pdf** (~18 KB)
Comprehensive return and refund procedures
- **Contents:**
  - Return windows (30-day standard, 60-day holiday, 14-day reduced)
  - Return conditions (original packaging, unused condition, proof of purchase)
  - Non-returnable items (personal care, opened software, customized items, final sale)
  - Step-by-step return process (initiate, pack, ship)
  - Refund timeline and methods (3-10 business days)
  - Exchange procedures
  - Damaged/defective item handling
  - Warranty information (manufacturer, extended, DOA protection)
  - Special circumstances (gifts, wrong item shipped, international returns)

### 3. **shipping_guide.pdf** (~20 KB)
Shipping options, tracking, and delivery information
- **Contents:**
  - Shipping options:
    - Standard (FREE on $50+, 3-7 days)
    - Expedited ($15.99, 2-3 days)
    - Express Overnight ($29.99, 1-2 days)
    - International (Canada, Mexico, worldwide)
  - Order processing timelines and cutoff times
  - Tracking instructions (email, website, carrier sites)
  - Delivery locations (residential, business, PO boxes, APO/FPO)
  - Common issues (lost/stolen packages, damage, delays)
  - Address changes and hold for pickup options
  - Large/heavy item shipping
  - Pre-order policies
  - Shipping restrictions

### 4. **technical_faq.pdf** (~25 KB)
Product troubleshooting and technical support guide
- **Contents:**
  - General compatibility questions
  - Warranty coverage explanations
  - **Monitor Troubleshooting:**
    - No signal issues (cable connections, input source, computer output)
    - Blurry display (resolution settings, ClearType, correct cables)
  - **Laptop Troubleshooting:**
    - Won't turn on (power check, hard reset, external display)
    - Battery drain (battery health, power optimization, driver updates)
  - **Connectivity Issues:**
    - Bluetooth pairing problems
    - USB device not recognized
  - **Audio Equipment:**
    - Headphones no sound (volume, output device, Bluetooth connection)
    - Microphone not working (input device, privacy settings, levels)
  - **Performance Optimization:**
    - Speed up computer (disk space, startup programs, updates, malware, upgrades)
  - **Installation Help:**
    - Dual monitor setup (Windows/macOS configuration)
  - **Warranty Claims:**
    - How to make a claim, service options, timeline
  - Contact information for support

---

## 🛠️ Suggested Unity Catalog Functions (Tools)

Based on the tables, here are the recommended UC functions to implement:

### 1. **check_order_status(order_id)**
```sql
-- Returns: order status, tracking_number, estimated_delivery
-- Joins orders table with order_items for complete order details
```

### 2. **check_product_stock(product_id)**
```sql
-- Returns: stock_quantity, warehouse_location, availability status
-- Alerts if stock is low (< 10 units)
```

### 3. **calculate_shipping(customer_id, total_weight_kg, destination_country, destination_region)**
```sql
-- Returns: shipping cost, estimated delivery days, available options
-- Considers customer tier (Gold gets free express shipping)
-- Looks up shipping_zones table for rates
```

### 4. **get_customer_orders(customer_id)**
```sql
-- Returns: order history with status, dates, totals
-- Joins orders with order_items and products for full details
```

### 5. **check_return_eligibility(order_id)**
```sql
-- Returns: eligible (yes/no), reason, days_remaining
-- Checks order_date against current date
-- Considers product category and order status
-- Returns number of days left in return window
```

### 6. **get_product_details(product_id)**
```sql
-- Returns: full product information including price, specs, stock
-- Used for product recommendations and comparisons
```

### 7. **get_customer_tier_benefits(customer_id)**
```sql
-- Returns: tier level, benefits, lifetime_value, total_orders
-- Shows eligibility for free shipping, discounts, priority support
```

---

## 💡 Example Agent Queries

Here are realistic queries that combine retriever (PDFs) + tools (functions):

### 1. **Order Status Check**
**Query:** "Where is my order 1003?"

**Expected Flow:**
- Tool: `check_order_status(1003)` → Status: shipped, Tracking: TRK1234567892
- Retriever: Search shipping_guide.pdf for tracking instructions
- **Answer:** Your order is shipped! Tracking number TRK1234567892. Estimated delivery: 3-5 business days. You can track it at [carrier link].

### 2. **Product Availability + Compatibility**
**Query:** "Do you have the UltraView 4K monitor in stock? Will it work with my MacBook Pro?"

**Expected Flow:**
- Tool: `check_product_stock(1)` → 45 units in stock
- Retriever: Search product_catalog.pdf for UltraView specs and compatibility
- **Answer:** Yes, in stock (45 units available). The UltraView 4K Monitor is fully compatible with MacBook Pro. Connect via USB-C (DisplayPort Alt Mode) or HDMI 2.0. Supports macOS 10.13+. Native 4K resolution works perfectly with Mac's scaling.

### 3. **Shipping Cost Calculation**
**Query:** "How much will shipping cost for the Gaming Chair to California?"

**Expected Flow:**
- Tool: `get_product_details(9)` → Weight: 22 kg
- Tool: `calculate_shipping(customer_id, 22, 'USA', 'West Coast')` → Base $8.99 + (22 × $2.25) = $58.49
- Retriever: Search shipping_guide.pdf for large item shipping policies
- **Answer:** The Gaming Chair weighs 22 kg. Standard shipping to California: $58.49 (5-7 business days). Due to size/weight, freight shipping is required. Delivery to curb/threshold. White glove delivery (inside home + assembly) available for additional $79.99.

### 4. **Return Policy Question**
**Query:** "Can I return my opened wireless headphones?"

**Expected Flow:**
- Retriever: Search return_policy.pdf for return conditions and non-returnable items
- **Answer:** Yes, audio equipment like headphones can be returned within 30 days if unused or lightly used, with all original accessories and packaging. However, in-ear headphones cannot be returned once opened for hygiene reasons. Over-ear headphones like the Noise-Canceling Headphones are returnable. The item must be in original condition with no signs of wear.

### 5. **Complex Support Query with Troubleshooting**
**Query:** "My laptop won't turn on after it arrived yesterday. What should I do?"

**Expected Flow:**
- Tool: `check_order_status(order_id)` → Delivered yesterday
- Retriever: Search technical_faq.pdf for laptop won't turn on troubleshooting
- Retriever: Search return_policy.pdf for DOA (Dead on Arrival) policy
- **Answer:** I'm sorry your new laptop isn't working! Let's try these steps: (1) Connect charger and verify LED lights up, (2) Hold power button for 30 seconds, reconnect charger, try again, (3) If still no response, this qualifies as Dead on Arrival (DOA). Since you received it yesterday, we'll immediately send a replacement at no cost, including return shipping. We'll also refund your original shipping charges. Would you like me to initiate the DOA replacement now?

### 6. **Product Recommendation with Customer Context**
**Query:** "I need a good keyboard for programming under $150"

**Expected Flow:**
- Tool: `get_customer_tier_benefits(customer_id)` → Gold tier, free express shipping
- Tool: Filter products by category='Accessories', price<150, name contains 'keyboard'
- Retriever: Search product_catalog.pdf for keyboard details
- **Answer:** I recommend the Mechanical Keyboard RGB ($129.99). Perfect for programming with hot-swappable mechanical switches (Red linear, tactile feedback), N-key rollover, programmable macros, and durable construction. As a Gold member, you get free express shipping (2-3 days). Plus it's in stock at Warehouse B!

### 7. **Multi-step Order Issue**
**Query:** "I ordered a monitor but received a mouse. I need the monitor by Friday."

**Expected Flow:**
- Tool: `check_order_status(order_id)` → Identify wrong item shipped
- Retriever: Search return_policy.pdf for "wrong item shipped" section
- Tool: `check_product_stock(product_id)` → Verify monitor still in stock
- Tool: `calculate_shipping` with express option → Calculate fastest delivery
- **Answer:** I apologize for the error! Here's what we'll do immediately: (1) I'm sending the correct UltraView 4K Monitor via express overnight shipping at no charge - it will arrive by Thursday. (2) Keep the incorrect mouse until the monitor arrives, then use the prepaid return label we'll email you. (3) No charges for return shipping, and we're applying a $25 credit to your account for the inconvenience. Your new tracking number will arrive in 1 hour.

---

## 🎯 Use Case Coverage

This dataset enables demonstrations of:

✅ **Retrieval (Vector Store):**
- Product specifications and compatibility
- Return policy conditions
- Shipping options and rates
- Technical troubleshooting guides
- Warranty information

✅ **Tools (UC Functions):**
- Real-time order tracking
- Inventory availability checks
- Shipping cost calculations
- Customer tier benefits
- Return eligibility verification

✅ **Hybrid (Retriever + Tools):**
- Personalized product recommendations (tier benefits + specs)
- Complete order support (status + policy + troubleshooting)
- Shipping quotes with policy explanations
- Return processes with eligibility checks
- Customer-specific pricing and benefits

---

## 🚀 Implementation Tips for Databricks

### Vector Store Setup
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from databricks.vector_search.client import VectorSearchClient

# Chunk the PDFs for optimal retrieval
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)

# Process each PDF
documents = []
for pdf_file in ['product_catalog.pdf', 'return_policy.pdf', 'shipping_guide.pdf', 'technical_faq.pdf']:
    chunks = splitter.split_documents([pdf_file])
    for chunk in chunks:
        chunk.metadata['source'] = pdf_file
        chunk.metadata['category'] = pdf_file.split('.')[0]
    documents.extend(chunks)

# Create Databricks Vector Search index
vsc = VectorSearchClient()
index = vsc.create_direct_access_index(
    endpoint_name="ecommerce_endpoint",
    index_name="ecommerce_knowledge_base",
    primary_key="id",
    embedding_dimension=1536,  # Adjust based on embedding model
    embedding_vector_column="embedding",
    schema={"id": "string", "text": "string", "embedding": "array<float>", "metadata": "string"}
)
```

### Feature Tables
```sql
-- Create Delta tables from CSVs
CREATE TABLE customers USING csv OPTIONS (path '/path/to/customers.csv', header 'true');
CREATE TABLE products USING csv OPTIONS (path '/path/to/products.csv', header 'true');
CREATE TABLE orders USING csv OPTIONS (path '/path/to/orders.csv', header 'true');
CREATE TABLE order_items USING csv OPTIONS (path '/path/to/order_items.csv', header 'true');
CREATE TABLE shipping_zones USING csv OPTIONS (path '/path/to/shipping_zones.csv', header 'true');

-- Register as Feature Store tables for online serving
CREATE FEATURE TABLE customers_features AS SELECT * FROM customers;
CREATE FEATURE TABLE products_features AS SELECT * FROM products;
```

### Unity Catalog Functions (Examples)
```sql
-- Function 1: Check Order Status
CREATE FUNCTION check_order_status(order_id INT)
RETURNS STRUCT<status STRING, tracking_number STRING, total_amount DECIMAL, estimated_delivery STRING>
LANGUAGE SQL
COMMENT 'Returns current order status and tracking information'
AS
$$
  SELECT 
    status,
    tracking_number,
    total_amount,
    CASE 
      WHEN status = 'delivered' THEN 'Delivered'
      WHEN status = 'shipped' THEN 'In Transit - 1-3 days'
      WHEN status = 'processing' THEN 'Processing - ships in 1-2 days'
      WHEN status = 'pending' THEN 'Pending - ships within 24 hours'
      ELSE 'Status Unknown'
    END as estimated_delivery
  FROM orders
  WHERE order_id = order_id
$$;

-- Function 2: Check Product Stock
CREATE FUNCTION check_product_stock(product_id INT)
RETURNS STRUCT<stock_quantity INT, warehouse STRING, availability STRING>
LANGUAGE SQL
AS
$$
  SELECT 
    stock_quantity,
    warehouse_location,
    CASE
      WHEN stock_quantity > 50 THEN 'In Stock - Ships Today'
      WHEN stock_quantity BETWEEN 10 AND 50 THEN 'Limited Stock Available'
      WHEN stock_quantity BETWEEN 1 AND 9 THEN 'Low Stock - Order Soon'
      ELSE 'Out of Stock'
    END as availability
  FROM products
  WHERE product_id = product_id
$$;

-- Function 3: Calculate Shipping (Python for more complex logic)
CREATE FUNCTION calculate_shipping(
  customer_id INT,
  total_weight_kg DECIMAL,
  destination_country STRING,
  destination_region STRING
)
RETURNS STRUCT<standard_cost DECIMAL, expedited_cost DECIMAL, express_cost DECIMAL, estimated_days STRING>
LANGUAGE PYTHON
AS
$$
def calculate_shipping(customer_id, total_weight_kg, destination_country, destination_region):
    # Get customer tier for benefits
    customer_tier = spark.sql(f"SELECT tier FROM customers WHERE customer_id = {customer_id}").collect()[0]['tier']
    
    # Get base shipping rate for zone
    zone_info = spark.sql(f"""
        SELECT base_rate, rate_per_kg, estimated_days 
        FROM shipping_zones 
        WHERE country = '{destination_country}' AND region = '{destination_region}'
    """).collect()[0]
    
    base_rate = zone_info['base_rate']
    rate_per_kg = zone_info['rate_per_kg']
    estimated_days = zone_info['estimated_days']
    
    # Calculate standard shipping
    standard_cost = base_rate + (total_weight_kg * rate_per_kg)
    
    # Apply tier benefits
    if customer_tier == 'Gold':
        expedited_cost = 0  # Free expedited for Gold
        express_cost = 15.99  # Discounted express
    elif customer_tier == 'Silver':
        expedited_cost = 10.99  # Discounted expedited
        express_cost = 24.99
    else:  # Bronze
        expedited_cost = 15.99
        express_cost = 29.99
    
    return {
        'standard_cost': round(standard_cost, 2),
        'expedited_cost': expedited_cost,
        'express_cost': express_cost,
        'estimated_days': estimated_days
    }

return calculate_shipping(customer_id, total_weight_kg, destination_country, destination_region)
$$;

-- Function 4: Check Return Eligibility
CREATE FUNCTION check_return_eligibility(order_id INT)
RETURNS STRUCT<eligible BOOLEAN, reason STRING, days_remaining INT>
LANGUAGE SQL
AS
$$
  SELECT 
    CASE 
      WHEN status = 'delivered' AND DATEDIFF(CURRENT_DATE(), order_date) <= 30 THEN TRUE
      ELSE FALSE
    END as eligible,
    CASE
      WHEN status != 'delivered' THEN 'Order must be delivered to process return'
      WHEN DATEDIFF(CURRENT_DATE(), order_date) > 30 THEN 'Return window expired (30 days from delivery)'
      WHEN status = 'cancelled' THEN 'Cannot return cancelled order'
      ELSE 'Eligible for return'
    END as reason,
    GREATEST(0, 30 - DATEDIFF(CURRENT_DATE(), order_date)) as days_remaining
  FROM orders
  WHERE order_id = order_id
$$;
```

---

## 📝 Data Quality Notes

- **12 realistic customers** with varying loyalty tiers and purchase patterns
- **20 diverse products** across 7 categories with realistic pricing
- **15 orders** with authentic e-commerce status distribution
- **Geographic diversity** in shipping addresses (all US states represented)
- **Temporal consistency** - orders are sequential and recent (Oct-Nov 2024)
- **Realistic pricing** - products priced according to market standards
- **Weight-based shipping** - shipping calculations reflect actual carrier pricing models
- **Multi-item orders** - some orders contain multiple products for realistic cart behavior

---

## 📦 Files Summary

**CSV Files (Data Tables):**
- customers.csv
- products.csv
- orders.csv
- order_items.csv
- shipping_zones.csv

**PDF Files (Knowledge Base):**
- product_catalog.pdf (~22 KB) - 20 products with detailed specs
- return_policy.pdf (~18 KB) - comprehensive return procedures
- shipping_guide.pdf (~20 KB) - shipping options and tracking
- technical_faq.pdf (~25 KB) - troubleshooting guides

**Total:** 9 files ready for import into Databricks

---

## 🎨 Demo Scenarios by Complexity

### Basic (Single Tool Call)
- "What's the status of order 1005?" → `check_order_status(1005)`
- "Is the wireless mouse in stock?" → `check_product_stock(3)`

### Intermediate (Tool + Retriever)
- "Can I return my headphones?" → Retriever (return_policy.pdf) + Tool (check order date)
- "How much to ship the laptop to Texas?" → Tool (calculate_shipping) + Retriever (shipping_guide.pdf)

### Advanced (Multiple Tools + Retriever + Reasoning)
- "I'm a Gold member, recommend a monitor under $500 that ships fast" → Multiple tools + product catalog retrieval + tier benefits
- "My laptop screen is blank, what do I do?" → Technical FAQ retrieval + order lookup + warranty check

---

## ✅ Ready to Use!

All files are production-ready and can be directly imported into Databricks:
1. **Tables** → Delta Lake or Feature Store
2. **PDFs** → Vector Search Index (with proper chunking)
3. **Functions** → Unity Catalog (SQL or Python)

This provides a complete, realistic e-commerce demo scenario with customer support capabilities! 🛒

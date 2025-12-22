# Agent Evaluation Dataset - E-Commerce Electronics Store

## 📦 What You've Received

A comprehensive evaluation dataset to test your **AI Agent** that combines UC Functions (tools) and RAG (retriever) for an e-commerce electronics store demo.

## 🎯 Key Difference: Agent vs. RAG Evaluation

| Aspect | RAG-Only | Agent (This Dataset) |
|--------|----------|----------------------|
| **Data Access** | PDFs only | PDFs + CSV tables |
| **Capabilities** | Retrieval only | Tools + Retrieval + Reasoning |

---

## 📄 File Included. **agent_evaluation_dataset.csv**
Complete structured dataset with:
- 5 agent queries with varying complexity
- Required tools and retriever specifications
- Expected capabilities and evaluation criteria
- Detailed expected information

---

## 🛠️ What Your Agent Needs

### Required UC Functions (Tools)
```python
1. check_order_status(order_id)
2. check_product_stock(product_id)
3. get_product_details(product_id)
4. calculate_shipping(customer_id, weight, country, region)
5. get_customer_tier_benefits(customer_id)
6. get_customer_orders(customer_id)
```

### Required Data Sources
**CSV Tables:**
- customers.csv
- products.csv
- orders.csv
- order_items.csv
- shipping_zones.csv

**PDF Documents:**
- product_catalog.pdf
- return_policy.pdf
- shipping_guide.pdf
- technical_faq.pdf

---




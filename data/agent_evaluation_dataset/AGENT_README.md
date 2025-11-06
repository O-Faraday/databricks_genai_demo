# Agent Evaluation Dataset - E-Commerce Electronics Store

## 📦 What You've Received

A comprehensive evaluation dataset to test your **AI Agent** that combines UC Functions (tools) and RAG (retriever) for an e-commerce electronics store demo.

## 🎯 Key Difference: Agent vs. RAG Evaluation

| Aspect | RAG-Only | Agent (This Dataset) |
|--------|----------|----------------------|
| **Data Access** | PDFs only | PDFs + CSV tables |
| **Capabilities** | Retrieval only | Tools + Retrieval + Reasoning |
| **Complexity** | Single-step | Multi-step orchestration |
| **Decision Making** | None | When to use which capability |

---

## 📄 Files Included

### 1. **agent_evaluation_dataset.json** (Primary)
Complete structured dataset with:
- 15 agent queries with varying complexity
- Required tools and retriever specifications
- Expected capabilities and evaluation criteria
- Detailed expected information

**Use for:** Automated evaluation scripts

---

### 2. **agent_evaluation_dataset.csv**
Simplified spreadsheet format (semicolon-delimited)

**Use for:** Manual tracking, team reviews, Excel/Sheets

**Load with:**
```python
import pandas as pd
df = pd.read_csv('agent_evaluation_dataset.csv', sep=';')
```

---

### 3. **AGENT_EVALUATION_GUIDE.md** (Documentation)
Comprehensive 40+ page guide covering:
- Query type breakdown
- Tool and retriever mapping
- Detailed query analysis
- Scoring rubrics
- Testing strategy
- Common failure patterns

**Use for:** Understanding the dataset and evaluation methodology

---

## 📊 Dataset Overview

### Query Distribution

| Category | Count | Description |
|----------|-------|-------------|
| **Tool-Only** | 2 | Tests function calling on CSV data |
| **Retriever-Only** | 6 | Tests RAG on PDF documents |
| **Hybrid Tool+Retriever** | 4 | Tests combining both capabilities |
| **Multi-Step** | 3 | Tests complex orchestration |

### Difficulty Distribution

| Level | Count | Pass Rate Target |
|-------|-------|------------------|
| **Easy** | 6 | 90%+ |
| **Medium** | 6 | 75%+ |
| **Hard** | 3 | 60%+ |

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

## 🚀 Quick Start

### Option 1: Automated Evaluation

```python
import json

# Load dataset
with open('agent_evaluation_dataset.json', 'r') as f:
    queries = json.load(f)

# Run evaluation
total_score = 0
for query_item in queries:
    # Run agent
    response = your_agent.run(query_item['query'])
    
    # Evaluate
    score = evaluate(
        response,
        expected_tools=query_item['required_tools'],
        expected_retriever=query_item['required_retriever'],
        criteria=query_item['evaluation_criteria']
    )
    
    total_score += score
    print(f"Query {query_item['query_id']}: {score}/5")

avg_score = total_score / len(queries)
print(f"\n🎯 Average Score: {avg_score:.2f}/5.0")
print(f"{'✅ PASS' if avg_score >= 4.0 else '❌ NEEDS IMPROVEMENT'}")
```

---

### Option 2: Manual Testing

1. Open `agent_evaluation_dataset.csv` in Excel/Sheets
2. Add columns: `agent_response`, `score`, `notes`
3. Run each query through your agent
4. Score 0-5 based on evaluation criteria
5. Calculate average score

**Target:** ≥ 4.0/5.0 overall

---

## 📈 Query Examples by Type

### Easy - Tool Only
```
Q1: "Where is my order 1003?"
Expected: Call check_order_status(1003), return tracking info
```

### Easy - Retriever Only
```
Q3: "Can I return opened software?"
Expected: Search return_policy.pdf, answer: No (non-returnable)
```

### Medium - Hybrid
```
Q2: "Do you have the UltraView 4K monitor in stock? Will it work with my MacBook Pro?"
Expected:
- Tool: check_product_stock() for inventory
- Retriever: product_catalog.pdf for compatibility
- Synthesize both in answer
```

### Hard - Multi-Step
```
Q10: "I ordered a monitor but received a mouse. I need the monitor by Friday."
Expected:
- Tool: check_order_status() to verify
- Retriever: return_policy.pdf for wrong item policy
- Tool: check_product_stock() for availability
- Tool: calculate_shipping() for express delivery
- Provide complete resolution plan
```

---

## 🎯 Evaluation Criteria

### Score each query 0-5:

| Score | Description |
|-------|-------------|
| **5** | Perfect - All tools/retriever used correctly, complete answer |
| **4** | Good - Correct approach, minor issues |
| **3** | Adequate - Partially correct, missing information |
| **2** | Poor - Wrong approach or significant gaps |
| **1** | Very Poor - Mostly incorrect |
| **0** | Failed - No answer or completely wrong |

### What to Check:

✅ **Tool Selection** - Used correct functions with right parameters  
✅ **Retriever Quality** - Retrieved relevant PDF sections  
✅ **Completeness** - Answered all parts of multi-part questions  
✅ **Synthesis** - Combined tool + retriever results coherently  
✅ **UX** - Clear, actionable, empathetic responses  

---

## 📋 Testing Strategy

### Phase 1: Basic (Queries 1, 3, 6, 7, 9, 11)
Validate that tools and retriever work independently.

### Phase 2: Hybrid (Queries 2, 4, 8, 12, 13, 14)
Test ability to combine tools and retriever.

### Phase 3: Advanced (Queries 5, 10, 15)
Validate multi-step reasoning and complex orchestration.

---

## 🚨 Common Failure Patterns

### 1. Wrong Capability Used
- ❌ Using retriever to check stock (should use tool)
- ❌ Using tool to look up return policy (should use retriever)

### 2. Incomplete Answers
- ❌ Only answering first part of multi-part question
- ❌ Using only tool when retriever also needed

### 3. Poor Orchestration
- ❌ Not calling tools in logical order
- ❌ Not passing context between steps

### 4. Missing Personalization
- ❌ Not checking customer tier for benefits
- ❌ Not verifying order status before suggesting action

---

## 📊 Data Source Coverage

### Tools (UC Functions) Usage
- **orders.csv**: 4 queries (1, 5, 7, 10)
- **products.csv**: 6 queries (2, 4, 8, 10, 13, 15)
- **customers.csv**: 2 queries (7, 8)
- **shipping_zones.csv**: 2 queries (4, 10)

### Retriever (PDF) Usage
- **product_catalog.pdf**: 5 queries (2, 6, 8, 13, 15)
- **return_policy.pdf**: 5 queries (3, 5, 9, 10, 12)
- **shipping_guide.pdf**: 3 queries (4, 10, 14)
- **technical_faq.pdf**: 2 queries (5, 11)

---

## 🎓 What This Tests

✅ **Tool Calling** - Can agent identify and call correct UC functions?  
✅ **RAG Quality** - Can agent retrieve relevant PDF information?  
✅ **Hybrid Reasoning** - Can agent combine tools + retriever?  
✅ **Multi-Step Planning** - Can agent orchestrate complex workflows?  
✅ **Decision Making** - Does agent know when to use which capability?  
✅ **Customer Service** - Are responses empathetic and actionable?  

---

## 💡 Example Agent Architecture

```python
class EcommerceAgent:
    """
    Agent with tools (UC functions) and retriever (vector store)
    """
    def __init__(self):
        self.tools = load_uc_functions()  # 6 functions
        self.retriever = VectorStore(pdfs=['product_catalog', ...])
        self.llm = LLM(model='claude-4-sonnet')
    
    def run(self, query: str):
        # 1. Plan what to do
        plan = self.llm.create_plan(query)
        
        # 2. Execute tools if needed
        tool_results = []
        if plan.use_tools:
            for tool in plan.tools:
                result = self.tools[tool.name](**tool.params)
                tool_results.append(result)
        
        # 3. Search documents if needed
        doc_results = []
        if plan.use_retriever:
            doc_results = self.retriever.search(query)
        
        # 4. Synthesize final answer
        answer = self.llm.synthesize(
            query=query,
            tool_results=tool_results,
            doc_results=doc_results
        )
        
        return answer
```

---

## 📈 Success Metrics

| Metric | Target | Excellent |
|--------|--------|-----------|
| **Overall Average** | ≥ 4.0 | ≥ 4.5 |
| **Tool-Only Queries** | ≥ 4.5 | 5.0 |
| **Retriever-Only** | ≥ 4.2 | ≥ 4.7 |
| **Hybrid Queries** | ≥ 3.8 | ≥ 4.3 |
| **Multi-Step Queries** | ≥ 3.5 | ≥ 4.0 |

---

## 🔗 Related Datasets

This package also includes:
- **rag_evaluation_dataset.json** - 15 queries for PDF-only RAG testing
- Use both datasets to comprehensively evaluate your system

---

## 📝 Version & Support

- **Version:** 1.0
- **Created:** November 2025
- **Purpose:** Agent evaluation for Databricks E-Commerce demo
- **Dataset Type:** Agent (Tools + Retriever)

---

## ✅ Checklist Before Testing

- [ ] All 6 UC functions implemented
- [ ] All 5 CSV tables loaded in Delta Lake
- [ ] All 4 PDFs indexed in vector store
- [ ] Agent can call tools programmatically
- [ ] Agent can retrieve from vector store
- [ ] Agent has reasoning/planning capability
- [ ] Evaluation framework ready

---

## 🎉 Ready to Evaluate!

1. Load the JSON dataset
2. Run each query through your agent
3. Score using the 0-5 rubric
4. Calculate average score
5. Identify improvement areas
6. Iterate and improve

**Goal:** Average score ≥ 4.0/5.0

---

**Good luck testing your agent! 🚀**

*For detailed documentation, see AGENT_EVALUATION_GUIDE.md*

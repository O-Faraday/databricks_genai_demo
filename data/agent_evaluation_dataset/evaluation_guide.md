# Agent Evaluation Dataset - E-Commerce Electronics Store

## Overview
This evaluation dataset contains **15 carefully crafted queries** designed to comprehensively test an **AI Agent** that combines:
- 🔧 **UC Functions/Tools** - for accessing structured data (CSV tables)
- 📚 **Retriever/RAG** - for accessing unstructured knowledge (PDF documents)
- 🤖 **Hybrid Reasoning** - combining both capabilities for complex scenarios

## What Makes This Different from RAG-Only Evaluation?

This dataset evaluates an **Agent**, not just a RAG system. The agent must:
- **Decide** when to use tools vs. retriever
- **Execute** multiple steps in sequence
- **Synthesize** information from databases AND documents
- **Reason** about which capability to use for each query

## Dataset Statistics

| Metric | Count |
|--------|-------|
| **Total Queries** | 15 |
| **Tool-Only Queries** | 2 |
| **Retriever-Only Queries** | 6 |
| **Hybrid Queries** | 7 |
| **Easy Difficulty** | 6 |
| **Medium Difficulty** | 6 |
| **Hard Difficulty** | 3 |

## Query Type Breakdown

### 1. Tool-Only Queries (2 queries)
These test the agent's ability to use UC Functions to query structured data.

**Queries:** 1, 7

**Examples:**
- "Where is my order 1003?" → Uses `check_order_status()`
- "I'm a Gold member. What are my benefits?" → Uses `get_customer_tier_benefits()`

**Required Capabilities:**
- Function calling
- Parameter extraction
- Structured data interpretation

---

### 2. Retriever-Only Queries (6 queries)
These test traditional RAG capabilities - retrieving information from PDFs.

**Queries:** 3, 6, 9, 11, 12, 14

**Examples:**
- "Can I return opened software?" → Search return_policy.pdf
- "My monitor displays a blurry image. How can I fix this?" → Search technical_faq.pdf

**Required Capabilities:**
- Semantic search
- Context retrieval
- Information synthesis from documents

---

### 3. Hybrid Tool + Retriever Queries (4 queries)
These require BOTH tools and retriever to answer completely.

**Queries:** 2, 4, 8, 13

**Example:**
- "Do you have the UltraView 4K monitor in stock? Will it work with my MacBook Pro?"
  - Tool: `check_product_stock()` for inventory
  - Retriever: product_catalog.pdf for compatibility

**Required Capabilities:**
- Multi-source information gathering
- Tool + document synthesis
- Deciding which capability to use for each sub-question

---

### 4. Hybrid Multi-Step Queries (3 queries) 🔥
The most complex scenarios requiring multiple tools, retriever access, and sophisticated reasoning.

**Queries:** 5, 10, 15

**Example:**
- "My laptop won't turn on after it arrived yesterday. What should I do?"
  - Tool: `check_order_status()` to verify delivery
  - Retriever: technical_faq.pdf for troubleshooting
  - Retriever: return_policy.pdf for DOA policy
  - Reasoning: Decide whether to troubleshoot or offer replacement

**Required Capabilities:**
- Multi-step planning
- Multiple tool calls
- Multiple document retrievals
- Complex reasoning and decision-making
- Empathetic customer service

---

## Data Sources Coverage

### CSV Tables (Accessed via UC Functions/Tools)
| Table | Queries Using It |
|-------|------------------|
| orders.csv | 1, 5, 7, 10 |
| products.csv | 2, 4, 8, 10, 13, 15 |
| customers.csv | 7, 8 |
| shipping_zones.csv | 4, 10 |
| order_items.csv | (indirect via orders) |

### PDF Documents (Accessed via Retriever/RAG)
| Document | Queries Using It |
|----------|------------------|
| product_catalog.pdf | 2, 6, 8, 13, 15 |
| return_policy.pdf | 3, 5, 9, 10, 12 |
| shipping_guide.pdf | 4, 10, 14 |
| technical_faq.pdf | 5, 11 |

---

## UC Functions Required

Based on the queries, your agent needs these UC Functions:

1. **check_order_status(order_id)** - Used in: Q1, Q5, Q10
2. **check_product_stock(product_id)** - Used in: Q2, Q8, Q10, Q13, Q15
3. **get_product_details(product_id)** - Used in: Q4, Q8, Q15
4. **calculate_shipping(customer_id, weight, country, region)** - Used in: Q4, Q10
5. **get_customer_tier_benefits(customer_id)** - Used in: Q7, Q8
6. **get_customer_orders(customer_id)** - Used in: Q7

---

## Detailed Query Analysis

### Easy Queries (6 queries)

| ID | Query | Type | What It Tests |
|----|-------|------|---------------|
| 1 | Where is my order 1003? | Tool-only | Basic function calling |
| 3 | Can I return opened software? | Retriever | Simple policy lookup |
| 6 | ProBook 15" specs? | Retriever | Product info retrieval |
| 7 | Gold member benefits + orders? | Tool-only | Multiple function calls |
| 9 | Holiday return window? | Retriever | Policy variation understanding |
| 11 | Blurry monitor fix? | Retriever | Troubleshooting retrieval |

**Success Criteria:** Agent correctly identifies data source and retrieves information.

---

### Medium Queries (6 queries)

| ID | Query | Type | What It Tests |
|----|-------|------|---------------|
| 2 | UltraView stock + MacBook compatibility? | Hybrid | Tool + retriever synthesis |
| 4 | Gaming Chair shipping to CA? | Hybrid | Weight lookup + shipping calculation + policy |
| 8 | Keyboard under $150 for programming? | Hybrid | Product filtering + specs + personalization |
| 12 | Return if opened but unused? | Retriever | Policy nuance understanding |
| 13 | Bluetooth speaker stock + battery? | Hybrid | Stock check + spec retrieval |
| 14 | Track package + lost package process? | Retriever | Multi-part policy question |

**Success Criteria:** Agent combines multiple sources, provides complete answers, shows understanding of context.

---

### Hard Queries (3 queries) 🔥

**Query 5: Laptop Won't Turn On (Empathetic Support)**
```
My laptop won't turn on after it arrived yesterday. What should I do?
```

**Required Flow:**
1. Verify delivery (tool: check_order_status)
2. Provide troubleshooting (retriever: technical_faq.pdf)
3. Mention DOA policy (retriever: return_policy.pdf)
4. Show empathy and provide clear resolution path

**What It Tests:**
- Multi-step reasoning
- Empathetic customer service
- Balancing troubleshooting vs. replacement
- Appropriate escalation

---

**Query 10: Wrong Item Shipped (Crisis Management)**
```
I ordered a monitor but received a mouse. I need the monitor by Friday.
```

**Required Flow:**
1. Verify order details (tool: check_order_status)
2. Look up wrong item policy (retriever: return_policy.pdf)
3. Check monitor availability (tool: check_product_stock)
4. Calculate express shipping (tool: calculate_shipping)
5. Provide complete resolution with timeline

**What It Tests:**
- Crisis handling
- Multiple tool coordination
- Time-sensitive problem solving
- Customer satisfaction focus
- Compensation awareness

---

**Query 15: Complex Product Search (Advanced Filtering)**
```
Show me all laptops under $1000 that are in stock, and tell me which one is best for video editing
```

**Required Flow:**
1. Filter products (tool: products table query)
2. Check stock for each (tool: check_product_stock)
3. Get detailed specs (retriever: product_catalog.pdf)
4. Evaluate specs for video editing needs
5. Make recommendation with justification

**What It Tests:**
- Complex filtering logic
- Multiple tool calls in loop
- Technical knowledge application
- Recommendation reasoning
- Spec comparison ability

---

## Evaluation Dimensions

### 1. Tool Selection & Execution (40%)
- ✅ Correctly identifies when to use tools
- ✅ Calls appropriate UC functions
- ✅ Extracts correct parameters from user query
- ✅ Handles tool results properly

### 2. Retriever Quality (30%)
- ✅ Retrieves relevant document chunks
- ✅ Searches correct PDFs
- ✅ Synthesizes information from documents
- ✅ Cites sources appropriately

### 3. Hybrid Reasoning (20%)
- ✅ Combines tool results with retrieved knowledge
- ✅ Maintains coherent response across sources
- ✅ Prioritizes information appropriately
- ✅ Handles contradictions or gaps

### 4. User Experience (10%)
- ✅ Provides complete answers
- ✅ Shows empathy when appropriate
- ✅ Gives actionable next steps
- ✅ Communicates clearly and concisely

---

## Scoring Guide

Score each query on a **0-5 scale**:

| Score | Description | Criteria |
|-------|-------------|----------|
| **5** | Excellent | All tools/retriever used correctly, complete answer, excellent UX |
| **4** | Good | Correct approach, minor issues in completeness or clarity |
| **3** | Adequate | Partially correct, missing some information or poor tool use |
| **2** | Poor | Wrong approach or significant gaps in answer |
| **1** | Very Poor | Mostly incorrect, failed to use appropriate capabilities |
| **0** | Failed | No answer, wrong tools, or completely incorrect |

**Target Score:** 4.0+ indicates a well-performing agent

---

## Testing Strategy

### Phase 1: Basic Capabilities (Queries 1, 3, 6, 7, 9, 11)
Validate basic tool calling and retrieval independently.

**Expected Pass Rate:** 90%+

---

### Phase 2: Hybrid Queries (Queries 2, 4, 8, 13, 12, 14)
Test agent's ability to combine tools and retriever.

**Expected Pass Rate:** 75%+

---

### Phase 3: Advanced Multi-Step (Queries 5, 10, 15)
Validate complex reasoning and orchestration.

**Expected Pass Rate:** 60%+

---

## Common Failure Patterns

### 1. Tool Selection Errors
❌ Using retriever when tool is needed (e.g., checking stock via PDF instead of function)
❌ Using tool when retriever is needed (e.g., trying to query return policy via function)

### 2. Incomplete Hybrid Responses
❌ Only answering one part of a multi-part question
❌ Using only tool OR retriever when both are needed

### 3. Missing Context
❌ Not verifying order status before suggesting solutions
❌ Not checking customer tier before discussing shipping benefits

### 4. Poor Orchestration
❌ Calling tools in wrong order
❌ Not passing results from one step to next
❌ Failing to synthesize multiple sources

---

## Usage Instructions

### Loading the Dataset

```python
import json

# Load evaluation dataset
with open('agent_evaluation_dataset.json', 'r') as f:
    eval_queries = json.load(f)

# Run evaluation
for query in eval_queries:
    print(f"\n{'='*60}")
    print(f"Query {query['query_id']}: {query['query']}")
    print(f"Type: {query['query_type']} | Difficulty: {query['difficulty']}")
    
    # Run agent
    response = your_agent.run(query['query'])
    
    # Evaluate
    score = evaluate_response(
        response,
        expected_tools=query['required_tools'],
        expected_retriever=query['required_retriever'],
        evaluation_criteria=query['evaluation_criteria']
    )
    
    print(f"Score: {score}/5")
```

### Evaluation Checklist

For each query, verify:

- [ ] **Correct capability used** (tool vs. retriever vs. both)
- [ ] **All required tools called** with correct parameters
- [ ] **Relevant documents retrieved** if needed
- [ ] **Complete answer** addressing all parts of query
- [ ] **Good user experience** (clear, empathetic, actionable)

---

## Expected Agent Architecture

Your agent should have:

```python
class EcommerceAgent:
    def __init__(self):
        self.tools = {
            'check_order_status': check_order_status_func,
            'check_product_stock': check_product_stock_func,
            'get_product_details': get_product_details_func,
            'calculate_shipping': calculate_shipping_func,
            'get_customer_tier_benefits': get_customer_tier_benefits_func,
            'get_customer_orders': get_customer_orders_func
        }
        self.retriever = VectorStoreRetriever(
            pdfs=['product_catalog', 'return_policy', 'shipping_guide', 'technical_faq']
        )
        self.llm = LanguageModel()
    
    def run(self, query: str):
        # 1. Plan: Decide which capabilities to use
        plan = self.llm.create_plan(query)
        
        # 2. Execute: Call tools and/or retriever
        results = []
        if plan.use_tools:
            for tool_call in plan.tool_calls:
                results.append(self.tools[tool_call.name](**tool_call.params))
        
        if plan.use_retriever:
            docs = self.retriever.search(query)
            results.append(docs)
        
        # 3. Synthesize: Combine results into final answer
        answer = self.llm.synthesize(query, results)
        
        return answer
```

---

## Real-World Scenarios Represented

✅ **Order Tracking** (Q1) - Most common support query  
✅ **Product Search** (Q2, Q8, Q15) - Pre-purchase research  
✅ **Policy Questions** (Q3, Q9, Q12) - Return/shipping policies  
✅ **Shipping Calculations** (Q4) - Cost estimation  
✅ **Technical Support** (Q5, Q11) - Product troubleshooting  
✅ **Account Management** (Q7) - Loyalty/tier benefits  
✅ **Crisis Resolution** (Q10) - Wrong/damaged items  
✅ **Multi-criteria Search** (Q15) - Complex filtering  

---

## Success Metrics

| Metric | Target |
|--------|--------|
| **Overall Average Score** | ≥ 4.0/5.0 |
| **Tool-Only Queries** | ≥ 4.5/5.0 |
| **Retriever-Only Queries** | ≥ 4.2/5.0 |
| **Hybrid Queries** | ≥ 3.8/5.0 |
| **Multi-Step Queries** | ≥ 3.5/5.0 |
| **First-Call Resolution** | ≥ 80% |

---

## Version History

- **v1.0** - Initial agent evaluation dataset with 15 queries
- Created: November 2025
- Purpose: E-Commerce Electronics Store Agent Evaluation

---

**Ready to test your agent! 🚀**

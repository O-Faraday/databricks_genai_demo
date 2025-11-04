# RAG Evaluation Dataset for E-Commerce Electronics Store

## Overview
This evaluation dataset contains **15 carefully crafted queries** designed to comprehensively test a RAG (Retrieval-Augmented Generation) workflow for an e-commerce electronics store. The queries are designed to interact exclusively with the 4 PDF documents in your dataset.

## Dataset Statistics

- **Total Queries:** 15
- **Target Documents:** 4 PDFs
- **Difficulty Levels:** Easy (3), Medium (9), Hard (3)
- **Query Types:** 8 distinct types

## Query Types Distribution

| Query Type | Count | Description |
|------------|-------|-------------|
| Factual Retrieval | 3 | Simple fact-finding from a single source |
| Multi-part Factual | 2 | Questions with multiple factual components |
| Procedural | 2 | Step-by-step process questions |
| Troubleshooting | 2 | Technical problem-solving |
| Policy Specific | 2 | Policy interpretation and edge cases |
| Cross-document Reasoning | 2 | Requires information from multiple PDFs |
| Issue Resolution | 1 | Complex customer service scenarios |
| Multi-scenario Complex | 1 | Multiple scenarios in one query |

## Document Coverage

| PDF Document | Number of Queries |
|--------------|-------------------|
| product_catalog.pdf | 5 queries |
| return_policy.pdf | 4 queries (2 cross-document) |
| shipping_guide.pdf | 5 queries (2 cross-document) |
| technical_faq.pdf | 4 queries |

## Difficulty Breakdown

### Easy (3 queries)
- Simple factual lookups
- Single piece of information
- Direct answers in the source

**Queries:** 1, 4, 8

### Medium (9 queries)
- Multi-part questions
- Requires understanding context
- May need synthesis of information

**Queries:** 2, 3, 5, 6, 7, 9, 11, 12, 13

### Hard (3 queries)
- Cross-document reasoning
- Complex multi-scenario questions
- Requires comprehensive understanding

**Queries:** 10, 14, 15

## Query Details

### Query 1: Monitor Specifications
- **Type:** Factual Retrieval (Easy)
- **PDF:** product_catalog.pdf
- **Tests:** Basic product information retrieval

### Query 2: Return Policy for Software
- **Type:** Multi-part Factual (Medium)
- **PDF:** return_policy.pdf
- **Tests:** Non-returnable items + refund timeline

### Query 3: Laptop Troubleshooting
- **Type:** Procedural (Medium)
- **PDF:** technical_faq.pdf
- **Tests:** Technical problem-solving steps

### Query 4: Express Shipping Details
- **Type:** Factual Retrieval (Easy)
- **PDF:** shipping_guide.pdf
- **Tests:** Shipping options and pricing

### Query 5: Laptop Specifications
- **Type:** Multi-part Factual (Medium)
- **PDF:** product_catalog.pdf
- **Tests:** Technical specs + included accessories

### Query 6: Holiday Return Window
- **Type:** Policy Specific (Medium)
- **PDF:** return_policy.pdf
- **Tests:** Policy variations and exceptions

### Query 7: Monitor Display Issues
- **Type:** Troubleshooting (Medium)
- **PDF:** technical_faq.pdf
- **Tests:** Multiple troubleshooting steps

### Query 8: Free Shipping Threshold
- **Type:** Factual Retrieval (Easy)
- **PDF:** shipping_guide.pdf
- **Tests:** Simple policy fact

### Query 9: Bluetooth Speaker Specs
- **Type:** Multi-part Technical (Medium)
- **PDF:** product_catalog.pdf
- **Tests:** Technical specifications retrieval

### Query 10: Damaged Item Process
- **Type:** Cross-document Reasoning (Hard)
- **PDFs:** return_policy.pdf, shipping_guide.pdf
- **Tests:** Multi-document information synthesis

### Query 11: Dual Monitor Setup
- **Type:** Procedural (Medium)
- **PDF:** technical_faq.pdf
- **Tests:** Installation instructions

### Query 12: Non-returnable Items
- **Type:** Policy Edge Case (Medium)
- **PDF:** return_policy.pdf
- **Tests:** Comprehensive policy understanding

### Query 13: Lost Package Resolution
- **Type:** Issue Resolution (Medium)
- **PDF:** shipping_guide.pdf
- **Tests:** Problem resolution procedures

### Query 14: Smart Watch Features + Warranty
- **Type:** Cross-document Reasoning (Hard)
- **PDFs:** product_catalog.pdf, return_policy.pdf
- **Tests:** Product info + policy synthesis

### Query 15: Address Change + Late Delivery
- **Type:** Multi-scenario Complex (Hard)
- **PDF:** shipping_guide.pdf
- **Tests:** Multiple complex scenarios in one query

## Evaluation Metrics to Consider

### 1. Retrieval Quality
- **Precision:** Are the retrieved chunks relevant?
- **Recall:** Are all necessary chunks retrieved?
- **Ranking:** Are the most relevant chunks ranked highest?

### 2. Generation Quality
- **Accuracy:** Is the information factually correct?
- **Completeness:** Are all parts of the question answered?
- **Clarity:** Is the answer easy to understand?
- **Conciseness:** Is the answer appropriately detailed without being verbose?

### 3. Source Attribution
- **Citation:** Does the system cite which PDF(s) it used?
- **Confidence:** Does it indicate uncertainty when appropriate?

### 4. Edge Case Handling
- **Policy Exceptions:** Correctly identifies special cases (Query 6, 12)
- **Multi-document:** Successfully combines information (Query 10, 14, 15)
- **Ambiguity:** Handles unclear questions appropriately

## Usage Instructions

### Loading the Dataset

```python
import json

# Load the evaluation dataset
with open('rag_evaluation_dataset.json', 'r') as f:
    eval_dataset = json.load(f)

# Iterate through queries
for query_item in eval_dataset:
    query = query_item['query']
    expected_info = query_item['expected_info']
    # Run your RAG system
    response = your_rag_system(query)
    # Evaluate response
    evaluate(response, expected_info, query_item['evaluation_criteria'])
```

### Evaluation Workflow

1. **Run each query** through your RAG system
2. **Capture the response** and retrieved chunks
3. **Compare against expected_info** for accuracy
4. **Check evaluation_criteria** for completeness
5. **Score based on:**
   - Factual accuracy
   - Completeness
   - Clarity
   - Source attribution
   - Handling of edge cases

### Recommended Scoring

For each query, score on a 0-5 scale:
- **0:** Completely incorrect or no answer
- **1:** Partially correct but missing critical information
- **2:** Somewhat correct but incomplete
- **3:** Correct but lacks clarity or completeness
- **4:** Good answer with minor issues
- **5:** Perfect answer - accurate, complete, and well-formatted

## Testing Strategy

### Phase 1: Basic Retrieval (Queries 1, 4, 8)
Start with easy factual queries to validate basic retrieval works.

### Phase 2: Single Document Complexity (Queries 2, 3, 5, 6, 7, 9, 11, 12, 13)
Test more complex queries within single documents.

### Phase 3: Cross-Document Reasoning (Queries 10, 14, 15)
Validate multi-document synthesis capabilities.

## Common Failure Patterns to Watch For

1. **Incomplete Retrieval:** Missing relevant chunks
2. **Over-retrieval:** Including irrelevant information
3. **Hallucination:** Making up information not in PDFs
4. **Context Confusion:** Mixing up information between products/policies
5. **Missing Multi-part Answers:** Only answering one part of multi-part questions
6. **Cross-document Failure:** Unable to synthesize from multiple PDFs

## Expected Output Format

Your RAG system should return:
```python
{
    "answer": "The detailed answer text",
    "sources": ["product_catalog.pdf", "page 3"],
    "confidence": 0.95,
    "retrieved_chunks": [
        {
            "text": "chunk text",
            "source": "product_catalog.pdf",
            "relevance_score": 0.89
        }
    ]
}
```

## Notes

- All queries are designed to be **answerable from the PDFs**
- No query requires external knowledge or the CSV files
- Queries simulate realistic customer support scenarios
- Mix of product, policy, and technical support questions
- Includes both straightforward and challenging edge cases

## License and Usage

This evaluation dataset is designed for testing RAG systems in the Databricks GenAI demo environment. Feel free to modify queries to suit your specific testing needs.

---

**Version:** 1.0  
**Created:** 2025  
**Purpose:** RAG System Evaluation for E-Commerce Electronics Store Demo

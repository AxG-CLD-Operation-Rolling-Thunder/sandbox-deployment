# RAG Integration Setup Guide

## Overview

The Invoice Agent now includes RAG (Retrieval-Augmented Generation) capabilities to enhance invoice processing with domain-specific knowledge. This allows the agent to access and utilize information from a knowledge base for better vendor validation, tax compliance checking, and processing guidance.

## Architecture

### Components Added

1. **RagService** (`services/rag_service.py`) - Core knowledge retrieval service
2. **Knowledge Retrieval Tool** (`tools/knowledge_retrieval_tool.py`) - Search tools and functions
3. **Enhanced Session Service** - RAG context tracking and history
4. **Updated Agent** - Integration with knowledge retrieval tools
5. **Enhanced Prompts** - RAG-aware processing workflows

### Key Features

- **Intelligent Vendor Validation** - Query knowledge base for vendor compliance info
- **Tax Regulation Checking** - Retrieve relevant tax codes and regulations
- **Historical Pattern Analysis** - Access past invoice processing patterns
- **Context-Aware Processing** - Enhanced decision making with domain knowledge
- **Graceful Degradation** - Continues working when knowledge base unavailable

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Knowledge Base Configuration (optional)
VERTEX_SEARCH_ENGINE_ID="your-search-engine-id"
GOOGLE_CLOUD_PROJECT="your-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"
```

### Setting Up Vertex AI Search

1. **Create a Search Engine** in Google Cloud Console:
   - Go to Vertex AI Search & Conversation
   - Create a new Search App
   - Configure data sources (documents, websites, etc.)
   - Note the Search Engine ID

2. **Upload Knowledge Base Content**:
   - Invoice processing guidelines
   - Vendor compliance information
   - Tax regulations and codes
   - Historical processing patterns

## Usage

### Through Agent Tools

The agent automatically has access to knowledge retrieval:

```python
# Available tools:
# 1. search_invoice_knowledge (if search engine configured)
# 2. retrieve_invoice_knowledge (fallback function)
```

### Through Request Handler

Use the service layer directly:

```python
# Query knowledge base
process_request(
    request_type="query_knowledge",
    data={"query": "vendor compliance requirements"}
)

# Retrieve context-specific information
process_request(
    request_type="retrieve_context",
    data={"context_type": "vendor", "entity": "ABC Corp"}
)

# Check RAG service status
process_request(request_type="get_rag_status", data={})
```

### Direct Function Usage

```python
from Invoice_agent.tools.knowledge_retrieval_tool import retrieve_invoice_knowledge

result = retrieve_invoice_knowledge(
    query="tax regulations for international invoices",
    context_type="tax",
    max_results=5
)
```

## Enhanced Processing Workflow

With RAG enabled, the invoice processing workflow becomes:

1. **Invoice Upload** - Standard extraction
2. **Knowledge Enhancement** - Query relevant context:
   - Vendor validation against compliance database
   - Tax code verification against regulations
   - Processing guideline retrieval
3. **Enhanced Output** - Results include:
   - Standard extraction data
   - Compliance warnings/notes
   - Regulatory validation
   - Processing recommendations

## Context Types

The system supports different context types for targeted retrieval:

- **`vendor`** - Vendor compliance, validation, risk information
- **`tax`** - Tax codes, regulations, compliance rules
- **`general`** - General invoice processing guidelines
- **`historical`** - Historical patterns and trends

## Fallback Behavior

When RAG is not configured:
- Agent continues standard invoice processing
- Knowledge retrieval functions return configuration errors
- No impact on core functionality
- Graceful degradation with informative messages

## Development Notes

### Mock Implementation

The current implementation includes mock responses for development/testing. In production:

1. Replace mock results with actual Vertex AI Search integration
2. Configure proper search engine with relevant documents
3. Set up authentication and permissions

### Extending Functionality

To add new knowledge types:

1. Update context types in `retrieve_context()`
2. Add query enhancement patterns
3. Update agent instructions with new capabilities

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies installed with `pip install -r requirements.txt`
2. **Configuration Missing**: Set `VERTEX_SEARCH_ENGINE_ID` and `GOOGLE_CLOUD_PROJECT`
3. **Search Engine Issues**: Verify search engine exists and is accessible
4. **Authentication**: Ensure proper Google Cloud credentials configured

### Logging

Knowledge retrieval activities are logged at INFO level:
```python
INFO:Invoice_agent.tools.knowledge_retrieval_tool:Knowledge search requested: vendor compliance
```

## Production Deployment

For production use:

1. Set up Vertex AI Search with proper data sources
2. Configure environment variables in deployment
3. Set up monitoring for knowledge retrieval performance
4. Consider caching frequently accessed knowledge

This RAG integration provides a foundation for intelligent, context-aware invoice processing while maintaining compatibility with existing workflows.
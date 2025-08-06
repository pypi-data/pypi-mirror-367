# Rowland Python SDK

Python SDK for the Rowland Documents API.

## Installation

```bash
pip install rowland
```

## Quick Start

```python
from rowland import DocumentsApiClient

# Initialize client
client = DocumentsApiClient(api_key="your-api-key")

# Upload a document
with open("contract.pdf", "rb") as f:
    document = client.upload_document(f, "contract.pdf")
    print(f"Uploaded: {document.id}")

# Get documents
documents = client.get_documents(limit=10)
print(f"Found {documents.total} documents")

# Get specific document
doc = client.get_document(document.id)
print(f"Status: {doc.status}")

# Get extractions when ready
if doc.status == "success":
    extractions = client.get_document_extractions(doc.id)
    print(f"Found {extractions.total_objects_found} objects")

# Close client
client.close()
```

## Context Manager (Recommended)

```python
with DocumentsApiClient(api_key="your-api-key") as client:
    # Upload document
    with open("document.pdf", "rb") as f:
        doc = client.upload_document(f, "document.pdf")
    
    # Client automatically closes
```

## Methods

- `upload_document()` - Upload a document for processing
- `get_documents()` - Get paginated list of documents
- `get_document()` - Get specific document by ID
- `delete_document()` - Delete a document
- `get_document_extractions()` - Get extracted data
- `get_health()` - Check API health

## Document Types Supported

Supports 40+ document types including leases, deeds, assignments, JOAs, division orders, and more.

## Requirements

- Python 3.8+
- API key from Rowland

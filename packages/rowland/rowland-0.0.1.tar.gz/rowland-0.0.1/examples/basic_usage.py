"""Basic usage example for the Rowland Documents SDK."""

import os

from rowland import DocumentsApiClient


def main() -> None:
    api_key = os.getenv("ROWLAND_API_KEY", "your-api-key-here")

    with DocumentsApiClient(api_key=api_key) as client:
        # Check health
        health = client.get_health()
        print(f"API Health: {health}")

        # Get documents
        documents = client.get_documents(limit=5)
        print(f"Found {documents.total} documents")

        for doc in documents.items:
            print(f"- {doc.name} ({doc.status})")


if __name__ == "__main__":
    main()

"""Documents API client."""

import mimetypes
from pathlib import Path
from tracemalloc import Traceback
from typing import Any, BinaryIO

import httpx

from .exceptions import RowlandAuthenticationError, RowlandHTTPError
from .models import Document, DocumentExtractionResponse, PaginatedResponse


class DocumentsApiClient:
    """Documents API client matching the C# SDK."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://documents.rowland.ai",
        timeout: float = 30.0,
    ):
        """Initialize the client.

        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

        self._client = httpx.Client(
            base_url=self._base_url,
            headers={"x-api-key": api_key},
            timeout=timeout,
        )

    def __enter__(self: "DocumentsApiClient") -> "DocumentsApiClient":
        return self

    def __exit__(
        self: "DocumentsApiClient",
        exc_type: type | None,
        exc_val: Exception | None,
        exc_tb: Traceback | None,
    ) -> None:
        self.close()

    def close(self: "DocumentsApiClient") -> None:
        """Close the client."""
        self._client.close()

    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename."""
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            return mime_type

        extension = Path(filename).suffix.lower()
        return {
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".doc": "application/msword",
            ".docx": (
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"
            ),
        }.get(extension, "application/octet-stream")

    def _handle_response(self: "DocumentsApiClient", response: httpx.Response) -> None:
        """Handle HTTP response errors."""
        if response.status_code == 401:
            raise RowlandAuthenticationError(response_text=response.text)
        if not response.is_success:
            raise RowlandHTTPError(
                f"Request failed with status {response.status_code}",
                status_code=response.status_code,
                response_text=response.text,
            )

    def upload_document(
        self,
        file: BinaryIO | bytes,
        filename: str,
        user_id: str | None = None,
        organization_id: str | None = None,
        folder_id: str | None = None,
        webhook_url: str | None = None,
        webhook_secret: str | None = None,
    ) -> Document:
        """Upload a document."""
        files = {"file": (filename, file, self._get_mime_type(filename))}

        data = {}
        if user_id:
            data["user_id"] = user_id
        if organization_id:
            data["organization_id"] = organization_id
        if folder_id:
            data["folder_id"] = folder_id
        if webhook_url:
            data["webhook_url"] = webhook_url
        if webhook_secret:
            data["webhook_secret"] = webhook_secret

        response = self._client.post("/v0/documents", files=files, data=data)
        self._handle_response(response)
        return Document(**response.json())

    def get_documents(
        self,
        offset: int = 0,
        limit: int = 50,
    ) -> PaginatedResponse[Document]:
        """Get a paginated list of documents."""
        response = self._client.get(
            "/v0/documents", params={"offset": offset, "limit": limit}
        )
        self._handle_response(response)

        data = response.json()
        documents = [Document(**item) for item in data["items"]]
        data["items"] = documents
        return PaginatedResponse[Document](**data)

    def get_document(self, document_id: str) -> Document:
        """Get a specific document by ID."""
        response = self._client.get(f"/v0/documents/{document_id}")
        self._handle_response(response)
        return Document(**response.json())

    def delete_document(self, document_id: str) -> Any:
        """Delete a document."""
        response = self._client.delete(f"/v0/documents/{document_id}")
        self._handle_response(response)
        return response.json()

    def get_document_extractions(self, document_id: str) -> DocumentExtractionResponse:
        """Get document extractions."""
        response = self._client.get(f"/v0/documents/{document_id}/extractions")
        self._handle_response(response)
        return DocumentExtractionResponse(**response.json())

    def get_health(self) -> Any:
        """Get API health status."""
        response = self._client.get("/health")
        self._handle_response(response)
        return response.json()

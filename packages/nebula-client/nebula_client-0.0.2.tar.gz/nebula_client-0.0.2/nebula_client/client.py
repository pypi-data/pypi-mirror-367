"""
Main client for the Nebula Client SDK

This client provides a clean, intuitive interface to Nebula's memory and retrieval capabilities.
"""

import os
import json
import hashlib
import uuid
from typing import Any, Dict, List, Optional, Union
import httpx
from urllib.parse import urljoin

from .exceptions import (
    NebulaException,
    NebulaClientException,
    NebulaAuthenticationException,
    NebulaRateLimitException,
    NebulaValidationException,
)
from .models import (
    Memory,
    Cluster,
    SearchResult,
    AgentResponse,
    RetrievalType,
)


class NebulaClient:
    """
    Simple client for interacting with Nebula Cloud API
    
    This client provides a clean interface to Nebula's memory and retrieval capabilities,
    focusing on the core functionality without the complexity of the underlying R2R system.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.nebulacloud.app",
        timeout: float = 30.0,
    ):
        """
        Initialize the Nebula client
        
        Args:
            api_key: Your Nebula API key. If not provided, will look for NEBULA_API_KEY env var
            base_url: Base URL for the Nebula API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("NEBULA_API_KEY")
        if not self.api_key:
            raise NebulaClientException(
                "API key is required. Pass it to the constructor or set NEBULA_API_KEY environment variable."
            )
        
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the HTTP client"""
        self._client.close()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Nebula API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/v3/documents")
            json_data: JSON data to send in request body
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            NebulaException: For API errors
            NebulaClientException: For client errors
        """
        url = urljoin(self.base_url, endpoint)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            response = self._client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params,
            )
            
            # Handle different response status codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise NebulaAuthenticationException("Invalid API key")
            elif response.status_code == 429:
                raise NebulaRateLimitException("Rate limit exceeded")
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                raise NebulaValidationException(
                    error_data.get("message", "Validation error"),
                    error_data.get("details")
                )
            else:
                error_data = response.json() if response.content else {}
                raise NebulaException(
                    error_data.get("message", f"API error: {response.status_code}"),
                    response.status_code,
                    error_data
                )
                
        except httpx.ConnectError as e:
            raise NebulaClientException(
                f"Failed to connect to {self.base_url}. Check your internet connection.",
                e
            )
        except httpx.TimeoutException as e:
            raise NebulaClientException(
                f"Request timed out after {self.timeout} seconds",
                e
            )
        except httpx.RequestError as e:
            raise NebulaClientException(f"Request failed: {str(e)}", e)
    
    # Collection Management Methods
    
    def create_collection(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Cluster:
        """
        Create a new collection
        """
        data = {
            "name": name,
        }
        if description:
            data["description"] = description
        if metadata:
            data["metadata"] = metadata
        
        response = self._make_request("POST", "/v3/collections", json_data=data)
        # Unwrap 'results' if present
        if isinstance(response, dict) and "results" in response:
            response = response["results"]
        return Cluster.from_dict(response)
    
    def get_collection(self, collection_id: str) -> Cluster:
        """
        Get a specific collection by ID
        
        Args:
            collection_id: ID of the collection to retrieve
            
        Returns:
            Cluster object
        """
        response = self._make_request("GET", f"/v3/collections/{collection_id}")
        return Cluster.from_dict(response)
    
    def list_collections(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Cluster]:
        """
        Get all collections
        
        Args:
            limit: Maximum number of collections to return
            offset: Number of collections to skip
            
        Returns:
            List of Cluster objects
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        response = self._make_request("GET", "/v3/collections", params=params)
        
        if isinstance(response, dict) and "results" in response:
            collections = response["results"]
        elif isinstance(response, list):
            collections = response
        else:
            collections = [response]
        
        return [Cluster.from_dict(collection) for collection in collections]
    
    def update_collection(
        self,
        collection_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Cluster:
        """
        Update a collection
        
        Args:
            collection_id: ID of the collection to update
            name: New name for the collection
            description: New description for the collection
            metadata: New metadata for the collection
            
        Returns:
            Updated Cluster object
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if metadata is not None:
            data["metadata"] = metadata
        
        response = self._make_request("PATCH", f"/v3/collections/{collection_id}", json_data=data)
        return Cluster.from_dict(response)
    
    def delete_collection(self, collection_id: str) -> bool:
        """
        Delete a collection
        
        Args:
            collection_id: ID of the collection to delete
            
        Returns:
            True if deletion was successful
        """
        self._make_request("DELETE", f"/v3/collections/{collection_id}")
        return True
    
    def get_collection_memories(
        self,
        collection_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Memory]:
        """
        Get all memories in a collection by filtering documents
        
        Args:
            collection_id: ID of the collection
            limit: Maximum number of memories to return
            offset: Number of memories to skip
            
        Returns:
            List of Memory objects
        """
        params = {
            "limit": limit,
            "offset": offset,
            "collection_ids": collection_id,
        }
        
        response = self._make_request("GET", "/v3/documents", params=params)
        
        if isinstance(response, dict) and "results" in response:
            documents = response["results"]
        elif isinstance(response, list):
            documents = response
        else:
            documents = [response]
        
        # Convert documents to memories
        memories = []
        for doc in documents:
            # Create a memory from the document
            memory_data = {
                "id": doc.get("id"),
                "agent_id": doc.get("metadata", {}).get("agent_id", "unknown"),
                "content": doc.get("summary", "No content available"),
                "metadata": doc.get("metadata", {}),
                "collection_ids": doc.get("collection_ids", [])
            }
            memories.append(Memory.from_dict(memory_data))
        
        return memories

    # Memory Management Methods
    
    def store(
        self,
        agent_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        speaker: Optional[str] = None,
    ) -> Memory:
        """
        Store a memory for an agent (creates a document with chunks)
        
        Args:
            agent_id: Unique identifier for the agent
            content: The memory content to store
            metadata: Additional metadata for the memory
            collection_id: Optional collection ID to store the memory in
            conversation_id: Optional conversation ID for conversational context
            timestamp: Optional timestamp for the memory
            speaker: Optional speaker identifier
            
        Returns:
            Memory object
        """
        # Prepare metadata
        doc_metadata = metadata or {}
        doc_metadata["agent_id"] = agent_id
        doc_metadata["memory_type"] = "chat_memory"
        
        if conversation_id:
            doc_metadata["conversation_id"] = conversation_id
        if timestamp:
            doc_metadata["timestamp"] = timestamp
        if speaker:
            doc_metadata["speaker"] = speaker
        
        # Generate deterministic document ID for deduplication
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        deterministic_doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, content_hash))
        
        # Use form data for document creation (like the original R2R SDK)
        data = {
            "raw_text": content,
            "metadata": json.dumps({**doc_metadata, "content_hash": content_hash}),
            "ingestion_mode": "fast",
        }
        
        if collection_id:
            data["collection_ids"] = json.dumps([collection_id])
        
        # Create document using the documents endpoint with form data
        url = f"{self.base_url}/v3/documents"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = self._client.post(url, data=data, headers=headers)
            
            if response.status_code not in (200, 202):
                error_data = response.json() if response.content else {}
                raise NebulaException(
                    error_data.get("message", f"Failed to create document: {response.status_code}"),
                    response.status_code,
                    error_data
                )
            
            response_data = response.json()
            
            # Extract document ID from response
            if isinstance(response_data, dict) and "results" in response_data:
                if hasattr(response_data["results"], 'document_id'):
                    doc_id = response_data["results"]["document_id"]
                else:
                    doc_id = deterministic_doc_id
            else:
                doc_id = deterministic_doc_id
            
        except Exception as e:
            # If duplicate (HTTP 409 or similar) just skip
            err_msg = str(e).lower()
            if any(token in err_msg for token in ["conflict", "already exists", "duplicate"]):
                # Return a memory object for the existing document
                memory_data = {
                    "id": deterministic_doc_id,
                    "agent_id": agent_id,
                    "content": content,
                    "metadata": doc_metadata,
                    "collection_ids": [collection_id] if collection_id else []
                }
                return Memory.from_dict(memory_data)
            # For other errors, re-raise
            raise
        
        # Return a memory object
        memory_data = {
            "id": doc_id,
            "agent_id": agent_id,
            "content": content,
            "metadata": doc_metadata,
            "collection_ids": [collection_id] if collection_id else []
        }
        return Memory.from_dict(memory_data)
    
    def store_conversation(
        self,
        agent_id: str,
        conversation: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        collection_id: Optional[str] = None,
        batch_size: int = 100,
    ) -> List[Memory]:
        """
        Store a conversation as multiple memories
        
        Args:
            agent_id: Unique identifier for the agent
            conversation: List of conversation messages
            metadata: Additional metadata for the memories
            collection_id: Optional collection ID to store memories in
            batch_size: Number of messages per document batch
            
        Returns:
            List of Memory objects
        """
        memories = []
        
        # Process conversation in batches
        total_batches = (len(conversation) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(conversation))
            message_batch = conversation[start_idx:end_idx]
            
            # Create text chunks for this batch
            chunks_text = []
            for msg in message_batch:
                timestamp = msg.get("timestamp", "")
                speaker = msg.get("speaker", "")
                text = msg.get("text", "")
                chunk_text = f"[{timestamp}] {speaker}: {text}"
                chunks_text.append(chunk_text)
            
            # Create metadata for this document batch
            batch_metadata = metadata or {}
            batch_metadata.update({
                "conversation_batch": batch_idx,
                "total_batches": total_batches,
                "title": f"Conversation_Batch_{batch_idx}",
                "document_type": "conversation_chunks",
                "total_messages": len(chunks_text),
                "message_range": f"{start_idx}-{end_idx-1}"
            })
            
            # Generate deterministic document ID for deduplication
            content_hash = hashlib.sha256("\n".join(chunks_text).encode("utf-8")).hexdigest()
            deterministic_doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, content_hash))
            
            # Use form data for document creation (like the original R2R SDK)
            data = {
                "chunks": json.dumps(chunks_text),
                "metadata": json.dumps({**batch_metadata, "content_hash": content_hash}),
                "ingestion_mode": "fast",
            }
            
            if collection_id:
                data["collection_ids"] = json.dumps([collection_id])
            
            # Create document using the documents endpoint with form data
            url = f"{self.base_url}/v3/documents"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            try:
                response = self._client.post(url, data=data, headers=headers)
                
                if response.status_code not in (200, 202):
                    error_data = response.json() if response.content else {}
                    raise NebulaException(
                        error_data.get("message", f"Failed to create document: {response.status_code}"),
                        response.status_code,
                        error_data
                    )
                
                response_data = response.json()
                
                # Extract document ID from response
                if isinstance(response_data, dict) and "results" in response_data:
                    if hasattr(response_data["results"], 'document_id'):
                        doc_id = response_data["results"]["document_id"]
                    else:
                        doc_id = deterministic_doc_id
                else:
                    doc_id = deterministic_doc_id
                
                # Create memory object
                memory_data = {
                    "id": doc_id,
                    "agent_id": agent_id,
                    "content": "\n".join(chunks_text),
                    "metadata": batch_metadata,
                    "collection_ids": [collection_id] if collection_id else []
                }
                memories.append(Memory.from_dict(memory_data))
                
            except Exception as e:
                # If duplicate (HTTP 409 or similar) just skip
                err_msg = str(e).lower()
                if any(token in err_msg for token in ["conflict", "already exists", "duplicate"]):
                    continue
                # For other errors, re-raise
                raise
        
        return memories

    def retrieve(
        self,
        agent_id: str,
        query: str,
        limit: int = 10,
        retrieval_type: Union[RetrievalType, str] = RetrievalType.SIMPLE,
        filters: Optional[Dict[str, Any]] = None,
        collection_id: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Retrieve relevant memories for an agent
        """
        # Convert string to enum if needed
        if isinstance(retrieval_type, str):
            retrieval_type = RetrievalType(retrieval_type)
        
        data = {
            "query": query,
            "limit": limit,
        }
        
        # Add search settings (but skip collection filters for now due to API issue)
        search_settings = {}
        if filters:
            # Filter out collection_ids from filters to avoid the API error
            filtered_filters = {k: v for k, v in filters.items() if k != "collection_ids"}
            if filtered_filters:
                search_settings["filters"] = filtered_filters
        
        if search_settings:
            data["search_settings"] = search_settings
        
        response = self._make_request("POST", "/v3/retrieval/search", json_data=data)
        
        # Extract chunk search results from the response
        if isinstance(response, dict) and "results" in response:
            chunk_results = response["results"].get("chunk_search_results", [])
        else:
            chunk_results = []
        
        return [SearchResult.from_dict(result) for result in chunk_results]
    
    def delete(self, memory_id: str) -> bool:
        """
        Delete a specific memory (document)
        """
        self._make_request("DELETE", f"/v3/documents/{memory_id}")
        return True
    
    def get(self, memory_id: str) -> Memory:
        """
        Get a specific memory by ID (via documents endpoint)
        """
        response = self._make_request("GET", f"/v3/documents/{memory_id}")
        
        # Convert document to memory
        memory_data = {
            "id": response.get("id"),
            "agent_id": response.get("metadata", {}).get("agent_id", "unknown"),
            "content": response.get("summary", "No content available"),
            "metadata": response.get("metadata", {}),
            "collection_ids": response.get("collection_ids", [])
        }
        return Memory.from_dict(memory_data)
    
    def list_agent_memories(
        self,
        agent_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Memory]:
        """
        Get all memories for a specific agent
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        response = self._make_request("GET", "/v3/documents", params=params)
        
        if isinstance(response, dict) and "results" in response:
            documents = response["results"]
        elif isinstance(response, list):
            documents = response
        else:
            documents = [response]
        
        # Filter documents by agent_id
        agent_memories = []
        for doc in documents:
            if doc.get("metadata", {}).get("agent_id") == agent_id:
                memory_data = {
                    "id": doc.get("id"),
                    "agent_id": agent_id,
                    "content": doc.get("summary", "No content available"),
                    "metadata": doc.get("metadata", {}),
                    "collection_ids": doc.get("collection_ids", [])
                }
                agent_memories.append(Memory.from_dict(memory_data))
        
        return agent_memories
    
    def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search across all memories in the system
        """
        data = {
            "query": query,
            "limit": limit,
        }
        
        if filters:
            # Filter out collection_ids from filters to avoid the API error
            filtered_filters = {k: v for k, v in filters.items() if k != "collection_ids"}
            if filtered_filters:
                data["search_settings"] = {"filters": filtered_filters}
        
        response = self._make_request("POST", "/v3/retrieval/search", json_data=data)
        
        # Extract chunk search results from the response
        if isinstance(response, dict) and "results" in response:
            chunk_results = response["results"].get("chunk_search_results", [])
        else:
            chunk_results = []
        
        return [SearchResult.from_dict(result) for result in chunk_results]
    
    def chat(
        self,
        agent_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        retrieval_type: Union[RetrievalType, str] = RetrievalType.SIMPLE,
        collection_id: Optional[str] = None,
    ) -> AgentResponse:
        """
        Chat with an agent using its memories for context
        
        Args:
            agent_id: Unique identifier for the agent
            message: User message to send to the agent
            conversation_id: Optional conversation ID for multi-turn conversations
            model: LLM model to use for generation
            temperature: Sampling temperature for generation
            max_tokens: Maximum tokens to generate
            retrieval_type: Type of retrieval to use for context
            collection_id: Optional collection ID to search within
            
        Returns:
            AgentResponse object with the agent's response
        """
        # Convert string to enum if needed
        if isinstance(retrieval_type, str):
            retrieval_type = RetrievalType(retrieval_type)
        
        data = {
            "query": message,
            "rag_generation_config": {
                "model": model,
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            data["rag_generation_config"]["max_tokens"] = max_tokens
        
        if conversation_id:
            data["conversation_id"] = conversation_id
        
        # Note: Skipping collection_id filter for now due to API issue
        
        response = self._make_request("POST", "/v3/retrieval/rag", json_data=data)
        
        # Extract the response from the API format
        if isinstance(response, dict) and "results" in response:
            # The RAG endpoint returns the answer in "generated_answer" field
            generated_answer = response["results"].get("generated_answer", "")
            if generated_answer:
                return AgentResponse(
                    content=generated_answer,
                    agent_id=agent_id,
                    conversation_id=conversation_id,
                    metadata={},
                    citations=[]
                )
            
            # Fallback to completion format if generated_answer is not available
            completion = response["results"].get("completion", {})
            if completion and "choices" in completion:
                content = completion["choices"][0].get("message", {}).get("content", "")
                return AgentResponse(
                    content=content,
                    agent_id=agent_id,
                    conversation_id=conversation_id,
                    metadata={},
                    citations=[]
                )
        
        # Fallback
        return AgentResponse(
            content="No response received",
            agent_id=agent_id,
            conversation_id=conversation_id,
            metadata={},
            citations=[]
        )
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the Nebula API
        
        Returns:
            Health status information
        """
        return self._make_request("GET", "/health")
    
    # Backward compatibility aliases for document terminology
    store_memory = store
    retrieve_memories = retrieve
    delete_memory = delete
    get_memory = get
    list_agent_memories = list_agent_memories
    search_memories = search
    chat_with_memories = chat
    
    # Backward compatibility aliases for cluster terminology
    create_cluster = create_collection
    get_cluster = get_collection
    list_clusters = list_collections
    update_cluster = update_collection
    delete_cluster = delete_collection
    get_cluster_memories = get_collection_memories 
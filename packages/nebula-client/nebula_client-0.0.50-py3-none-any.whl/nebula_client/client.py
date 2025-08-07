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
    NebulaClusterNotFoundException,
)
from .models import (
    Memory,
    Cluster,
    SearchResult,
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
    
    def _validate_cluster_exists(self, cluster_id: str) -> None:
        """
        Validate that a cluster exists by checking the collections list
        
        Args:
            cluster_id: ID of the cluster to validate
            
        Raises:
            NebulaClusterNotFoundException: If the cluster doesn't exist
        """
        # Use the collections list endpoint with ID filter
        params = {
            "ids": cluster_id,
            "limit": 1,  # We only need to check if it exists
            "offset": 0
        }
        
        try:
            response = self._make_request("GET", "/v3/collections", params=params)
            
            # Check if the cluster exists in the results
            collections = response.get("results", [])
            if not collections:
                raise NebulaClusterNotFoundException(cluster_id)
                
        except NebulaClusterNotFoundException:
            # Re-raise the specific exception
            raise
        except Exception as e:
            # For other errors, raise a generic exception
            raise NebulaClientException(f"Failed to validate cluster: {str(e)}", e)
    
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
    

    
    # def _make_streaming_generator(
    #     self,
    #     method: str,
    #     endpoint: str,
    #     json_data: Optional[Dict[str, Any]] = None,
    #     params: Optional[Dict[str, Any]] = None,
    #     agent_id: Optional[str] = None,
    #     conversation_id: Optional[str] = None,
    # ):
    #     """
    #     Make a streaming HTTP request to the Nebula API and yield content as it arrives
    #     
    #     Args:
    #         method: HTTP method (GET, POST, etc.)
    #         endpoint: API endpoint (e.g., "/v3/retrieval/rag")
    #         json_data: JSON data to send in request body
    #         params: Query parameters
    #         agent_id: Agent ID for the response
    #         conversation_id: Conversation ID for the response
    #         
    #     Yields:
    #         Content chunks as they arrive from the streaming response
    #     """
    #     url = urljoin(self.base_url, endpoint)
    #     headers = {
    #         "Authorization": f"Bearer {self.api_key}",
    #         "Content-Type": "application/json",
    #         "Accept": "text/event-stream",
    #     }
    #     
    #     try:
    #         response = self._client.request(
    #             method=method,
    #             url=url,
    #             headers=headers,
    #             json=json_data,
    #             params=params,
    #         )
    #         
    #         if response.status_code != 200:
    #             error_data = response.json() if response.content else {}
    #             raise NebulaException(
    #                 error_data.get("message", f"Streaming API error: {response.status_code}"),
    #                 response.status_code,
    #                 error_data
    #             )
    #         
    #         # Process streaming response and yield content as it arrives
    #         for line in response.iter_lines():
    #             if line:
    #                 # Handle both bytes and string responses
    #                 if isinstance(line, bytes):
    #                     line_str = line.decode('utf-8')
    #                 else:
    #                     line_str = str(line)
    #                 
    #                 if line_str.startswith('data: '):
    #                     data_str = line_str[6:]  # Remove 'data: ' prefix
    #                     if data_str.strip() == '[DONE]':
    #                         break
    #                     try:
    #                         data = json.loads(data_str)
    #                         # Handle different streaming formats
    #                         if 'choices' in data and len(data['choices']) > 0:
    #                             delta = data['choices'][0].get('delta', {})
    #                             if 'content' in delta:
    #                                 yield delta['content']
    #                         elif 'delta' in data and 'content' in data['delta']:
    #                             # R2R streaming format
    #                             content_list = data['delta']['content']
    #                             if content_list and len(content_list) > 0:
    #                                 content_item = content_list[0]
    #                                 if 'payload' in content_item and 'value' in content_item['payload']:
    #                                     yield content_item['payload']['value']
    #                         elif 'message' in data:
    #                             # Alternative format for R2R streaming
    #                             yield data['message']
    #                         elif isinstance(data, str):
    #                             # Direct string content
    #                             yield data
    #                     except json.JSONDecodeError:
    #                         # If it's not JSON, treat as direct content
    #                         if data_str.strip() and data_str.strip() != '[DONE]':
    #                             yield data_str
    #                         continue
    #         
    #     except httpx.ConnectError as e:
    #         raise NebulaClientException(
    #             f"Failed to connect to {self.base_url}. Check your internet connection.",
    #             e
    #         )
    #     except httpx.TimeoutException as e:
    #         raise NebulaClientException(
    #             f"Request timed out after {self.timeout} seconds",
    #             e
    #         )
    #     except httpx.RequestError as e:
    #         raise NebulaClientException(f"Request failed: {str(e)}", e)
    
    # Cluster Management Methods
    
    def create_cluster(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Cluster:
        """
        Create a new cluster
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
    
    def get_cluster(self, cluster_id: str) -> Cluster:
        """
        Get a specific cluster by ID
        
        Args:
            cluster_id: ID of the cluster to retrieve
            
        Returns:
            Cluster object
        """
        response = self._make_request("GET", f"/v3/collections/{cluster_id}")
        # Unwrap 'results' if present
        if isinstance(response, dict) and "results" in response:
            response = response["results"]
        return Cluster.from_dict(response)
    
    def list_clusters(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Cluster]:
        """
        Get all clusters
        
        Args:
            limit: Maximum number of clusters to return
            offset: Number of clusters to skip
            
        Returns:
            List of Cluster objects
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        response = self._make_request("GET", "/v3/collections", params=params)
        
        if isinstance(response, dict) and "results" in response:
            clusters = response["results"]
        elif isinstance(response, list):
            clusters = response
        else:
            clusters = [response]
        
        return [Cluster.from_dict(cluster) for cluster in clusters]
    
    def update_cluster(
        self,
        cluster_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Cluster:
        """
        Update a cluster
        
        Args:
            cluster_id: ID of the cluster to update
            name: New name for the cluster
            description: New description for the cluster
            metadata: New metadata for the cluster
            
        Returns:
            Updated Cluster object
        """
        # Validate that the cluster exists
        self._validate_cluster_exists(cluster_id)
        
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if metadata is not None:
            data["metadata"] = metadata
        
        response = self._make_request("POST", f"/v3/collections/{cluster_id}", json_data=data)
        # Unwrap 'results' if present
        if isinstance(response, dict) and "results" in response:
            response = response["results"]
        return Cluster.from_dict(response)
    
    def delete_cluster(self, cluster_id: str) -> bool:
        """
        Delete a cluster
        
        Args:
            cluster_id: ID of the cluster to delete
            
        Returns:
            True if successful
        """
        # Validate that the cluster exists
        self._validate_cluster_exists(cluster_id)
        
        self._make_request("DELETE", f"/v3/collections/{cluster_id}")
        return True

    # Memory Management Methods
    
    def store(
        self,
        content: str,
        cluster_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        """
        Store a memory (creates a document with chunks)
        
        Args:
            content: The memory content to store
            cluster_id: Cluster ID to store the memory in (required)
            metadata: Additional metadata for the memory
            
        Returns:
            Memory object
        """
        # Validate that the cluster exists
        self._validate_cluster_exists(cluster_id)
        
        # Prepare metadata
        doc_metadata = metadata or {}
        doc_metadata["memory_type"] = "memory"
        
        # Generate deterministic document ID for deduplication
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        deterministic_doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, content_hash))
        
        # Use form data for document creation (like the original R2R SDK)
        data = {
            "raw_text": content,
            "metadata": json.dumps({**doc_metadata, "content_hash": content_hash}),
            "ingestion_mode": "fast",
            "collection_ids": json.dumps([cluster_id])
        }
        
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
                # Try to get the actual document ID from the response
                if "document_id" in response_data["results"]:
                    doc_id = response_data["results"]["document_id"]
                elif "id" in response_data["results"]:
                    doc_id = response_data["results"]["id"]
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
                    "content": content,
                    "metadata": doc_metadata,
                    "collection_ids": [cluster_id]
                }
                return Memory.from_dict(memory_data)
            # For other errors, re-raise
            raise
        
        # Return a memory object
        memory_data = {
            "id": doc_id,
            "content": content,
            "metadata": doc_metadata,
            "collection_ids": [cluster_id]
        }
        return Memory.from_dict(memory_data)
    
    # def store_conversation(
    #     self,
    #     agent_id: str,
    #     conversation: List[Dict[str, Any]],
    #     metadata: Optional[Dict[str, Any]] = None,
    #     cluster_id: Optional[str] = None,
    #     batch_size: int = 100,
    # ) -> List[Memory]:
    #     """
    #     Store a conversation as multiple memories
    #     
    #     Args:
    #         agent_id: Unique identifier for the agent
    #         conversation: List of conversation messages
    #         metadata: Additional metadata for the memories
    #         cluster_id: Optional cluster ID to store memories in
    #         batch_size: Number of messages per document batch
    #         
    #     Returns:
    #         List of Memory objects
    #     """
    #     memories = []
    #     
    #     # Process conversation in batches
    #     total_batches = (len(conversation) + batch_size - 1) // batch_size
    #     
    #     for batch_idx in range(total_batches):
    #         start_idx = batch_idx * batch_size
    #         end_idx = min(start_idx + batch_size, len(conversation))
    #         message_batch = conversation[start_idx:end_idx]
    #         
    #         # Create text chunks for this batch
    #         chunks_text = []
    #         for msg in message_batch:
    #             timestamp = msg.get("timestamp", "")
    #             speaker = msg.get("speaker", "")
    #             text = msg.get("text", "")
    #             chunk_text = f"[{timestamp}] {speaker}: {text}"
    #             chunks_text.append(chunk_text)
    #         
    #         # Create metadata for this document batch
    #         batch_metadata = metadata or {}
    #         batch_metadata.update({
    #             "conversation_batch": batch_idx,
    #             "total_batches": total_batches,
    #             "title": f"Conversation_Batch_{batch_idx}",
    #             "document_type": "conversation_chunks",
    #             "total_messages": len(chunks_text),
    #             "message_range": f"{start_idx}-{end_idx-1}"
    #         })
    #         
    #         # Generate deterministic document ID for deduplication
    #         content_hash = hashlib.sha256("\n".join(chunks_text).encode("utf-8")).hexdigest()
    #         deterministic_doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, content_hash))
    #         
    #         # Use form data for document creation (like the original R2R SDK)
    #         data = {
    #             "chunks": json.dumps(chunks_text),
    #             "metadata": json.dumps({**batch_metadata, "content_hash": content_hash}),
    #             "ingestion_mode": "fast",
    #         }
    #         
    #         if cluster_id:
    #             data["collection_ids"] = json.dumps([cluster_id])
    #         
    #         # Create document using the documents endpoint with form data
    #         url = f"{self.base_url}/v3/documents"
    #         headers = {"Authorization": f"Bearer {self.api_key}"}
    #         
    #         try:
    #             response = self._client.post(url, data=data, headers=headers)
    #             
    #             if response.status_code not in (200, 202):
    #                 error_data = response.json() if response.content else {}
    #                 raise NebulaException(
    #                     error_data.get("message", f"Failed to create document: {response.status_code}"),
    #                     response.status_code,
    #                     error_data
    #                 )
    #             
    #             response_data = response.json()
    #             
    #             # Extract document ID from response
    #             if isinstance(response_data, dict) and "results" in response_data:
    #                 if hasattr(response_data["results"], 'document_id'):
    #                     doc_id = response_data["results"]["document_id"]
    #                 else:
    #                     doc_id = deterministic_doc_id
    #             else:
    #                 doc_id = deterministic_doc_id
    #             
    #             # Create memory object
    #             memory_data = {
    #                 "id": doc_id,
    #                 "agent_id": agent_id,
    #                 "content": "\n".join(chunks_text),
    #                 "metadata": batch_metadata,
    #                 "collection_ids": [cluster_id] if cluster_id else []
    #             }
    #             memories.append(Memory.from_dict(memory_data))
    #             
    #         except Exception as e:
    #             # If duplicate (HTTP 409 or similar) just skip
    #             err_msg = str(e).lower()
    #             if any(token in err_msg for token in ["conflict", "already exists", "duplicate"]):
    #                 continue
    #             # For other errors, re-raise
    #             raise
    #     
    #     return memories


    
    def delete(self, memory_id: str) -> bool:
        """
        Delete a specific memory (document)
        
        Returns True if successful, raises exception otherwise.
        """
        try:
            self._make_request("DELETE", f"/v3/documents/{memory_id}")
            return True
        except Exception as e:
            raise
    

    
    def list_memories(
        self,
        cluster_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Memory]:
        """
        Get all memories from a specific cluster
        
        Args:
            cluster_id: Cluster ID to retrieve memories from (required)
            limit: Maximum number of memories to return
            offset: Number of memories to skip
            
        Returns:
            List of Memory objects
        """
        # Validate that the cluster exists
        self._validate_cluster_exists(cluster_id)
        
        params = {
            "limit": limit,
            "offset": offset,
            "collection_ids": [cluster_id]
        }
        
        response = self._make_request("GET", "/v3/documents", params=params)
        
        if isinstance(response, dict) and "results" in response:
            documents = response["results"]
        elif isinstance(response, list):
            documents = response
        else:
            documents = [response]
        
        # Convert all documents to memories
        memories = []
        for doc in documents:
            # Use text field directly from document response
            content = doc.get("text", "No content available")
            
            memory_data = {
                "id": doc.get("id"),
                "content": content,
                "metadata": doc.get("metadata", {}),
                "cluster_id": cluster_id
            }
            memories.append(Memory.from_dict(memory_data))
        
        return memories

    def get_memory(self, memory_id: str) -> Memory:
        """
        Get a specific memory by ID
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory object
        """
        response = self._make_request("GET", f"/v3/documents/{memory_id}")
        
        # Use text field directly from document response
        content = response.get("text", "No content available")
        
        memory_data = {
            "id": response.get("id"),
            "content": content,
            "metadata": response.get("metadata", {}),
            "cluster_id": response.get("collection_ids", [])[0] if response.get("collection_ids", []) else None
        }
        return Memory.from_dict(memory_data)
    
    def search(
        self,
        query: str,
        cluster_id: str,
        limit: int = 10,
        retrieval_type: Union[RetrievalType, str] = RetrievalType.ADVANCED,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search within a specific cluster
        
        Args:
            query: Search query string
            cluster_id: Cluster ID to search within (required)
            limit: Maximum number of results to return
            retrieval_type: Type of retrieval strategy (simple, reasoning, planning)
            filters: Optional filters to apply to the search
            
        Returns:
            List of SearchResult objects
        """
        # Validate that the cluster exists
        self._validate_cluster_exists(cluster_id)
        
        # Convert string to enum if needed
        if isinstance(retrieval_type, str):
            retrieval_type = RetrievalType(retrieval_type)
        
        # Build search settings
        search_settings = {
            "limit": limit,
            "graph_settings": {
                "enabled": False
            }
        }
        
        # Add retrieval type if not advanced
        if retrieval_type != RetrievalType.ADVANCED:
            search_settings["retrieval_type"] = retrieval_type.value
        
        # Build filters
        search_filters = {}
        
        # Add user-provided filters
        if filters:
            search_filters.update(filters)
        
        # Always add cluster filter - cluster_id must be a list for $overlap
        search_filters["collection_id"] = {"$overlap": [cluster_id]}
        
        # Add filters to search settings
        search_settings["filters"] = search_filters
        
        data = {
            "query": query,
            "search_settings": search_settings
        }
        
        response = self._make_request("POST", "/v3/retrieval/search", json_data=data)
        
        # Extract chunk search results from the response
        if isinstance(response, dict) and "results" in response:
            chunk_results = response["results"].get("chunk_search_results", [])
        else:
            chunk_results = []
        
        return [SearchResult.from_dict(result) for result in chunk_results]
    
    # def chat(
    #     self,
    #     agent_id: str,
    #     message: str,
    #     conversation_id: Optional[str] = None,
    #     model: str = "gpt-4",
    #     temperature: float = 0.7,
    #     max_tokens: Optional[int] = None,
    #     retrieval_type: Union[RetrievalType, str] = RetrievalType.SIMPLE,
    #     cluster_id: Optional[str] = None,
    #     stream: bool = False,
    # ) -> AgentResponse:
    #     """
    #     Chat with an agent using its memories for context
    #     
    #     Args:
    #         agent_id: Unique identifier for the agent
    #         message: User message to send to the agent
    #         conversation_id: Optional conversation ID for multi-turn conversations
    #         model: LLM model to use for generation
    #         temperature: Sampling temperature for generation
    #         max_tokens: Maximum tokens to generate
    #         retrieval_type: Type of retrieval to use for context
    #         cluster_id: Optional cluster ID to search within
    #         stream: Whether to enable streaming response
    #         
    #     Returns:
    #         AgentResponse object with the agent's response
    #     """
    #     # Convert string to enum if needed
    #     if isinstance(retrieval_type, str):
    #         retrieval_type = RetrievalType(retrieval_type)
    #     
    #     data = {
    #         "query": message,
    #         "rag_generation_config": {
    #             "model": model,
    #             "temperature": temperature,
    #             "stream": stream,
    #         }
    #     }
    #     
    #     if max_tokens:
    #         data["rag_generation_config"]["max_tokens"] = max_tokens
    #     
    #     if conversation_id:
    #         data["conversation_id"] = conversation_id
    #     
    #     # Note: Skipping collection_id filter for now due to API issue
    #     
    #     if stream:
    #         # For streaming, we need to handle the response differently
    #         return self._make_streaming_generator("POST", "/v3/retrieval/rag", json_data=data, agent_id=agent_id, conversation_id=conversation_id)
    #     else:
    #         response = self._make_request("POST", "/v3/retrieval/rag", json_data=data)
    #     
    #     # Extract the response from the API format
    #     if isinstance(response, dict) and "results" in response:
    #         # The RAG endpoint returns the answer in "generated_answer" field
    #         generated_answer = response["results"].get("generated_answer", "")
    #         if generated_answer:
    #                 return AgentResponse(
    #                     content=generated_answer,
    #                     agent_id=agent_id,
    #                     conversation_id=conversation_id,
    #                     metadata={},
    #                     citations=[]
    #                 )
    #             
    #             # Fallback to completion format if generated_answer is not available
    #             completion = response["results"].get("completion", {})
    #             if completion and "choices" in completion:
    #                 content = completion["choices"][0].get("message", {}).get("content", "")
    #                 return AgentResponse(
    #                     content=content,
    #                     agent_id=agent_id,
    #                     conversation_id=conversation_id,
    #                     metadata={},
    #                     citations=[]
    #                 )
    #         
    #     # Fallback
    #     return AgentResponse(
    #         content="No response received",
    #         agent_id=agent_id,
    #         conversation_id=conversation_id,
    #         metadata={},
    #         citations=[]
    #     )
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the Nebula API
        
        Returns:
            Health status information
        """
        return self._make_request("GET", "/health") 
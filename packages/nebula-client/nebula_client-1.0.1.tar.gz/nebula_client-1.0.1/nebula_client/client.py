"""
Main client for the Nebula Client SDK

This client provides a clean, intuitive interface to Nebula's memory and retrieval capabilities.
"""

import os
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
            endpoint: API endpoint (e.g., "/v3/chunks")
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
    
    # Cluster Management Methods
    
    def create_cluster(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Cluster:
        """
        Create a new cluster
        
        Args:
            name: Name of the cluster
            description: Optional description of the cluster
            metadata: Optional metadata to attach to the cluster
            
        Returns:
            Cluster object representing the created cluster
        """
        data = {
            "name": name,
        }
        if description:
            data["description"] = description
        if metadata:
            data["metadata"] = metadata
        
        response = self._make_request("POST", "/v3/collections", json_data=data)
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
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if metadata is not None:
            data["metadata"] = metadata
        
        response = self._make_request("PATCH", f"/v3/collections/{cluster_id}", json_data=data)
        return Cluster.from_dict(response)
    
    def delete_cluster(self, cluster_id: str) -> bool:
        """
        Delete a cluster
        
        Args:
            cluster_id: ID of the cluster to delete
            
        Returns:
            True if deletion was successful
        """
        self._make_request("DELETE", f"/v3/collections/{cluster_id}")
        return True
    
    def add_memory_to_cluster(
        self,
        cluster_id: str,
        memory_id: str,
    ) -> bool:
        """
        Add a memory to a cluster
        
        Args:
            cluster_id: ID of the cluster
            memory_id: ID of the memory to add
            
        Returns:
            True if addition was successful
        """
        self._make_request(
            "POST", 
            f"/v3/collections/{cluster_id}/memories",
            json_data={"memory_id": memory_id}
        )
        return True
    
    def remove_memory_from_cluster(
        self,
        cluster_id: str,
        memory_id: str,
    ) -> bool:
        """
        Remove a memory from a cluster
        
        Args:
            cluster_id: ID of the cluster
            memory_id: ID of the memory to remove
            
        Returns:
            True if removal was successful
        """
        self._make_request("DELETE", f"/v3/collections/{cluster_id}/memories/{memory_id}")
        return True
    
    def get_cluster_memories(
        self,
        cluster_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Memory]:
        """
        Get all memories in a cluster
        
        Args:
            cluster_id: ID of the cluster
            limit: Maximum number of memories to return
            offset: Number of memories to skip
            
        Returns:
            List of Memory objects
        """
        params = {
            "limit": limit,
            "offset": offset,
            "collection_ids": cluster_id,
        }
        
        response = self._make_request("GET", "/v3/chunks", params=params)
        
        if isinstance(response, dict) and "results" in response:
            memories = response["results"]
        elif isinstance(response, list):
            memories = response
        else:
            memories = [response]
        
        return [Memory.from_dict(memory) for memory in memories]
    
    # Memory Management Methods
    
    def store(
        self,
        agent_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        cluster_id: Optional[str] = None,
    ) -> Memory:
        """
        Store a memory for an agent
        
        Args:
            agent_id: Unique identifier for the agent
            content: The content to store as a memory
            metadata: Optional metadata to attach to the memory
            cluster_id: Optional cluster ID to add the memory to
            
        Returns:
            Memory object representing the stored memory
        """
        data = {
            "agent_id": agent_id,
            "content": content,
        }
        if metadata:
            data["metadata"] = metadata
        if cluster_id:
            data["cluster_id"] = cluster_id
        
        response = self._make_request("POST", "/v3/chunks", json_data=data)
        return Memory.from_dict(response)
    
    def retrieve(
        self,
        agent_id: str,
        query: str,
        limit: int = 10,
        retrieval_type: Union[RetrievalType, str] = RetrievalType.SIMPLE,
        filters: Optional[Dict[str, Any]] = None,
        cluster_id: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Retrieve relevant memories for an agent
        
        Args:
            agent_id: Unique identifier for the agent
            query: Search query to find relevant memories
            limit: Maximum number of results to return
            retrieval_type: Type of retrieval to perform
            filters: Optional filters to apply to the search
            cluster_id: Optional cluster ID to search within
            
        Returns:
            List of SearchResult objects
        """
        # Convert string to enum if needed
        if isinstance(retrieval_type, str):
            retrieval_type = RetrievalType(retrieval_type)
        
        data = {
            "agent_id": agent_id,
            "query": query,
            "limit": limit,
            "retrieval_type": retrieval_type.value,
        }
        
        if filters:
            data["filters"] = filters
        if cluster_id:
            data["cluster_id"] = cluster_id
        
        response = self._make_request("POST", "/v3/chunks/search", json_data=data)
        
        # Handle different response formats
        if isinstance(response, dict) and "results" in response:
            results = response["results"]
        elif isinstance(response, list):
            results = response
        else:
            results = [response]
        
        return [SearchResult.from_dict(result) for result in results]
    
    def delete(self, memory_id: str) -> bool:
        """
        Delete a specific memory
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if deletion was successful
        """
        self._make_request("DELETE", f"/v3/chunks/{memory_id}")
        return True
    
    def get(self, memory_id: str) -> Memory:
        """
        Get a specific memory by ID
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory object representing the memory
        """
        response = self._make_request("GET", f"/v3/chunks/{memory_id}")
        return Memory.from_dict(response)
    
    def list_agent_memories(
        self,
        agent_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Memory]:
        """
        Get all memories for a specific agent
        
        Args:
            agent_id: Unique identifier for the agent
            limit: Maximum number of memories to return
            offset: Number of memories to skip
            
        Returns:
            List of Memory objects
        """
        params = {
            "agent_id": agent_id,
            "limit": limit,
            "offset": offset,
        }
        
        response = self._make_request("GET", "/v3/chunks", params=params)
        
        if isinstance(response, dict) and "chunks" in response:
            memories = response["chunks"]
        elif isinstance(response, list):
            memories = response
        else:
            memories = [response]
        
        return [Memory.from_dict(memory) for memory in memories]
    
    def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search across all memories in the system
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            filters: Optional filters to apply
            
        Returns:
            List of SearchResult objects
        """
        data = {
            "query": query,
            "limit": limit,
        }
        
        if filters:
            data["filters"] = filters
        
        response = self._make_request("POST", "/v3/chunks/search", json_data=data)
        
        if isinstance(response, dict) and "results" in response:
            results = response["results"]
        elif isinstance(response, list):
            results = response
        else:
            results = [response]
        
        return [SearchResult.from_dict(result) for result in results]
    
    def chat(
        self,
        agent_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        retrieval_type: Union[RetrievalType, str] = RetrievalType.SIMPLE,
        cluster_id: Optional[str] = None,
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
            cluster_id: Optional cluster ID to search within
            
        Returns:
            AgentResponse object with the agent's response
        """
        # Convert string to enum if needed
        if isinstance(retrieval_type, str):
            retrieval_type = RetrievalType(retrieval_type)
        
        data = {
            "message": {
                "role": "user",
                "content": message
            },
            "mode": "rag",
        }
        
        if conversation_id:
            data["conversation_id"] = conversation_id
        
        # Add search settings if cluster_id is provided
        if cluster_id:
            data["search_settings"] = {
                "filters": {
                    "collection_ids": [cluster_id]
                }
            }
        
        response = self._make_request("POST", "/v3/retrieval/agent", json_data=data)
        
        # Extract the response from the API format
        if isinstance(response, dict) and "results" in response:
            messages = response["results"].get("messages", [])
            if messages:
                content = messages[0].get("content", "")
                conversation_id = response["results"].get("conversation_id")
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
    
    # Backward compatibility aliases for chunk terminology
    store_chunk = store
    retrieve_chunks = retrieve
    delete_chunk = delete
    get_chunk = get
    list_agent_chunks = list_agent_memories
    search_chunks = search
    chat_with_chunks = chat
    
    # Backward compatibility aliases for collection terminology
    create_collection = create_cluster
    get_collection = get_cluster
    list_collections = list_clusters
    update_collection = update_cluster
    delete_collection = delete_cluster
    add_memory_to_collection = add_memory_to_cluster
    remove_memory_from_collection = remove_memory_from_cluster
    get_collection_memories = get_cluster_memories 
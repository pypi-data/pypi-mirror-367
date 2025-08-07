"""
Data models for the Nebula Client SDK
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class RetrievalType(str, Enum):
    """Types of retrieval available"""
    BASIC = "basic"
    ADVANCED = "advanced"
    CUSTOM = "custom"


@dataclass
class Memory:
    """A memory stored in Nebula"""

    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    cluster_id: Optional[str] = None  # Single cluster ID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """Create a Memory from a dictionary"""
        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            elif isinstance(data["created_at"], datetime):
                created_at = data["created_at"]

        updated_at = None
        if data.get("updated_at"):
            if isinstance(data["updated_at"], str):
                updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            elif isinstance(data["updated_at"], datetime):
                updated_at = data["updated_at"]

        # Handle chunk response format (API returns chunks, not memories)
        memory_id = str(data.get("id", ""))
        
        # API returns 'text' field, SDK expects 'content'
        content = data.get("content") or data.get("text", "")
        
        # Handle cluster_id from collection_ids
        cluster_id = data.get("cluster_id")
        if cluster_id is None:
            collection_ids = data.get("collection_ids", [])
            cluster_id = collection_ids[0] if collection_ids else None
        
        metadata = data.get("metadata", {})
        if data.get("document_id"):
            metadata["document_id"] = data["document_id"]
        
        # Handle document-based approach - if this is a document response
        if data.get("document_id") and not memory_id:
            memory_id = data["document_id"]
        
        # If we have document metadata, merge it
        if data.get("document_metadata"):
            metadata.update(data["document_metadata"])

        return cls(
            id=memory_id,
            content=content,
            metadata=metadata,
            cluster_id=cluster_id,
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Memory to dictionary"""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "cluster_id": self.cluster_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class Cluster:
    """A cluster of memories in Nebula (alias for Collection)"""

    id: str
    name: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    memory_count: int = 0
    owner_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cluster":
        """Create a Cluster from a dictionary"""
        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            elif isinstance(data["created_at"], datetime):
                created_at = data["created_at"]

        updated_at = None
        if data.get("updated_at"):
            if isinstance(data["updated_at"], str):
                updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            elif isinstance(data["updated_at"], datetime):
                updated_at = data["updated_at"]

        # Handle different field mappings from API response
        cluster_id = str(data.get("id", ""))  # Convert UUID to string
        cluster_name = data.get("name", "")
        cluster_description = data.get("description")
        cluster_owner_id = str(data.get("owner_id", "")) if data.get("owner_id") else None
        
        # Map API fields to SDK fields
        # API has document_count, SDK expects memory_count
        memory_count = data.get("document_count", 0)
        
        # Create metadata from API-specific fields
        metadata = {
            "graph_cluster_status": data.get("graph_cluster_status", ""),
            "graph_sync_status": data.get("graph_sync_status", ""),
            "user_count": data.get("user_count", 0),
            "document_count": data.get("document_count", 0)
        }

        return cls(
            id=cluster_id,
            name=cluster_name,
            description=cluster_description,
            metadata=metadata,
            created_at=created_at,
            updated_at=updated_at,
            memory_count=memory_count,
            owner_id=cluster_owner_id
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Cluster to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "memory_count": self.memory_count,
            "owner_id": self.owner_id,
        }


@dataclass
class SearchResult:
    """A search result from Nebula"""

    id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    cluster_id: Optional[str] = None
    memory_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        """Create a SearchResult from a dictionary"""
        # API returns 'text' field, SDK expects 'content'
        content = data.get("content") or data.get("text", "")
        
        # Handle chunk search results
        result_id = data.get("id") or data.get("chunk_id", "")
        
        # Extract collection_ids from the API response and take the first one as cluster_id
        collection_ids = data.get("collection_ids", [])
        cluster_id = collection_ids[0] if collection_ids else None
        
        # Extract document_id from the API response and rename to memory_id
        memory_id = data.get("document_id")
        
        # Get metadata from the API response
        metadata = data.get("metadata", {})
        
        return cls(
            id=result_id,
            content=content,
            score=data.get("score", 0.0),
            metadata=metadata,
            source=data.get("source"),
            cluster_id=cluster_id,
            memory_id=memory_id
        )


# @dataclass
# class AgentResponse:
#     """A response from an agent"""
# 
#     content: str
#     agent_id: str
#     conversation_id: Optional[str] = None
#     metadata: Dict[str, Any] = field(default_factory=dict)
#     citations: List[Dict[str, Any]] = field(default_factory=list)
# 
#     @classmethod
#     def from_dict(cls, data: Dict[str, Any]) -> "AgentResponse":
#         """Create an AgentResponse from a dictionary"""
#         return cls(
#             content=data["content"],
#             agent_id=data["agent_id"],
#             conversation_id=data.get("conversation_id"),
#             metadata=data.get("metadata", {}),
#             citations=data.get("citations", [])
#         )


@dataclass
class SearchOptions:
    """Options for search operations"""

    limit: int = 10
    filters: Optional[Dict[str, Any]] = None
    retrieval_type: RetrievalType = RetrievalType.ADVANCED


# @dataclass
# class AgentOptions:
#     """Options for agent operations"""
# 
#     model: str = "gpt-4"
#     temperature: float = 0.7
#     max_tokens: Optional[int] = None
#     retrieval_type: RetrievalType = RetrievalType.SIMPLE 
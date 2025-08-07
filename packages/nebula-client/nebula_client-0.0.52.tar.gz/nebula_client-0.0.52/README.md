# Nebula Client SDK

A Python SDK for interacting with the Nebula Cloud API, providing a clean interface to Nebula's memory and retrieval capabilities.

## Overview

This SDK provides a clean interface to Nebula's memory and retrieval capabilities, focusing on the core functionality without the complexity of the underlying R2R system. It uses clusters (collections) to organize memories and provides comprehensive search and retrieval capabilities.

## Key Features

- **Cluster-based Organization**: Organize memories into clusters for better management
- **Memory Storage**: Store individual memories with rich metadata
- **Advanced Search**: Search within specific clusters with filtering and ranking
- **Deduplication**: Automatic content-based deduplication
- **Flexible Metadata**: Rich metadata support for memories and clusters
- **Error Handling**: Comprehensive error handling with specific exception types

## Installation

```bash
pip install nebula-client
```

## Quick Start

### Basic Setup

```python
from nebula_client import NebulaClient

# Initialize client
client = NebulaClient(
    api_key="your-api-key",  # or set NEBULA_API_KEY env var
    base_url="https://api.nebulacloud.app"
)
```

### Cluster Management

```python
# Create a cluster
cluster = client.create_cluster(
    name="my_memories",
    description="Cluster for storing important memories"
)

# List clusters
clusters = client.list_clusters()

# Get specific cluster
cluster = client.get_cluster(cluster_id)

# Update cluster
updated_cluster = client.update_cluster(
    cluster_id,
    name="updated_name",
    description="Updated description"
)

# Delete cluster
client.delete_cluster(cluster_id)
```

### Storing Memories

```python
# Store a single memory
memory = client.store(
    content="This is an important memory about machine learning.",
    cluster_id=cluster.id,
    metadata={"topic": "machine_learning", "importance": "high"}
)
```

### Retrieving Memories

```python
# Get a specific memory
memory = client.get_memory(memory_id)
print(f"Content: {memory.content}")
print(f"Cluster ID: {memory.cluster_id}")

# List memories from a specific cluster
memories = client.list_memories(
    cluster_id=cluster.id,
    limit=100
)

for memory in memories:
    print(f"Content: {memory.content}")
    print(f"ID: {memory.id}")
    print(f"Cluster ID: {memory.cluster_id}")
```

### Search Within a Cluster

```python
# Search within a specific cluster
results = client.search(
    query="machine learning concepts",
    cluster_id=cluster.id,
    limit=5,
    retrieval_type="basic"
)

for result in results:
    print(f"Content: {result.content}")
    print(f"Score: {result.score}")
    print(f"Memory ID: {result.memory_id}")
```

## API Reference

### Core Methods

#### Cluster Management

- `create_cluster(name, description=None, metadata=None)` - Create a new cluster
- `get_cluster(cluster_id)` - Get cluster details
- `list_clusters(limit=100, offset=0)` - List all clusters
- `update_cluster(cluster_id, name=None, description=None, metadata=None)` - Update cluster
- `delete_cluster(cluster_id)` - Delete cluster

#### Memory Storage

- `store(content, cluster_id, metadata=None)` - Store individual memory
- `delete(memory_id)` - Delete a memory

#### Memory Retrieval

- `get_memory(memory_id)` - Get specific memory by ID
- `list_memories(cluster_id, limit=100, offset=0)` - List memories from a specific cluster

#### Search

- `search(query, cluster_id, limit=10, retrieval_type=RetrievalType.ADVANCED, filters=None)` - Search within a cluster

### Data Models

#### Memory

```python
@dataclass
class Memory:
    id: str
    content: str
    metadata: Dict[str, Any]
    cluster_id: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

#### Cluster

```python
@dataclass
class Cluster:
    id: str
    name: str
    description: Optional[str]
    metadata: Dict[str, Any]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    memory_count: int
    owner_id: Optional[str]
```

#### SearchResult

```python
@dataclass
class SearchResult:
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    source: Optional[str]
    cluster_id: Optional[str]
    memory_id: Optional[str]
```

### Retrieval Types

The SDK supports different retrieval types for search:

- **`basic`**: Basic semantic search
- **`advanced`**: Enhanced reasoning-based search (default)
- **`custom`**: Custom search configuration

## Error Handling

The SDK provides comprehensive error handling:

```python
from nebula_client.exceptions import (
    NebulaException,
    NebulaClientException,
    NebulaAuthenticationException,
    NebulaRateLimitException,
    NebulaValidationException,
    NebulaClusterNotFoundException,
)

try:
    memory = client.store(
        content="Test memory",
        cluster_id="test_cluster"
    )
except NebulaAuthenticationException:
    print("Invalid API key")
except NebulaRateLimitException:
    print("Rate limit exceeded")
except NebulaClusterNotFoundException as e:
    print(f"Cluster not found: {e}")
except NebulaValidationException as e:
    print(f"Validation error: {e}")
except NebulaException as e:
    print(f"API error: {e}")
```

## Best Practices

1. **Use Clusters for Organization**: Group related memories in clusters
2. **Leverage Metadata**: Add rich metadata to improve search and filtering
3. **Handle Deduplication**: The SDK handles deduplication automatically
4. **Monitor Rate Limits**: Handle rate limit exceptions gracefully
5. **Validate Clusters**: Always ensure clusters exist before storing memories
6. **Use Appropriate Retrieval Types**: Choose the right retrieval type for your search needs

## Complete Example

```python
from nebula_client import NebulaClient

# Initialize client
client = NebulaClient(api_key="your-api-key")

# Create a cluster
cluster = client.create_cluster(
    name="customer_support",
    description="Customer support interactions"
)

# Store customer preferences
memory = client.store(
    content="Customer prefers email communication over phone calls",
    metadata={
        "user_id": "user_123",
        "preference_type": "communication"
    },
    cluster_id=cluster.id
)

# Retrieve the stored memory
retrieved_memory = client.get_memory(memory.id)
print(f"Retrieved content: {retrieved_memory.content}")
print(f"Cluster ID: {retrieved_memory.cluster_id}")

# List memories from the cluster
cluster_memories = client.list_memories(cluster_id=cluster.id)
for memory in cluster_memories:
    print(f"Memory: {memory.content[:100]}...")

# Search within the cluster
results = client.search(
    query="communication preferences",
    cluster_id=cluster.id,
    limit=5
)

for result in results:
    print(f"Score: {result.score:.3f}")
    print(f"Content: {result.content}")
    print("---")

# Clean up
client.delete(memory.id)
client.delete_cluster(cluster.id)
```
import numpy as np
from rust_annie import PyHnswIndex
import pytest
import os

def test_hnsw_basic():
    dim = 64
    index = PyHnswIndex(dims=dim)
    
    # Generate sample data
    data = np.random.rand(1000, dim).astype(np.float32)
    ids = np.arange(1000, dtype=np.int64)
    
    # Add to index
    index.add(data, ids)
    
    # Generate a random query
    query = np.random.rand(dim).astype(np.float32)
    
    # Search
    retrieved_ids = index.search(query, k=10)

    # Assertions
    retrieved_ids = np.array(retrieved_ids)
    assert retrieved_ids.shape == (10,)
    assert issubclass(retrieved_ids.dtype.type, np.integer)

# Deprecated test since PyHnswConfig no longer exists
# def test_invalid_config():
#     config = PyHnswConfig(m=0, ef_construction=10, ef_search=0, max_elements=0)
#     with pytest.raises(ValueError):
#         config.validate()

# Future implementation
# def test_hnsw_save_load(tmp_path):
#     ...

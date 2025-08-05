"""
VRIN Hybrid RAG SDK
A powerful SDK for interacting with the VRIN Hybrid RAG system.

Example usage:
    from vrin import VRINClient
    
    # Initialize client
    client = VRINClient(api_key="your_api_key")
    
    # Insert knowledge into the system
    job = client.insert(
        content="Your knowledge content here...",
        title="Knowledge Title",
        tags=["tag1", "tag2"]
    )
    
    # Wait for processing to complete
    client.wait_for_job(job.job_id)
    
    # Query the knowledge base
    results = client.query("What is machine learning?")
    
    # Print results
    for result in results:
        print(f"Content: {result.content}")
        print(f"Score: {result.score}")
        print(f"Source: {result.metadata.get('title')}")
"""

from .client import VRINClient
from .models import Document, QueryResult, JobStatus
from .exceptions import VRINError, JobFailedError, TimeoutError

__version__ = "0.1.6"
__author__ = "VRIN Team"
__email__ = "support@vrin.ai"

__all__ = [
    "VRINClient",
    "Document", 
    "QueryResult",
    "JobStatus",
    "VRINError",
    "JobFailedError",
    "TimeoutError"
] 
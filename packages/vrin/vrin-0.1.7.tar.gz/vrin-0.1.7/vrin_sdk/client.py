"""
VRIN Client - Main interface for interacting with the VRIN Hybrid RAG system
"""

import time
import requests
from typing import List, Dict, Any, Optional
from .models import Document, QueryResult, JobStatus
from .exceptions import VRINError, JobFailedError, TimeoutError


class VRINClient:
    """
    Main client for interacting with the VRIN Hybrid RAG system.
    
    This client provides a simple interface for:
    - Submitting documents for processing
    - Checking job status
    - Querying the knowledge base
    - Managing documents and metadata
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the VRIN client.
        
        Args:
            api_key: Your VRIN API key
        """
        self.api_key = api_key
        # Hardcoded production URLs - no need to confuse users
        self.rag_base_url = "https://v6kkzi6x1b.execute-api.us-east-1.amazonaws.com/dev"
        self.auth_base_url = "https://gp7g651udc.execute-api.us-east-1.amazonaws.com/Prod"
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def insert(self, 
               content: str,
               title: Optional[str] = None,
               tags: Optional[List[str]] = None,
               source: Optional[str] = None,
               document_type: str = "text") -> JobStatus:
        """
        Insert knowledge into the system for processing and indexing.
        
        This is the primary method for adding any type of knowledge to the system.
        It can handle plain text, documents, facts, or any other knowledge content.
        
        Args:
            content: The knowledge content to insert (text, facts, information, etc.)
            title: Title for the knowledge (optional)
            tags: List of tags for categorization (optional)
            source: Source of the knowledge (optional)
            document_type: Type of content (default: "text")
            
        Returns:
            JobStatus object with job information
            
        Raises:
            VRINError: If the request fails
        """
        payload = {
            "type": "document_processing",
            "content": content,
            "document_type": document_type,
            "metadata": {
                "title": title or "Untitled Document",
                "tags": tags or [],
                "source": source or "vrin-sdk"
            }
        }
        
        try:
            response = self.session.post(f"{self.rag_base_url}/job", json=payload)
            response.raise_for_status()
            data = response.json()
            return JobStatus(**data)
        except requests.exceptions.RequestException as e:
            raise VRINError(f"Failed to submit document: {str(e)}")
    
    def get_job_status(self, job_id: str) -> JobStatus:
        """
        Get the status of a processing job.
        
        Args:
            job_id: The job ID to check
            
        Returns:
            JobStatus object with current status
            
        Raises:
            VRINError: If the request fails
        """
        try:
            response = self.session.get(f"{self.rag_base_url}/job/{job_id}")
            response.raise_for_status()
            data = response.json()
            return JobStatus(**data)
        except requests.exceptions.RequestException as e:
            raise VRINError(f"Failed to get job status: {str(e)}")
    
    def wait_for_job(self, job_id: str, timeout: int = 300, poll_interval: int = 5) -> JobStatus:
        """
        Wait for a job to complete.
        
        Args:
            job_id: The job ID to wait for
            timeout: Maximum time to wait in seconds (default: 300)
            poll_interval: Time between status checks in seconds (default: 5)
            
        Returns:
            JobStatus object with final status
            
        Raises:
            TimeoutError: If the job doesn't complete within timeout
            JobFailedError: If the job fails
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_job_status(job_id)
            
            if status.status == "completed":
                return status
            elif status.status == "failed":
                raise JobFailedError(f"Job {job_id} failed: {status.message}")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")
    
    def query(self, 
              query: str,
              max_results: int = 10) -> List[QueryResult]:
        """
        Query the knowledge base using hybrid RAG search.
        
        Args:
            query: The search query
            user_id: User ID for personalized results (optional)
            max_results: Maximum number of results to return (default: 10)
            search_type: Type of search ("hybrid", "sparse", "dense") (default: "hybrid")
            
        Returns:
            List of QueryResult objects
            
        Raises:
            VRINError: If the request fails
        """
        payload = {
            "query": query,
            "max_results": max_results
        }
        
        try:
            response = self.session.post(f"{self.rag_base_url}/query", json=payload)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for result_data in data.get('results', []):
                results.append(QueryResult(**result_data))
            
            return results
        except requests.exceptions.RequestException as e:
            raise VRINError(f"Failed to query knowledge base: {str(e)}")
    
    def insert_and_wait(self, 
                       content: str,
                       title: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       source: Optional[str] = None,
                       document_type: str = "text",
                       timeout: int = 300) -> JobStatus:
        """
        Insert knowledge and wait for it to complete processing.
        
        This is a convenience method that combines insert() and wait_for_job().
        
        Args:
            content: The knowledge content to insert
            title: Title for the knowledge (optional)
            tags: List of tags for categorization (optional)
            source: Source of the knowledge (optional)
            document_type: Type of content (default: "text")
            timeout: Maximum time to wait in seconds (default: 300)
            
        Returns:
            JobStatus object with final status
        """
        job = self.insert(
            content=content,
            title=title,
            tags=tags,
            source=source,
            document_type=document_type
        )
        
        return self.wait_for_job(job.job_id, timeout=timeout)
    
    def insert_text(self, text: str) -> JobStatus:
        """
        Insert plain text knowledge into the system.
        
        This is a simplified method for quickly inserting plain text without
        needing to specify title, tags, or other metadata.
        
        Args:
            text: The plain text to insert
            
        Returns:
            JobStatus object with job information
            
        Raises:
            VRINError: If the request fails
        """
        return self.insert(
            content=text,
            title="Plain Text Knowledge",
            tags=["text", "plain"],
            source="vrin-sdk-text",
            document_type="text"
        )
    
    def batch_insert(self, documents: List[Document]) -> List[JobStatus]:
        """
        Insert multiple knowledge items for processing.
        
        Args:
            documents: List of Document objects to insert
            
        Returns:
            List of JobStatus objects for each inserted knowledge item
        """
        jobs = []
        for doc in documents:
            job = self.insert(
                content=doc.content,
                title=doc.title,
                tags=doc.tags,
                source=doc.source,
                document_type=doc.document_type
            )
            jobs.append(job)
        
        return jobs
    
    def batch_wait_for_jobs(self, job_ids: List[str], timeout: int = 300) -> List[JobStatus]:
        """
        Wait for multiple jobs to complete.
        
        Args:
            job_ids: List of job IDs to wait for
            timeout: Maximum time to wait per job in seconds (default: 300)
            
        Returns:
            List of JobStatus objects for completed jobs
        """
        completed_jobs = []
        for job_id in job_ids:
            try:
                status = self.wait_for_job(job_id, timeout=timeout)
                completed_jobs.append(status)
            except (TimeoutError, JobFailedError) as e:
                # Create a failed status object
                failed_status = JobStatus(
                    job_id=job_id,
                    status="failed",
                    message=str(e),
                    error_details=str(e)
                )
                completed_jobs.append(failed_status)
        
        return completed_jobs 
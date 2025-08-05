"""
Promptlyzer Client Library

A comprehensive Python client for interacting with the Promptlyzer API.
Provides prompt management, caching, and multi-provider LLM inference capabilities.

Author: Promptlyzer Team
License: MIT
"""

import os
import json
import requests
import time
import asyncio
import aiohttp
import random
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta, timezone

from .exceptions import (
    PromptlyzerError,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
    ServerError,
    RateLimitError
)
from .inference import InferenceManager
from .simple_collector import SimpleDatasetCollector
from .optimization import OptimizationManager


class PromptlyzerClient:
    """
    Main client for interacting with the Promptlyzer API.
    
    This client provides:
    - API key and JWT authentication support
    - Prompt management with caching
    - Multi-provider LLM inference
    - Connection pooling for better performance
    - Comprehensive error handling
    
    Example:
        >>> client = PromptlyzerClient(api_key="pk_live_...")
        >>> prompt = client.get_prompt("project-id", "greeting")
        >>> print(prompt['content'])
    """
    
    def __init__(
        self,
        api_url: str = None,
        api_key: str = None,
        environment: str = "dev",
        cache_ttl_minutes: int = 5,
        max_pool_connections: int = 10,
        enable_data_collection: bool = True,
        collection_sample_rate: float = 0.2,
        collection_batch_size: int = 10,
        weekly_collection_quota: int = 100
    ):
        """
        Initialize a new PromptlyzerClient.
        
        Args:
            api_url: The URL of the Promptlyzer API.
            api_key: API key for authentication (required).
            environment: The prompt environment to use (dev, staging, prod).
            cache_ttl_minutes: Cache time-to-live in minutes. Defaults to 5 minutes.
            max_pool_connections: Maximum number of connections in the pool. Defaults to 10.
            enable_data_collection: Enable automatic data collection for optimization. Defaults to True.
            collection_sample_rate: Sampling rate for data collection (0.0-1.0). Defaults to 0.2 (20%).
            collection_batch_size: Number of items to batch before sending. Defaults to 10.
            weekly_collection_quota: Maximum items to collect per week. Defaults to 100.
        """
        self.api_url = api_url or os.environ.get("PROMPTLYZER_API_URL", "https://api.promptlyzer.com")
        self.api_key = api_key or os.environ.get("PROMPTLYZER_API_KEY")
        self.environment = environment
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.max_pool_connections = max_pool_connections
        
        # Initialize cache
        self._cache = {}
        
        # Initialize session for connection pooling
        self._session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=self.max_pool_connections, 
                                              pool_maxsize=self.max_pool_connections)
        self._session.mount('http://', adapter)
        self._session.mount('https://', adapter)
        
        # Async session (initialized on demand)
        self._async_session = None
        
        # Validate API key is provided
        if not self.api_key:
            raise AuthenticationError("API key is required. Set PROMPTLYZER_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize inference manager
        self.inference = InferenceManager(promptlyzer_client=self)
        
        # Initialize optimization manager
        self.optimization = OptimizationManager(promptlyzer_client=self)
        
        # Initialize data collection settings
        self.enable_data_collection = enable_data_collection
        self.collection_sample_rate = collection_sample_rate
        self.collection_batch_size = collection_batch_size
        self.weekly_collection_quota = weekly_collection_quota
        
        # Data collection state
        self._collection_buffer = []
        self._weekly_usage = 0
        self._week_start = self._get_current_week_start()
        self._active_sessions = {}
        self._collection_stats = {
            "total_collected": 0,
            "total_sent": 0,
            "last_batch_sent": None
        }
    
    def __del__(self):
        """Cleanup resources on deletion."""
        # Send any remaining batched data
        if hasattr(self, '_collection_buffer') and self._collection_buffer:
            self._send_batch(force=True)
        
        if hasattr(self, '_session') and self._session:
            self._session.close()
    
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get the headers for API requests.
        
        Returns:
            Dict[str, str]: The headers with API key authentication.
        """
        return {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
    
    def _get_cache_key(self, *args) -> str:
        """
        Generate a cache key from the arguments.
        
        Args:
            *args: Arguments to include in the cache key.
            
        Returns:
            str: The cache key.
        """
        return ":".join(str(arg) for arg in args)
    
    def _get_from_cache(self, cache_key: str) -> Tuple[bool, Any]:
        """
        Try to get a value from the cache.
        
        Args:
            cache_key: The cache key.
            
        Returns:
            Tuple[bool, Any]: A tuple of (is_cached, value).
                If is_cached is False, value will be None.
        """
        if cache_key not in self._cache:
            return False, None
            
        cached_item = self._cache[cache_key]
        if datetime.now() - cached_item["timestamp"] > self.cache_ttl:
            # Cache expired
            return False, None
            
        return True, cached_item["value"]
    
    def _add_to_cache(self, cache_key: str, value: Any) -> None:
        """
        Add a value to the cache.
        
        Args:
            cache_key: The cache key.
            value: The value to cache.
        """
        self._cache[cache_key] = {
            "value": value,
            "timestamp": datetime.now()
        }
    
    def list_prompts(self, project_id: str, environment: Optional[str] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        List all prompts in a project, returning only their latest versions.
        
        Args:
            project_id: The ID of the project.
            environment: The environment to filter by. Defaults to client's environment.
            use_cache: Whether to use cached results if available. Defaults to True.
            
        Returns:
            Dict[str, Any]: An object containing prompts and total count.
        """
        env = environment or self.environment
        cache_key = self._get_cache_key("list_prompts", project_id, env)
        
        # Try to get from cache if use_cache is True
        if use_cache:
            is_cached, cached_value = self._get_from_cache(cache_key)
            if is_cached:
                return cached_value
        
        # Fixed URL - not using version parameter
        url = f"{self.api_url}/projects/{project_id}/prompts?env={env}"
        headers = self.get_headers()
        
        response = self._make_request("GET", url, headers=headers)
        
        # Cache the results
        self._add_to_cache(cache_key, response)
        
        return response
    
    def get_prompt(self, project_id: str, prompt_name: str, environment: Optional[str] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get a specific prompt by name, returning only the latest version with content directly accessible.
        
        Args:
            project_id: The ID of the project.
            prompt_name: The name of the prompt.
            environment: The environment to get the prompt from. Defaults to client's environment.
            use_cache: Whether to use cached results if available. Defaults to True.
            
        Returns:
            Dict[str, Any]: A simplified prompt object with content directly accessible.
        """
        env = environment or self.environment
        cache_key = self._get_cache_key("get_prompt", project_id, prompt_name, env)
        
        # Try to get from cache if use_cache is True
        if use_cache:
            is_cached, cached_value = self._get_from_cache(cache_key)
            if is_cached:
                return cached_value
        
        # Fixed URL - not using version parameter
        url = f"{self.api_url}/projects/{project_id}/prompts/{prompt_name}?env={env}"
        headers = self.get_headers()
        
        response = self._make_request("GET", url, headers=headers)
        
        # Simplify the response structure to make content directly accessible
        simplified_response = {
            "name": response.get("name"),
            "project_id": project_id,
            "environment": env,
            "version": response.get("current_version"),
            "content": response.get("version", {}).get("content", "")
        }
        
        # Cache the simplified results
        self._add_to_cache(cache_key, simplified_response)
        
        return simplified_response
    
    def get_prompt_content(self, project_id: str, prompt_name: str, environment: Optional[str] = None, use_cache: bool = True) -> str:
        """
        Get only the content of a prompt.
        
        Args:
            project_id: The ID of the project.
            prompt_name: The name of the prompt.
            environment: The environment to get the prompt from. Defaults to client's environment.
            use_cache: Whether to use cached results if available. Defaults to True.
            
        Returns:
            str: The prompt content text.
        """
        prompt_data = self.get_prompt(project_id, prompt_name, environment, use_cache)
        return prompt_data.get("content", "")
    
    def clear_cache(self) -> None:
        """
        Clear the entire cache.
        """
        self._cache = {}
    
    def clear_prompt_cache(self, project_id: str, prompt_name: str = None, environment: Optional[str] = None) -> None:
        """
        Clear cache for a specific prompt or all prompts in a project.
        
        Args:
            project_id: The ID of the project.
            prompt_name: The name of the prompt. If None, clear all prompts in the project.
            environment: The environment to clear. If None, clear client's environment.
        """
        env = environment or self.environment
        
        if prompt_name:
            # Clear specific prompt cache
            get_key = self._get_cache_key("get_prompt", project_id, prompt_name, env)
            if get_key in self._cache:
                del self._cache[get_key]
        else:
            # Clear all prompts in the project
            list_key = self._get_cache_key("list_prompts", project_id, env)
            if list_key in self._cache:
                del self._cache[list_key]
            
            # Also clear specific prompt caches for this project
            keys_to_delete = []
            for key in self._cache:
                if project_id in key and env in key:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self._cache[key]
    
    def _make_request(self, method: str, url: str, headers: Dict[str, str] = None, json_data: Dict[str, Any] = None) -> Any:
        """
        Make a request to the Promptlyzer API using connection pooling.
        
        Args:
            method: The HTTP method to use.
            url: The URL to request.
            headers: The headers to include.
            json_data: The JSON data to send.
            
        Returns:
            Any: The parsed JSON response.
            
        Raises:
            Various PromptlyzerError subclasses depending on the error.
        """
        try:
            response = self._session.request(method, url, headers=headers, json=json_data)
            response.raise_for_status()
            return response.json()
        
        except requests.HTTPError as e:
            return self._handle_request_error(e, e.response)
    
    def _handle_request_error(self, error: requests.HTTPError, response: requests.Response) -> None:
        """
        Handle HTTP errors from the API.
        
        Args:
            error: The HTTPError exception.
            response: The response object.
            
        Raises:
            AuthenticationError: For 401 status codes.
            ResourceNotFoundError: For 404 status codes.
            ValidationError: For 400 and 422 status codes.
            RateLimitError: For 429 status codes.
            ServerError: For 500+ status codes.
            PromptlyzerError: For all other error codes.
        """
        status_code = response.status_code
        
        try:
            error_data = response.json()
            detail = error_data.get("detail", "Unknown error")
        except (ValueError, KeyError):
            detail = response.text or "Unknown error"
        
        if status_code == 401:
            raise AuthenticationError(detail, status_code, response)
        elif status_code == 404:
            raise ResourceNotFoundError(detail, status_code, response)
        elif status_code in (400, 422):
            raise ValidationError(detail, status_code, response)
        elif status_code == 429:
            raise RateLimitError(detail, status_code, response)
        elif status_code >= 500:
            raise ServerError(detail, status_code, response)
        else:
            raise PromptlyzerError(detail, status_code, response)
    
    def configure_inference_provider(self, provider: str, api_key: str, base_url: Optional[str] = None) -> None:
        """
        Configure an inference provider with API key.
        
        Args:
            provider: Provider name (openai, anthropic, together)
            api_key: API key for the provider
            base_url: Optional base URL for the provider
        """
        self.inference.add_provider(provider, api_key, base_url)
    
    def get_inference_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get inference metrics summary from API.
        
        Args:
            days: Number of days to look back (default: 7)
            
        Returns:
            Dict containing metrics summary
        """
        try:
            url = f"{self.api_url}/llm-gateway/metrics/summary?days={days}"
            headers = self.get_headers()
            response = self._make_request("GET", url, headers=headers)
            return response.get("summary", {})
        except Exception:
            # Fallback to local metrics if API fails
            return self.inference.get_metrics_summary()
    
    async def submit_inference_metrics(self) -> None:
        """Submit collected inference metrics to the API."""
        await self.inference.submit_metrics_to_api()
    
    def collect_inference_data(
        self,
        prompt: str,
        response: str,
        project_id: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        session_id: Optional[str] = None,
        optimization_data: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Collect inference data from external providers for optimization.
        
        This method allows you to send inference data to Promptlyzer even when
        using your own inference providers (OpenAI, Anthropic, etc. directly).
        
        Args:
            prompt: The prompt sent to the model (required)
            response: The model's response (required)
            project_id: Project ID to associate the data with (optional)
            model: Model name (optional, e.g., "gpt-4o")
            provider: Provider name (optional, e.g., "openai")
            session_id: Session ID for conversation tracking (optional)
            optimization_data: Data for prompt optimization (optional):
                - system_message: The system prompt to optimize
                - user_question: The actual user question
                - context: Any additional context
                - messages: Previous conversation messages
            metrics: Performance metrics (optional):
                - latency_ms: Response time in milliseconds
                - tokens: Token count
                - cost: Cost of the inference
        
        Returns:
            bool: True if data was successfully collected, False otherwise
            
        Example:
            >>> # Minimal usage
            >>> client.collect_inference_data(
            ...     prompt="What is the capital of France?",
            ...     response="The capital of France is Paris."
            ... )
            
            >>> # With optimization data
            >>> client.collect_inference_data(
            ...     prompt="Where is my order?",
            ...     response="Your order #12345 was shipped yesterday.",
            ...     optimization_data={
            ...         "system_message": "You are a helpful assistant",
            ...         "user_question": "Where is my order?",
            ...         "context": {"order_id": "12345"}
            ...     }
            ... )
        """
        try:
            # Check if data collection is enabled
            if not self.enable_data_collection:
                return False
            
            # Check weekly quota
            if not self._check_and_update_quota():
                return False
            
            # Apply sampling logic
            if not self._should_collect_sample(session_id):
                return False
            
            # Track session if provided
            if session_id:
                self._track_session(session_id)
            
            # Validate optimization data if provided
            if optimization_data:
                validated_optimization_data = self.inference._validate_optimization_data(optimization_data)
            else:
                validated_optimization_data = None
            
            # Prepare the data payload
            data = {
                "prompt": prompt,
                "response": response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Add optional fields if provided
            if project_id:
                data["project_id"] = project_id
            if model:
                data["model"] = model
            if provider:
                data["provider"] = provider
            if session_id:
                data["session_id"] = session_id
            if validated_optimization_data:
                # Extract system_message and user_question to root level for backend
                if "system_message" in validated_optimization_data:
                    data["system_message"] = validated_optimization_data["system_message"]
                if "user_question" in validated_optimization_data:
                    data["user_question"] = validated_optimization_data["user_question"]
                if "context" in validated_optimization_data:
                    data["context"] = validated_optimization_data["context"]
                # Keep full optimization_data for backward compatibility
                data["optimization_data"] = validated_optimization_data
            if metrics:
                data["metrics"] = metrics
            
            # Add to batch buffer instead of sending immediately
            self._collection_buffer.append(data)
            self._collection_stats["total_collected"] += 1
            
            # Send batch if buffer is full
            if len(self._collection_buffer) >= self.collection_batch_size:
                return self._send_batch()
            
            # For immediate sending (when buffer is not full but user wants to send)
            # This is handled by flush_collection_buffer() method
            
            return True
            
        except Exception as e:
            # Log error but don't raise - data collection should not break user's flow
            if hasattr(self, 'logger'):
                self.logger.warning(f"Failed to collect inference data: {str(e)}")
            return False
    
    def _get_current_week_start(self) -> datetime:
        """Get the start of the current week (Monday)."""
        now = datetime.now(timezone.utc)
        days_since_monday = now.weekday()
        week_start = now - timedelta(days=days_since_monday)
        return week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def _check_and_update_quota(self) -> bool:
        """Check if weekly quota allows collection and update usage."""
        # Reset weekly usage if new week
        current_week_start = self._get_current_week_start()
        if current_week_start > self._week_start:
            self._weekly_usage = 0
            self._week_start = current_week_start
        
        # Check quota
        if self._weekly_usage >= self.weekly_collection_quota:
            return False
        
        self._weekly_usage += 1
        return True
    
    def _should_collect_sample(self, session_id: Optional[str] = None) -> bool:
        """Determine if this request should be collected based on sampling strategy."""
        # Session-based priority
        if session_id:
            if session_id not in self._active_sessions:
                # New session - higher priority
                return random.random() < min(self.collection_sample_rate * 3, 1.0)
            else:
                # Active session - medium priority
                session_data = self._active_sessions[session_id]
                if session_data["message_count"] >= 3:
                    # Long conversation - high value
                    return random.random() < min(self.collection_sample_rate * 2, 0.8)
        
        # Default sampling
        return random.random() < self.collection_sample_rate
    
    def _track_session(self, session_id: str) -> None:
        """Track session data for smart collection."""
        if session_id not in self._active_sessions:
            self._active_sessions[session_id] = {
                "message_count": 0,
                "start_time": datetime.now(timezone.utc),
                "last_activity": datetime.now(timezone.utc)
            }
        else:
            self._active_sessions[session_id]["message_count"] += 1
            self._active_sessions[session_id]["last_activity"] = datetime.now(timezone.utc)
        
        # Clean up old sessions (older than 1 hour)
        current_time = datetime.now(timezone.utc)
        expired_sessions = [
            sid for sid, data in self._active_sessions.items()
            if (current_time - data["last_activity"]).total_seconds() > 3600
        ]
        for sid in expired_sessions:
            del self._active_sessions[sid]
    
    def _send_batch(self, force: bool = False) -> bool:
        """Send batched data to the API."""
        if not self._collection_buffer:
            return True
        
        # Don't send if buffer is not full (unless forced)
        if not force and len(self._collection_buffer) < self.collection_batch_size:
            return True
        
        # Group items by project_id
        items_by_project = {}
        for item in self._collection_buffer:
            project_id = item.get("project_id")
            if project_id:
                if project_id not in items_by_project:
                    items_by_project[project_id] = []
                items_by_project[project_id].append(item)
        
        # Check quota for each project and prepare sendable items
        batch_to_send = []
        items_to_keep = []
        
        for project_id, items in items_by_project.items():
            quota_status = self._get_backend_quota_status(project_id)
            remaining = quota_status.get("remaining", 0)
            
            if remaining > 0:
                # Add items up to the remaining quota
                can_send = items[:remaining]
                cant_send = items[remaining:]
                
                batch_to_send.extend(can_send)
                items_to_keep.extend(cant_send)
                
                if cant_send and hasattr(self, 'logger'):
                    self.logger.info(f"Project {project_id} quota limit. Buffering {len(cant_send)} items.")
            else:
                # No quota for this project, keep all items
                items_to_keep.extend(items)
                if hasattr(self, 'logger'):
                    self.logger.info(f"Project {project_id} quota exhausted. Buffering {len(items)} items.")
        
        if not batch_to_send:
            return False
        
        try:
            # Send to API - new endpoint expects array directly
            url = f"{self.api_url}/optimization/collect-inference/batch"
            headers = self.get_headers()
            
            # Send array directly as per new API format
            response = self._make_request("POST", url, headers=headers, json_data=batch_to_send)
            
            # Update statistics
            self._collection_stats["total_sent"] += len(batch_to_send)
            self._collection_stats["last_batch_sent"] = datetime.now(timezone.utc)
            
            # Update buffer with items that couldn't be sent
            self._collection_buffer = items_to_keep
            
            return True
            
        except RateLimitError as e:
            # Quota exceeded - keep data in buffer for next week
            if hasattr(self, 'logger'):
                self.logger.warning(f"Weekly quota exceeded: {str(e)}")
            # Don't clear buffer, keep for retry
            return False
        except Exception as e:
            # Other errors - keep data in buffer for retry
            if hasattr(self, 'logger'):
                self.logger.error(f"Failed to send batch: {str(e)}")
            return False
    
    def get_collection_status(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current data collection status and statistics.
        
        Args:
            project_id: Optional project ID to get specific project quota.
                       If None, returns all projects quota status.
        """
        # Get backend quota status
        backend_quota = self._get_backend_quota_status(project_id)
        
        # For specific project
        if project_id and "project_id" in backend_quota:
            return {
                "enabled": self.enable_data_collection,
                "project_id": backend_quota.get("project_id"),
                "weekly_limit": backend_quota.get("weekly_limit", 100),
                "used_this_week": backend_quota.get("used_this_week", 0),
                "remaining": backend_quota.get("remaining", 0),
                "reset_date": backend_quota.get("reset_date"),
                "days_until_reset": backend_quota.get("days_until_reset"),
                "buffer_size": len([item for item in self._collection_buffer if item.get("project_id") == project_id]),
                "total_collected": self._collection_stats["total_collected"],
                "total_sent": self._collection_stats["total_sent"]
            }
        
        # For all projects
        return {
            "enabled": self.enable_data_collection,
            "weekly_limit_per_project": backend_quota.get("weekly_limit_per_project", 100),
            "reset_date": backend_quota.get("reset_date"),
            "days_until_reset": backend_quota.get("days_until_reset"),
            "projects": backend_quota.get("projects", []),
            "buffer_size": len(self._collection_buffer),
            "buffer_by_project": self._get_buffer_stats_by_project(),
            "total_collected": self._collection_stats["total_collected"],
            "total_sent": self._collection_stats["total_sent"],
            "active_sessions": len(self._active_sessions)
        }
    
    def _get_buffer_stats_by_project(self) -> Dict[str, int]:
        """Get buffer item count grouped by project."""
        stats = {}
        for item in self._collection_buffer:
            project_id = item.get("project_id", "unknown")
            stats[project_id] = stats.get(project_id, 0) + 1
        return stats
    
    def _get_backend_quota_status(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get quota status from backend."""
        try:
            url = f"{self.api_url}/optimization/collect-inference/quota"
            if project_id:
                url += f"?project_id={project_id}"
            headers = self.get_headers()
            return self._make_request("GET", url, headers=headers)
        except Exception:
            # Fallback to local estimation if backend call fails
            return {
                "weekly_limit": self.weekly_collection_quota,
                "used_this_week": self._weekly_usage,
                "remaining": max(0, self.weekly_collection_quota - self._weekly_usage)
            }
    
    def flush_collection_buffer(self) -> bool:
        """Manually flush the collection buffer."""
        return self._send_batch(force=True)
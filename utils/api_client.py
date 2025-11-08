"""OpenAI-compatible API client wrapper"""

import json
import time
from typing import Any, Dict, Optional
import requests


class OpenAIAPIClient:
    """
    Client for interacting with OpenAI-compatible APIs
    
    Supports any API that follows the OpenAI API format, including:
    - OpenAI
    - Venice.ai
    - OpenRouter
    - Together.ai
    - Local Ollama
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 120,
        max_retries: int = 3,
        retry_delay: int = 2,
    ):
        """
        Initialize API client
        
        Args:
            base_url: API base URL (e.g., "https://api.openai.com/v1")
            api_key: API authentication key
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON as dictionary
            
        Raises:
            Exception: On API error after retries exhausted
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # Raise exception for bad status codes
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.Timeout as e:
                last_exception = e
                print(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                print(f"Connection error (attempt {attempt + 1}/{self.max_retries})")
                
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                
                # Don't retry on client errors (4xx)
                if 400 <= status_code < 500:
                    error_msg = f"API Error {status_code}: {e.response.text}"
                    raise Exception(error_msg)
                
                last_exception = e
                print(f"HTTP error {status_code} (attempt {attempt + 1}/{self.max_retries})")
                
            except Exception as e:
                last_exception = e
                print(f"Unexpected error (attempt {attempt + 1}/{self.max_retries}): {e}")
            
            # Wait before retrying
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        # All retries failed
        raise Exception(f"API request failed after {self.max_retries} attempts: {last_exception}")
    
    def list_models(self) -> list[Dict[str, Any]]:
        """
        List available models from the API
        
        Returns:
            List of model objects
        """
        response = self._request("GET", "/models")
        return response.get("data", [])
    
    def chat_completion(
        self,
        model: str,
        messages: list[Dict[str, Any]],
        **params
    ) -> Dict[str, Any]:
        """
        Create a chat completion
        
        Args:
            model: Model identifier (required)
            messages: Array of message objects (required)
            **params: Optional parameters:
                - temperature (float): 0-2
                - max_tokens (int): Max completion tokens
                - top_p (float): 0-1
                - frequency_penalty (float): -2 to 2
                - presence_penalty (float): -2 to 2
                - stop (str or list): Stop sequences
                - seed (int): For reproducibility
                - response_format (dict): {"type": "json_object"}
                - etc.
                
        Returns:
            Completion response object
        """
        data = {
            "model": model,
            "messages": messages,
            **params
        }
        
        return self._request("POST", "/chat/completions", json=data)
    
    def generate_image(
        self,
        model: str,
        prompt: str,
        **params
    ) -> Dict[str, Any]:
        """
        Generate images
        
        Args:
            model: Model identifier (required for some APIs)
            prompt: Image description (required)
            **params: Optional parameters:
                - n (int): Number of images (1-10)
                - size (str): Image size (e.g., "1024x1024")
                - quality (str): "standard" or "hd"
                - style (str): "vivid" or "natural"
                - response_format (str): "url" or "b64_json"
                - width (int): Image width
                - height (int): Image height
                - negative_prompt (str): What to avoid (some APIs)
                - etc.
                
        Returns:
            Image generation response object
        """
        data = {
            "prompt": prompt,
            **params
        }
        
        # Some APIs require model, some don't
        if model:
            data["model"] = model
        
        return self._request("POST", "/images/generations", json=data)
    
    def generate_video(
        self,
        model: str,
        prompt: str,
        **params
    ) -> Dict[str, Any]:
        """
        Generate videos (OpenAI Video API)
        
        Args:
            model: Model identifier (required)
            prompt: Video description (required)
            **params: Optional parameters:
                - duration (int): Video duration in seconds
                - resolution (str): Video resolution
                - fps (int): Frames per second
                - aspect_ratio (str): e.g., "16:9", "9:16", "1:1"
                - image_url (str): For image-to-video
                - etc.
                
        Returns:
            Video generation response object
        """
        data = {
            "model": model,
            "prompt": prompt,
            **params
        }
        
        return self._request("POST", "/videos/create", json=data)
    
    def generate_speech(
        self,
        model: str,
        input: str,
        voice: str,
        **params
    ) -> bytes:
        """
        Generate speech audio
        
        Args:
            model: TTS model identifier (required)
            input: Text to synthesize (required)
            voice: Voice identifier (required)
            **params: Optional parameters:
                - response_format (str): Audio format
                - speed (float): 0.25-4.0
                - etc.
                
        Returns:
            Audio bytes
        """
        data = {
            "model": model,
            "input": input,
            "voice": voice,
            **params
        }
        
        url = f"{self.base_url}/audio/speech"
        
        response = self.session.post(
            url,
            json=data,
            timeout=self.timeout,
        )
        
        response.raise_for_status()
        return response.content


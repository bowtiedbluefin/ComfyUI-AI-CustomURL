"""Model discovery and management"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from .api_client import OpenAIAPIClient


class ModelManager:
    """
    Manages model discovery and caching for OpenAI-compatible APIs
    """
    
    def __init__(self, cache_dir: Optional[Path] = None, cache_duration: int = 3600):
        """
        Initialize model manager
        
        Args:
            cache_dir: Directory for cache storage
            cache_duration: Cache validity duration in seconds (default: 1 hour)
        """
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent / "data"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_duration = cache_duration
        
        self.cache_file = self.cache_dir / "model_cache.json"
        self._cache: Dict[str, Dict] = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Dict]:
        """Load cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load model cache: {e}")
        
        return {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            print(f"Failed to save model cache: {e}")
    
    def _is_cache_valid(self, profile_name: str) -> bool:
        """Check if cached data is still valid"""
        if profile_name not in self._cache:
            return False
        
        cache_data = self._cache[profile_name]
        timestamp = cache_data.get("timestamp", 0)
        
        return (time.time() - timestamp) < self.cache_duration
    
    def fetch_models(
        self,
        base_url: str,
        api_key: str,
        profile_name: str = "default",
        force_refresh: bool = False,
    ) -> List[Dict]:
        """
        Fetch models from API with caching
        
        Args:
            base_url: API base URL
            api_key: API key
            profile_name: Profile identifier for caching
            force_refresh: Force refresh cache
            
        Returns:
            List of model objects
        """
        # Check cache first
        if not force_refresh and self._is_cache_valid(profile_name):
            return self._cache[profile_name]["models"]
        
        # Fetch from API
        try:
            client = OpenAIAPIClient(base_url, api_key)
            models = client.list_models()
            
            # Update cache
            self._cache[profile_name] = {
                "timestamp": time.time(),
                "models": models,
                "base_url": base_url,
            }
            self._save_cache()
            
            return models
            
        except Exception as e:
            print(f"Failed to fetch models: {e}")
            
            # Return cached data if available
            if profile_name in self._cache:
                print("Using cached model data")
                return self._cache[profile_name]["models"]
            
            return []
    
    def get_models_by_capability(
        self,
        models: List[Dict],
        capability: str,
    ) -> List[str]:
        """
        Filter models by capability
        
        Args:
            models: List of model objects
            capability: Capability to filter by (text, image, vision, audio, video)
            
        Returns:
            List of model IDs
        """
        filtered = []
        
        for model in models:
            model_id = model.get("id", "")
            
            # Try to infer capability from model ID or metadata
            if capability == "text":
                # Text models typically include: gpt, claude, llama, etc.
                if any(k in model_id.lower() for k in ["gpt", "claude", "llama", "mistral", "qwen"]):
                    filtered.append(model_id)
            
            elif capability == "vision":
                # Vision-capable models
                if any(k in model_id.lower() for k in ["vision", "gpt-4", "claude-3", "gemini"]):
                    filtered.append(model_id)
            
            elif capability == "image":
                # Image generation models
                if any(k in model_id.lower() for k in ["dall-e", "dalle", "stable-diffusion", "sd", "flux", "midjourney"]):
                    filtered.append(model_id)
            
            elif capability == "audio" or capability == "speech":
                # TTS models
                if any(k in model_id.lower() for k in ["tts", "whisper", "speech", "audio"]):
                    filtered.append(model_id)
            
            elif capability == "video":
                # Video generation models
                if any(k in model_id.lower() for k in ["video", "sora", "runway", "kling", "pika"]):
                    filtered.append(model_id)
            
            else:
                # Return all if unknown capability
                filtered.append(model_id)
        
        return filtered if filtered else [m.get("id", "") for m in models]
    
    def clear_cache(self, profile_name: Optional[str] = None):
        """
        Clear cached data
        
        Args:
            profile_name: Specific profile to clear, or None for all
        """
        if profile_name:
            self._cache.pop(profile_name, None)
        else:
            self._cache.clear()
        
        self._save_cache()


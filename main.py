"""
AI CustomURL Integration for ComfyUI

This extension enables text, image, video, and speech generation using any
OpenAI-compatible API endpoint with custom URLs.

Supports: OpenAI, Venice.ai, OpenRouter, Together.ai, Ollama, and more.
"""

from typing_extensions import override
from comfy_api.latest import ComfyExtension, io
from aiohttp import web
from server import PromptServer

# Import all node classes
from nodes import (
    TextGenerationNode,
    TextAdvancedParamsNode,
    ImageGenerationNode,
    ImageAdvancedParamsNode,
    VideoGenerationNode,
    VideoAdvancedParamsNode,
    SpeechGenerationNode,
    SpeechAdvancedParamsNode,
    ImageURLLoaderNode,
    VideoURLLoaderNode,
)

# Server routes
routes = PromptServer.instance.routes


@routes.get("/ai_customurl/models")
async def get_models(request):
    """
    Fetch available models from API
    
    Query params:
        - base_url: API base URL
        - api_key: API key
        - profile: Profile name for caching
        - force_refresh: Force refresh cache
    """
    try:
        base_url = request.query.get("base_url", "https://api.openai.com/v1")
        api_key = request.query.get("api_key", "")
        profile = request.query.get("profile", "default")
        force_refresh = request.query.get("force_refresh", "false").lower() == "true"
        
        if not api_key:
            return web.json_response(
                {"success": False, "error": "API key required"},
                status=400
            )
        
        from utils.model_manager import ModelManager
        
        manager = ModelManager()
        models = manager.fetch_models(
            base_url=base_url,
            api_key=api_key,
            profile_name=profile,
            force_refresh=force_refresh,
        )
        
        return web.json_response({
            "success": True,
            "models": models,
            "count": len(models)
        })
        
    except Exception as e:
        return web.json_response(
            {"success": False, "error": str(e)},
            status=500
        )


@routes.post("/ai_customurl/test_connection")
async def test_connection(request):
    """
    Test API connection
    
    Body:
        - base_url: API base URL
        - api_key: API key
    """
    try:
        data = await request.json()
        base_url = data.get("base_url")
        api_key = data.get("api_key")
        
        if not base_url or not api_key:
            return web.json_response(
                {"success": False, "error": "base_url and api_key required"},
                status=400
            )
        
        from utils.api_client import OpenAIAPIClient
        
        client = OpenAIAPIClient(base_url, api_key, timeout=10)
        models = client.list_models()
        
        return web.json_response({
            "success": True,
            "message": f"Connected successfully. Found {len(models)} models.",
            "model_count": len(models)
        })
        
    except Exception as e:
        return web.json_response(
            {"success": False, "error": str(e)},
            status=500
        )


@routes.get("/ai_customurl/filter_models")
async def filter_models(request):
    """
    Filter models by capability
    
    Query params:
        - base_url: API base URL
        - api_key: API key
        - capability: text, image, vision, audio, video
        - profile: Profile name for caching
    """
    try:
        base_url = request.query.get("base_url", "https://api.openai.com/v1")
        api_key = request.query.get("api_key", "")
        capability = request.query.get("capability", "text")
        profile = request.query.get("profile", "default")
        
        if not api_key:
            return web.json_response(
                {"success": False, "error": "API key required"},
                status=400
            )
        
        from utils.model_manager import ModelManager
        
        manager = ModelManager()
        
        # Fetch all models
        models = manager.fetch_models(
            base_url=base_url,
            api_key=api_key,
            profile_name=profile,
        )
        
        # Filter by capability
        filtered_models = manager.get_models_by_capability(models, capability)
        
        return web.json_response({
            "success": True,
            "models": filtered_models,
            "capability": capability,
            "count": len(filtered_models)
        })
        
    except Exception as e:
        return web.json_response(
            {"success": False, "error": str(e)},
            status=500
        )


@routes.post("/ai_customurl/clear_cache")
async def clear_cache(request):
    """
    Clear model cache
    
    Body:
        - profile: Profile name (optional, clears all if not provided)
    """
    try:
        data = await request.json()
        profile = data.get("profile")
        
        from utils.model_manager import ModelManager
        
        manager = ModelManager()
        manager.clear_cache(profile)
        
        return web.json_response({
            "success": True,
            "message": f"Cache cleared for profile: {profile if profile else 'all'}"
        })
        
    except Exception as e:
        return web.json_response(
            {"success": False, "error": str(e)},
            status=500
        )


class AICustomURLExtension(ComfyExtension):
    """AI CustomURL integration for ComfyUI"""
    
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        """Return all node classes"""
        return [
            # Text nodes
            TextGenerationNode,
            TextAdvancedParamsNode,
            
            # Image nodes
            ImageGenerationNode,
            ImageAdvancedParamsNode,
            
            # Video nodes
            VideoGenerationNode,
            VideoAdvancedParamsNode,
            
            # Speech nodes
            SpeechGenerationNode,
            SpeechAdvancedParamsNode,
            
            # Utility nodes
            ImageURLLoaderNode,
            VideoURLLoaderNode,
        ]


async def comfy_entrypoint() -> AICustomURLExtension:
    """ComfyUI calls this to load the extension"""
    print("=" * 60)
    print("AI CustomURL Extension Loaded")
    print("=" * 60)
    print("Supports: Text, Image, Video, and Speech Generation")
    print("Compatible with: OpenAI, Venice.ai, OpenRouter, Together.ai, Ollama")
    print("=" * 60)
    
    return AICustomURLExtension()


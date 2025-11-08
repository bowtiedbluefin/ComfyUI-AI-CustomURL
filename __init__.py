"""
ComfyUI AI CustomURL Extension

Traditional __init__.py for backward compatibility with older ComfyUI versions.
For newer versions, see main.py with comfy_entrypoint().
"""

from .main import comfy_entrypoint

# Try to use the modern API if available
try:
    # Modern API - this will be used by newer ComfyUI versions
    __all__ = ['comfy_entrypoint']
except:
    pass

# Legacy support for older ComfyUI versions
try:
    from .nodes.text_nodes import TextGenerationNode, TextAdvancedParamsNode
    from .nodes.image_nodes import ImageGenerationNode, ImageAdvancedParamsNode
    from .nodes.video_nodes import VideoGenerationNode, VideoAdvancedParamsNode
    from .nodes.speech_nodes import SpeechGenerationNode, SpeechAdvancedParamsNode
    from .nodes.utility_nodes import ImageURLLoaderNode, VideoURLLoaderNode

    # Legacy ComfyUI expects NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS
    NODE_CLASS_MAPPINGS = {
        "TextGeneration_AICustomURL": TextGenerationNode,
        "TextAdvancedParams_AICustomURL": TextAdvancedParamsNode,
        "ImageGeneration_AICustomURL": ImageGenerationNode,
        "ImageAdvancedParams_AICustomURL": ImageAdvancedParamsNode,
        "VideoGeneration_AICustomURL": VideoGenerationNode,
        "VideoAdvancedParams_AICustomURL": VideoAdvancedParamsNode,
        "SpeechGeneration_AICustomURL": SpeechGenerationNode,
        "SpeechAdvancedParams_AICustomURL": SpeechAdvancedParamsNode,
        "ImageURLLoader_AICustomURL": ImageURLLoaderNode,
        "VideoURLLoader_AICustomURL": VideoURLLoaderNode,
    }

    NODE_DISPLAY_NAME_MAPPINGS = {
        "TextGeneration_AICustomURL": "Generate Text (AI CustomURL)",
        "TextAdvancedParams_AICustomURL": "Text Advanced Parameters",
        "ImageGeneration_AICustomURL": "Generate Image (AI CustomURL)",
        "ImageAdvancedParams_AICustomURL": "Image Advanced Parameters",
        "VideoGeneration_AICustomURL": "Generate Video (AI CustomURL)",
        "VideoAdvancedParams_AICustomURL": "Video Advanced Parameters",
        "SpeechGeneration_AICustomURL": "Generate Speech (AI CustomURL)",
        "SpeechAdvancedParams_AICustomURL": "Speech Advanced Parameters",
        "ImageURLLoader_AICustomURL": "Load Image from URL",
        "VideoURLLoader_AICustomURL": "Load Video from URL",
    }

    __all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'comfy_entrypoint']

    print("=" * 60)
    print("AI CustomURL Extension Loaded (Legacy Mode)")
    print("=" * 60)
    print("Supports: Text, Image, Video, and Speech Generation")
    print("Compatible with: OpenAI, Venice.ai, OpenRouter, Together.ai, Ollama")
    print("=" * 60)

except Exception as e:
    print(f"Error loading AI CustomURL extension: {e}")
    print("The extension requires the comfy_api.latest module.")
    print("Please update ComfyUI to a newer version that supports the modern node API.")
    
    # Provide empty mappings to prevent crashes
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}


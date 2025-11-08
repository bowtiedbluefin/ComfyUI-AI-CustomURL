"""
ComfyUI AI CustomURL Extension

Traditional ComfyUI node format for maximum compatibility.
"""

# Import all node mappings
from .nodes.text_nodes import NODE_CLASS_MAPPINGS as TEXT_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as TEXT_DISPLAY
from .nodes.image_nodes import NODE_CLASS_MAPPINGS as IMAGE_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as IMAGE_DISPLAY
from .nodes.video_nodes import NODE_CLASS_MAPPINGS as VIDEO_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as VIDEO_DISPLAY
from .nodes.speech_nodes import NODE_CLASS_MAPPINGS as SPEECH_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as SPEECH_DISPLAY
from .nodes.utility_nodes import NODE_CLASS_MAPPINGS as UTILITY_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as UTILITY_DISPLAY

# Combine all mappings
NODE_CLASS_MAPPINGS = {
    **TEXT_MAPPINGS,
    **IMAGE_MAPPINGS,
    **VIDEO_MAPPINGS,
    **SPEECH_MAPPINGS,
    **UTILITY_MAPPINGS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **TEXT_DISPLAY,
    **IMAGE_DISPLAY,
    **VIDEO_DISPLAY,
    **SPEECH_DISPLAY,
    **UTILITY_DISPLAY,
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print("=" * 60)
print("AI CustomURL Extension Loaded")
print("=" * 60)
print("Nodes: Text, Image, Video, Speech Generation + Utilities")
print("Compatible with: OpenAI, Venice.ai, OpenRouter, Together.ai, Ollama")
print("=" * 60)

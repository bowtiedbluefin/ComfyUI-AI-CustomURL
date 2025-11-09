"""ComfyUI nodes for OpenAI-compatible API integration"""

from .text_nodes import TextGenerationNode, TextAdvancedParamsNode
from .image_nodes import ImageGenerationNode, ImageAdvancedParamsNode
from .video_nodes import VideoGenerationNode, VideoAdvancedParamsNode
from .speech_nodes import SpeechGenerationNode, SpeechAdvancedParamsNode
from .utility_nodes import ImageLoaderNode, VideoLoaderNode

__all__ = [
    "TextGenerationNode",
    "TextAdvancedParamsNode",
    "ImageGenerationNode",
    "ImageAdvancedParamsNode",
    "VideoGenerationNode",
    "VideoAdvancedParamsNode",
    "SpeechGenerationNode",
    "SpeechAdvancedParamsNode",
    "ImageLoaderNode",
    "VideoLoaderNode",
]


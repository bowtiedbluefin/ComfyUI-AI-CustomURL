"""
ComfyUI AI CustomURL Extension

Traditional ComfyUI node format for maximum compatibility.
Users manually enter API URLs and model names.
"""

# Direct imports - simpler and more reliable
from .nodes.text_nodes import NODE_CLASS_MAPPINGS as TEXT_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as TEXT_DISPLAY
from .nodes.image_nodes import NODE_CLASS_MAPPINGS as IMAGE_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as IMAGE_DISPLAY
from .nodes.video_nodes import NODE_CLASS_MAPPINGS as VIDEO_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as VIDEO_DISPLAY
from .nodes.speech_nodes import NODE_CLASS_MAPPINGS as SPEECH_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as SPEECH_DISPLAY
from .nodes.utility_nodes import NODE_CLASS_MAPPINGS as UTILITY_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as UTILITY_DISPLAY

NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(TEXT_MAPPINGS)
NODE_CLASS_MAPPINGS.update(IMAGE_MAPPINGS)
NODE_CLASS_MAPPINGS.update(VIDEO_MAPPINGS)
NODE_CLASS_MAPPINGS.update(SPEECH_MAPPINGS)
NODE_CLASS_MAPPINGS.update(UTILITY_MAPPINGS)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(TEXT_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(IMAGE_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(VIDEO_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(SPEECH_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(UTILITY_DISPLAY)

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

print("=" * 60)
print(f"AI CustomURL Extension Loaded: {len(NODE_CLASS_MAPPINGS)} total nodes")
print("=" * 60)
if NODE_CLASS_MAPPINGS:
    print("Available nodes:")
    for node_id in sorted(NODE_CLASS_MAPPINGS.keys()):
        print(f"  - {node_id}")
    print("=" * 60)
else:
    print("WARNING: No nodes were loaded!")
    print("=" * 60)

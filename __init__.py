"""
ComfyUI AI CustomURL Extension

Traditional ComfyUI node format for maximum compatibility.
Users manually enter API URLs and model names.
"""

import traceback
import os

# Initialize empty mappings
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Set the web directory for JavaScript extensions
WEB_DIRECTORY = os.path.join(os.path.dirname(__file__), "web")

try:
    # Import all node mappings
    from .nodes.text_nodes import NODE_CLASS_MAPPINGS as TEXT_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as TEXT_DISPLAY
    NODE_CLASS_MAPPINGS.update(TEXT_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(TEXT_DISPLAY)
    print(f"[AI CustomURL] Loaded {len(TEXT_MAPPINGS)} text nodes")
except Exception as e:
    print(f"[AI CustomURL] ERROR loading text_nodes: {e}")
    traceback.print_exc()

try:
    from .nodes.image_nodes import NODE_CLASS_MAPPINGS as IMAGE_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as IMAGE_DISPLAY
    NODE_CLASS_MAPPINGS.update(IMAGE_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(IMAGE_DISPLAY)
    print(f"[AI CustomURL] Loaded {len(IMAGE_MAPPINGS)} image nodes")
except Exception as e:
    print(f"[AI CustomURL] ERROR loading image_nodes: {e}")
    traceback.print_exc()

try:
    from .nodes.video_nodes import NODE_CLASS_MAPPINGS as VIDEO_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as VIDEO_DISPLAY
    NODE_CLASS_MAPPINGS.update(VIDEO_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(VIDEO_DISPLAY)
    print(f"[AI CustomURL] Loaded {len(VIDEO_MAPPINGS)} video nodes")
except Exception as e:
    print(f"[AI CustomURL] ERROR loading video_nodes: {e}")
    traceback.print_exc()

try:
    from .nodes.speech_nodes import NODE_CLASS_MAPPINGS as SPEECH_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as SPEECH_DISPLAY
    NODE_CLASS_MAPPINGS.update(SPEECH_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(SPEECH_DISPLAY)
    print(f"[AI CustomURL] Loaded {len(SPEECH_MAPPINGS)} speech nodes")
except Exception as e:
    print(f"[AI CustomURL] ERROR loading speech_nodes: {e}")
    traceback.print_exc()

try:
    from .nodes.utility_nodes import NODE_CLASS_MAPPINGS as UTILITY_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as UTILITY_DISPLAY
    NODE_CLASS_MAPPINGS.update(UTILITY_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(UTILITY_DISPLAY)
    print(f"[AI CustomURL] Loaded {len(UTILITY_MAPPINGS)} utility nodes")
except Exception as e:
    print(f"[AI CustomURL] ERROR loading utility_nodes: {e}")
    traceback.print_exc()

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

print("=" * 60)
print(f"AI CustomURL Extension Loaded: {len(NODE_CLASS_MAPPINGS)} total nodes")
print("=" * 60)
if NODE_CLASS_MAPPINGS:
    print("Available nodes:")
    for node_id in NODE_CLASS_MAPPINGS.keys():
        print(f"  - {node_id}")
    print("=" * 60)
else:
    print("WARNING: No nodes were loaded! Check errors above.")
    print("=" * 60)

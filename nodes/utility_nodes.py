"""Utility nodes for URL loading and data conversion"""

import torch
import os
import requests
import tempfile
import shutil
from datetime import datetime


class ImageLoaderNode:
    """
    Load image from URL
    
    For file uploads, use ComfyUI's built-in 'Load Image' node (it has proper file picker)
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "load_image"
    CATEGORY = "ai_customurl"
    
    def load_image(self, url):
        """Load image from URL"""
        
        from ..utils.converters import url_to_tensor, create_blank_tensor
        
        try:
            if not url:
                print("[WARNING] No URL provided")
                blank = create_blank_tensor()
                return (blank,)
            
            image = url_to_tensor(url)
            print(f"[INFO] Loaded image from URL: {url}")
            return (image,)
            
        except Exception as e:
            error_msg = f"Failed to load image: {str(e)}"
            print(error_msg)
            blank = create_blank_tensor()
            return (blank,)


class VideoLoaderNode:
    """
    Load video from URL and convert to image frames
    
    For file uploads, use ComfyUI's built-in video nodes
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
                "start_frame": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 10000,
                }),
                "frame_count": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 10000,
                }),
                "skip_frames": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 100,
                }),
                "resize_mode": (["none", "fit", "fill"], {
                    "default": "none",
                }),
                "target_width": ("INT", {
                    "default": 512,
                    "min": 64,
                    "max": 4096,
                    "step": 64,
                }),
                "target_height": ("INT", {
                    "default": 512,
                    "min": 64,
                    "max": 4096,
                    "step": 64,
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("frames", "info")
    FUNCTION = "load_video"
    CATEGORY = "ai_customurl"
    
    def load_video(
        self,
        url,
        start_frame,
        frame_count,
        skip_frames,
        resize_mode,
        target_width,
        target_height,
    ):
        """Load video from URL"""
        
        import tempfile
        import os
        import requests
        import cv2
        from ..utils.converters import create_blank_tensor
        
        try:
            if not url:
                print("[WARNING] No URL provided")
                blank = create_blank_tensor()
                return (blank, "No URL provided")
            
            # Download video to temporary file
            print(f"[INFO] Downloading video from URL: {url}")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                response = requests.get(url, stream=True, timeout=60)
                response.raise_for_status()
                
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                
                temp_file_path = temp_file.name
            
            # Load video using OpenCV
            cap = cv2.VideoCapture(temp_file_path)
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Calculate frames to load
            end_frame = total_frames if frame_count == 0 else min(start_frame + frame_count, total_frames)
            
            frames = []
            frame_idx = 0
            loaded_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Skip until start_frame
                if frame_idx < start_frame:
                    frame_idx += 1
                    continue
                
                # Stop if reached end
                if frame_idx >= end_frame:
                    break
                
                # Skip frames based on skip_frames parameter
                if (frame_idx - start_frame) % skip_frames != 0:
                    frame_idx += 1
                    continue
                
                # Resize if needed
                if resize_mode != "none":
                    if resize_mode == "fit":
                        # Maintain aspect ratio
                        aspect = width / height
                        target_aspect = target_width / target_height
                        
                        if aspect > target_aspect:
                            new_width = target_width
                            new_height = int(target_width / aspect)
                        else:
                            new_height = target_height
                            new_width = int(target_height * aspect)
                    else:  # fill
                        new_width = target_width
                        new_height = target_height
                    
                    frame = cv2.resize(frame, (new_width, new_height))
                
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to tensor
                frame_tensor = torch.from_numpy(frame).float() / 255.0
                frames.append(frame_tensor)
                
                loaded_count += 1
                frame_idx += 1
            
            cap.release()
            os.unlink(temp_file_path)
            
            if frames:
                # Stack frames
                frames_tensor = torch.stack(frames)
                info = f"Loaded {loaded_count} frames from video ({width}x{height} @ {fps}fps)"
                return (frames_tensor, info)
            else:
                blank = create_blank_tensor()
                return (blank, "No frames loaded")
            
        except Exception as e:
            error_msg = f"Failed to load video: {str(e)}"
            print(error_msg)
            blank = create_blank_tensor()
            return (blank, error_msg)


class SaveVideoNode:
    """
    Download and save video from URL to local filesystem
    
    Supports both public URLs and authenticated endpoints (like OpenAI)
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
                "filename": ("STRING", {
                    "default": "video_{timestamp}",
                    "multiline": False,
                }),
                "output_folder": ("STRING", {
                    "default": "output/videos",
                    "multiline": False,
                }),
            },
            "optional": {
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("filepath", "status")
    FUNCTION = "save_video"
    CATEGORY = "ai_customurl"
    OUTPUT_NODE = True
    
    def save_video(self, video_url, filename, output_folder, api_key=""):
        """Download and save video from URL"""
        
        try:
            # Check if URL is valid before trying to download
            if not video_url or not video_url.startswith(("http://", "https://")):
                print(f"[WARNING] Save Video: Invalid or empty URL, skipping")
                return ("", "No valid video URL to save")
            
            # Replace {timestamp} placeholder
            if "{timestamp}" in filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = filename.replace("{timestamp}", timestamp)
            
            # Ensure filename has extension
            if not filename.endswith((".mp4", ".webm", ".mov", ".avi")):
                filename += ".mp4"
            
            # Create output directory if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)
            
            # Full output path
            output_path = os.path.join(output_folder, filename)
            
            # Download video
            print(f"Downloading video from: {video_url}")
            
            # Setup headers for authenticated requests (e.g., OpenAI)
            headers = {}
            if api_key and ("openai.com" in video_url or "api.openai" in video_url):
                headers["Authorization"] = f"Bearer {api_key}"
                print(f"[INFO] Using authenticated download")
            
            response = requests.get(video_url, headers=headers, stream=True, timeout=300)
            response.raise_for_status()
            
            # Save to file
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Get file size
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            
            success_msg = f"Video saved successfully: {output_path} ({file_size_mb:.2f} MB)"
            print(success_msg)
            
            return (output_path, success_msg)
            
        except Exception as e:
            error_msg = f"Failed to save video: {str(e)}"
            print(error_msg)
            return ("", error_msg)


class ShowTextNode:
    """
    Display text in ComfyUI interface
    
    Connect any STRING output to this node to display it
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "forceInput": True,
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "show_text"
    CATEGORY = "ai_customurl"
    OUTPUT_NODE = True
    
    def show_text(self, text):
        """Display text in UI and pass it through"""
        # Handle empty text gracefully
        display_text = text if text and text.strip() else "(empty)"
        print(f"[SHOW TEXT] {display_text}")

        # Return UI data for ComfyUI display and pass through result
        return {"ui": {"text": display_text}, "result": (text,)}


NODE_CLASS_MAPPINGS = {
    "ImageLoader_AICustomURL": ImageLoaderNode,
    "VideoLoader_AICustomURL": VideoLoaderNode,
    "SaveVideo_AICustomURL": SaveVideoNode,
    "ShowText_AICustomURL": ShowTextNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageLoader_AICustomURL": "Load Image (AI CustomURL)",
    "VideoLoader_AICustomURL": "Load Video (AI CustomURL)",
    "SaveVideo_AICustomURL": "Save Video from URL",
    "ShowText_AICustomURL": "Show Text (AI CustomURL)",
}

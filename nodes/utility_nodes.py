"""Utility nodes for URL loading and data conversion"""

import torch
import os
import requests
import tempfile
import shutil
from datetime import datetime


class ImageLoaderNode:
    """
    Load image from URL or file upload
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        import folder_paths
        return {
            "required": {
                "mode": (["url", "file"], {
                    "default": "url",
                }),
                "url": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
                "image_file": (sorted(folder_paths.get_filename_list("input")), {
                    "image_upload": True
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "status")
    FUNCTION = "load_image"
    CATEGORY = "ai_customurl"
    
    def load_image(self, mode, url, image_file):
        """Load image from URL or uploaded file"""
        
        from ..utils.converters import url_to_tensor, create_blank_tensor
        import folder_paths
        from PIL import Image
        import numpy as np
        
        try:
            if mode == "file" and image_file:
                # Load from ComfyUI input folder
                image_path = folder_paths.get_annotated_filepath(image_file)
                img = Image.open(image_path)
                img = img.convert("RGB")
                image_np = np.array(img).astype(np.float32) / 255.0
                image_tensor = torch.from_numpy(image_np)[None,]
                return (image_tensor, f"Loaded image from file: {image_file}")
            elif mode == "url" and url:
                loaded_image = url_to_tensor(url)
                return (loaded_image, f"Loaded image from URL: {url}")
            else:
                error_msg = "No image source provided"
                print(error_msg)
                blank = create_blank_tensor()
                return (blank, error_msg)
            
        except Exception as e:
            error_msg = f"Failed to load image: {str(e)}"
            print(error_msg)
            blank = create_blank_tensor()
            return (blank, error_msg)


class VideoLoaderNode:
    """
    Load video from URL or file and convert to image frames
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        import folder_paths
        return {
            "required": {
                "mode": (["url", "file"], {
                    "default": "url",
                }),
                "url": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
                "video_file": (sorted(folder_paths.get_filename_list("input")), {
                    "video_upload": True
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
        mode,
        url,
        video_file,
        start_frame,
        frame_count,
        skip_frames,
        resize_mode,
        target_width,
        target_height,
    ):
        """Load video from URL or file"""
        
        import tempfile
        import os
        import requests
        import cv2
        import folder_paths
        from ..utils.converters import create_blank_tensor
        
        try:
            # Get video file path
            if mode == "file" and video_file:
                # Load from ComfyUI input folder
                temp_file_path = folder_paths.get_annotated_filepath(video_file)
            elif mode == "url" and url:
                # Download video to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                    response = requests.get(url, stream=True, timeout=60)
                    response.raise_for_status()
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        temp_file.write(chunk)
                    
                    temp_file_path = temp_file.name
            else:
                error_msg = "No video source provided"
                print(error_msg)
                blank = create_blank_tensor()
                return (blank, error_msg)
            
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
            # Only delete temp file if we downloaded it
            if mode == "url":
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
            if not video_url or video_url.startswith("error:"):
                return ("", f"Invalid video URL: {video_url}")
            
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


NODE_CLASS_MAPPINGS = {
    "ImageLoader_AICustomURL": ImageLoaderNode,
    "VideoLoader_AICustomURL": VideoLoaderNode,
    "SaveVideo_AICustomURL": SaveVideoNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageLoader_AICustomURL": "Load Image (AI CustomURL)",
    "VideoLoader_AICustomURL": "Load Video (AI CustomURL)",
    "SaveVideo_AICustomURL": "Save Video from URL",
}

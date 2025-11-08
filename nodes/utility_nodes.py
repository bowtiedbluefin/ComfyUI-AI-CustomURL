"""Utility nodes for URL loading and data conversion"""

import torch
from comfy_api.latest import io


class ImageURLLoaderNode(io.ComfyNode):
    """
    Load image from URL
    """
    
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ImageURLLoader_AICustomURL",
            display_name="Load Image from URL",
            category="AI_CustomURL/Utility",
            inputs=[
                io.String.Input(
                    "url",
                    default="",
                    multiline=False,
                ),
            ],
            outputs=[
                io.Image.Output("image"),
                io.String.Output("status"),
            ],
        )
    
    @classmethod
    def execute(cls, url: str) -> io.NodeOutput:
        """Load image from URL"""
        
        from utils.converters import url_to_tensor, create_blank_tensor
        
        try:
            image = url_to_tensor(url)
            return io.NodeOutput(image, f"Loaded image from {url}")
            
        except Exception as e:
            error_msg = f"Failed to load image: {str(e)}"
            print(error_msg)
            blank = create_blank_tensor()
            return io.NodeOutput(blank, error_msg)


class VideoURLLoaderNode(io.ComfyNode):
    """
    Load video from URL and convert to image frames
    """
    
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="VideoURLLoader_AICustomURL",
            display_name="Load Video from URL",
            category="AI_CustomURL/Utility",
            inputs=[
                io.String.Input(
                    "url",
                    default="",
                    multiline=False,
                ),
                io.Int.Input(
                    "start_frame",
                    default=0,
                    min=0,
                    max=10000,
                ),
                io.Int.Input(
                    "frame_count",
                    default=0,
                    min=0,
                    max=10000,
                ),
                io.Int.Input(
                    "skip_frames",
                    default=1,
                    min=1,
                    max=100,
                ),
                io.Combo.Input(
                    "resize_mode",
                    options=["none", "fit", "fill"],
                ),
                io.Int.Input(
                    "target_width",
                    default=512,
                    min=64,
                    max=4096,
                    step=64,
                ),
                io.Int.Input(
                    "target_height",
                    default=512,
                    min=64,
                    max=4096,
                    step=64,
                ),
            ],
            outputs=[
                io.Image.Output("frames"),
                io.String.Output("info"),
            ],
        )
    
    @classmethod
    def execute(
        cls,
        url: str,
        start_frame: int,
        frame_count: int,
        skip_frames: int,
        resize_mode: str,
        target_width: int,
        target_height: int,
    ) -> io.NodeOutput:
        """Load video from URL"""
        
        import tempfile
        import os
        import requests
        import cv2
        from utils.converters import create_blank_tensor
        
        try:
            # Download video to temporary file
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
                return io.NodeOutput(frames_tensor, info)
            else:
                blank = create_blank_tensor()
                return io.NodeOutput(blank, "No frames loaded")
            
        except Exception as e:
            error_msg = f"Failed to load video: {str(e)}"
            print(error_msg)
            blank = create_blank_tensor()
            return io.NodeOutput(blank, error_msg)


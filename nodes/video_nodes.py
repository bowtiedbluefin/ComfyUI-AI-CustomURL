"""Video generation nodes for AI CustomURL"""

import json
from typing import Optional
from comfy_api.latest import io


class VideoGenerationNode(io.ComfyNode):
    """
    Generate videos using OpenAI-compatible video generation API
    
    Supports: OpenAI Sora (/videos/create endpoint) and compatible APIs
    """
    
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="VideoGeneration_AICustomURL",
            display_name="Generate Video (AI CustomURL)",
            category="AI_CustomURL/Video",
            inputs=[
                # API Configuration
                io.String.Input(
                    "base_url",
                    default="https://api.openai.com/v1",
                    multiline=False,
                ),
                io.String.Input(
                    "api_key",
                    default="",
                    multiline=False,
                ),
                
                # Required Parameters (OpenAI spec)
                io.String.Input(
                    "model",
                    default="sora-1.0",
                    multiline=False,
                ),
                io.String.Input(
                    "prompt",
                    default="",
                    multiline=True,
                ),
                
                # Optional Parameters
                io.Combo.Input(
                    "resolution",
                    options=["1080p", "720p", "480p"],
                ),
                io.Int.Input(
                    "duration",
                    default=5,
                    min=1,
                    max=60,
                ),
                io.Int.Input(
                    "fps",
                    default=24,
                    min=1,
                    max=60,
                ),
                io.Combo.Input(
                    "aspect_ratio",
                    options=["16:9", "9:16", "1:1", "4:3", "21:9"],
                ),
                
                # Optional Image Input (for image-to-video)
                io.Image.Input("image", optional=True),
                
                # Advanced parameters (custom JSON)
                io.String.Input(
                    "advanced_params_json",
                    default="",
                    multiline=False,
                    optional=True,
                ),
            ],
            outputs=[
                io.String.Output("video_url"),
                io.String.Output("response_json"),
            ],
        )
    
    @classmethod
    def execute(
        cls,
        base_url: str,
        api_key: str,
        model: str,
        prompt: str,
        resolution: str,
        duration: int,
        fps: int,
        aspect_ratio: str,
        image: Optional[object] = None,
        advanced_params_json: str = "",
    ) -> io.NodeOutput:
        """Execute video generation"""
        
        from utils.api_client import OpenAIAPIClient
        from utils.converters import image_to_base64
        
        try:
            client = OpenAIAPIClient(base_url, api_key)
            
            # Build parameters
            params = {
                "resolution": resolution,
                "duration": duration,
                "fps": fps,
                "aspect_ratio": aspect_ratio,
            }
            
            # Add image for image-to-video if provided
            if image is not None:
                # Convert image to base64 data URL
                base64_img = image_to_base64(image)
                params["image_url"] = f"data:image/png;base64,{base64_img}"
            
            # Merge advanced parameters if provided
            if advanced_params_json:
                try:
                    advanced_params = json.loads(advanced_params_json)
                    params.update(advanced_params)
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse advanced_params_json: {e}")
            
            # Make API call
            response = client.generate_video(
                model=model,
                prompt=prompt,
                **params
            )
            
            # Extract video URL from response
            video_url = ""
            if "video" in response:
                video_url = response["video"].get("url", "")
            elif "data" in response and len(response["data"]) > 0:
                video_url = response["data"][0].get("url", "")
            
            response_json = json.dumps(response, indent=2)
            
            if not video_url:
                print("Warning: No video URL found in response")
                video_url = "error: no video URL in response"
            
            return io.NodeOutput(video_url, response_json)
            
        except Exception as e:
            error_msg = f"Video generation failed: {str(e)}"
            print(error_msg)
            return io.NodeOutput(error_msg, str(e))


class VideoAdvancedParamsNode(io.ComfyNode):
    """
    Advanced parameters for video generation
    
    Includes both standard and extended parameters
    """
    
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="VideoAdvancedParams_AICustomURL",
            display_name="Video Advanced Parameters",
            category="AI_CustomURL/Video",
            inputs=[
                # Seed for reproducibility
                io.Int.Input(
                    "seed",
                    default=-1,
                    min=-1,
                    max=2147483647,
                ),
                
                # Motion strength (some APIs)
                io.Float.Input(
                    "motion_strength",
                    default=1.0,
                    min=0.0,
                    max=2.0,
                    step=0.1,
                ),
                
                # Camera motion
                io.Combo.Input(
                    "camera_motion",
                    options=["none", "static", "pan_left", "pan_right", "zoom_in", "zoom_out", "rotate"],
                ),
                
                # Loop video
                io.Combo.Input(
                    "loop",
                    options=["false", "true"],
                ),
                
                # End frame (for first-to-last interpolation)
                io.Image.Input("end_image", optional=True),
                
                # Upscale output
                io.Combo.Input(
                    "upscale",
                    options=["false", "true"],
                ),
                
                # Negative prompt (some APIs)
                io.String.Input(
                    "negative_prompt",
                    default="",
                    multiline=True,
                ),
                
                # CFG scale (some APIs)
                io.Float.Input(
                    "guidance_scale",
                    default=7.5,
                    min=1.0,
                    max=20.0,
                    step=0.5,
                ),
                
                # Number of inference steps (some APIs)
                io.Int.Input(
                    "steps",
                    default=50,
                    min=1,
                    max=150,
                ),
            ],
            outputs=[
                io.String.Output("params_json"),
            ],
        )
    
    @classmethod
    def execute(
        cls,
        seed: int,
        motion_strength: float,
        camera_motion: str,
        loop: str,
        end_image: Optional[object],
        upscale: str,
        negative_prompt: str,
        guidance_scale: float,
        steps: int,
    ) -> io.NodeOutput:
        """Build advanced parameters object"""
        
        from utils.converters import image_to_base64
        
        params = {}
        
        # Add seed if specified
        if seed >= 0:
            params["seed"] = seed
        
        # Add motion strength if not default
        if motion_strength != 1.0:
            params["motion_strength"] = motion_strength
        
        # Add camera motion if specified
        if camera_motion != "none":
            params["camera_motion"] = camera_motion
        
        # Add loop if enabled
        if loop == "true":
            params["loop"] = True
        
        # Add end image if provided
        if end_image is not None:
            base64_img = image_to_base64(end_image)
            params["end_image_url"] = f"data:image/png;base64,{base64_img}"
        
        # Add upscale if enabled
        if upscale == "true":
            params["upscale"] = True
        
        # Add negative prompt if provided
        if negative_prompt:
            params["negative_prompt"] = negative_prompt
        
        # Add guidance scale if not default
        if guidance_scale != 7.5:
            params["guidance_scale"] = guidance_scale
            params["cfg_scale"] = guidance_scale  # Alternative name
        
        # Add steps if not default
        if steps != 50:
            params["steps"] = steps
            params["num_inference_steps"] = steps  # Alternative name
        
        return io.NodeOutput(json.dumps(params))


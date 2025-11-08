"""Video generation nodes for AI CustomURL"""

import json


class VideoGenerationNode:
    """
    Generate videos using OpenAI-compatible video generation API
    
    Supports: OpenAI Sora (/videos/create endpoint) and compatible APIs
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_url": ("STRING", {
                    "default": "https://api.openai.com/v1",
                    "multiline": False,
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
                "model": ("STRING", {
                    "default": "sora-1.0",
                    "multiline": False,
                }),
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "resolution": (["1080p", "720p", "480p"], {
                    "default": "1080p",
                }),
                "duration": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 60,
                }),
                "fps": ("INT", {
                    "default": 24,
                    "min": 1,
                    "max": 60,
                }),
                "aspect_ratio": (["16:9", "9:16", "1:1", "4:3", "21:9"], {
                    "default": "16:9",
                }),
            },
            "optional": {
                "image": ("IMAGE",),
                "advanced_params_json": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "response_json")
    FUNCTION = "generate_video"
    CATEGORY = "ai_customurl"
    
    def generate_video(
        self,
        base_url,
        api_key,
        model,
        prompt,
        resolution,
        duration,
        fps,
        aspect_ratio,
        image=None,
        advanced_params_json="",
    ):
        """Execute video generation"""
        
        from ..utils.api_client import OpenAIAPIClient
        from ..utils.converters import image_to_base64
        
        try:
            client = OpenAIAPIClient(base_url, api_key)
            
            # Convert parameters to OpenAI format
            # Map resolution + aspect_ratio to OpenAI's "size" parameter
            size_mapping = {
                ("1080p", "16:9"): "1920x1080",
                ("1080p", "9:16"): "1080x1920",
                ("1080p", "1:1"): "1080x1080",
                ("1080p", "4:3"): "1440x1080",
                ("1080p", "21:9"): "2560x1080",
                ("720p", "16:9"): "1280x720",
                ("720p", "9:16"): "720x1280",
                ("720p", "1:1"): "720x720",
                ("720p", "4:3"): "960x720",
                ("720p", "21:9"): "1680x720",
                ("480p", "16:9"): "854x480",
                ("480p", "9:16"): "480x854",
                ("480p", "1:1"): "480x480",
                ("480p", "4:3"): "640x480",
                ("480p", "21:9"): "1120x480",
            }
            
            # Build parameters in OpenAI format
            params = {
                "size": size_mapping.get((resolution, aspect_ratio), "1920x1080"),
                "seconds": duration,  # OpenAI expects integer like 5
            }
            
            # Note: OpenAI doesn't support fps directly, but keep for other APIs
            # Only add if specified in advanced params or if not using OpenAI
            if "openai.com" not in base_url:
                params["fps"] = fps
                params["resolution"] = resolution
                params["aspect_ratio"] = aspect_ratio
            
            # Add image for image-to-video if provided
            if image is not None:
                # Convert image to base64 data URL
                base64_img = image_to_base64(image)
                # OpenAI uses "input_reference" for image-to-video
                if "openai.com" in base_url:
                    params["input_reference"] = f"data:image/png;base64,{base64_img}"
                else:
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
            
            return (video_url, response_json)
            
        except Exception as e:
            error_msg = f"Video generation failed: {str(e)}"
            print(error_msg)
            return (error_msg, str(e))


class VideoAdvancedParamsNode:
    """
    Advanced parameters for video generation
    
    Includes both standard and extended parameters
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647,
                }),
                "motion_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                }),
                "camera_motion": (["none", "static", "pan_left", "pan_right", "zoom_in", "zoom_out", "rotate"], {
                    "default": "none",
                }),
                "loop": (["false", "true"], {
                    "default": "false",
                }),
                "upscale": (["false", "true"], {
                    "default": "false",
                }),
                "negative_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "guidance_scale": ("FLOAT", {
                    "default": 7.5,
                    "min": 1.0,
                    "max": 20.0,
                    "step": 0.5,
                }),
                "steps": ("INT", {
                    "default": 50,
                    "min": 1,
                    "max": 150,
                }),
            },
            "optional": {
                "end_image": ("IMAGE",),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("params_json",)
    FUNCTION = "generate_params"
    CATEGORY = "ai_customurl"
    
    def generate_params(
        self,
        seed,
        motion_strength,
        camera_motion,
        loop,
        upscale,
        negative_prompt,
        guidance_scale,
        steps,
        end_image=None,
    ):
        """Build advanced parameters object"""
        
        from ..utils.converters import image_to_base64
        
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
        
        return (json.dumps(params),)


NODE_CLASS_MAPPINGS = {
    "VideoGeneration_AICustomURL": VideoGenerationNode,
    "VideoAdvancedParams_AICustomURL": VideoAdvancedParamsNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoGeneration_AICustomURL": "Generate Video (AI CustomURL)",
    "VideoAdvancedParams_AICustomURL": "Video Advanced Parameters",
}

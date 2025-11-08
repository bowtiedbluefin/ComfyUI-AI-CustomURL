"""Image generation nodes for AI CustomURL"""

import json
import torch


class ImageGenerationNode:
    """
    Generate images using OpenAI-compatible image generation API
    
    Supports: OpenAI DALL-E, Venice.ai, and other compatible APIs
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
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "model": ("STRING", {
                    "default": "dall-e-3",
                    "multiline": False,
                }),
                "n": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 10,
                }),
                "size": (["1024x1024", "1024x1792", "1792x1024", "512x512", "256x256"], {
                    "default": "1024x1024",
                }),
                "quality": (["standard", "hd"], {
                    "default": "standard",
                }),
                "style": (["vivid", "natural"], {
                    "default": "vivid",
                }),
                "response_format": (["url", "b64_json"], {
                    "default": "url",
                }),
            },
            "optional": {
                "advanced_params_json": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "urls")
    FUNCTION = "generate_image"
    CATEGORY = "ai_customurl"
    
    def generate_image(
        self,
        base_url,
        api_key,
        prompt,
        model,
        n,
        size,
        quality,
        style,
        response_format,
        advanced_params_json="",
    ):
        """Execute image generation"""
        
        from ..utils.api_client import OpenAIAPIClient
        from ..utils.converters import url_to_tensor, base64_to_tensor, create_blank_tensor
        
        try:
            client = OpenAIAPIClient(base_url, api_key)
            
            # Build parameters
            params = {
                "n": n,
                "size": size,
                "response_format": response_format,
            }
            
            # Add optional parameters if not default
            if quality != "standard":
                params["quality"] = quality
            
            if style != "vivid":
                params["style"] = style
            
            # Merge advanced parameters if provided
            if advanced_params_json:
                try:
                    advanced_params = json.loads(advanced_params_json)
                    params.update(advanced_params)
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse advanced_params_json: {e}")
            
            # Make API call
            response = client.generate_image(
                model=model,
                prompt=prompt,
                **params
            )
            
            # Process images
            images = []
            urls = []
            
            for img_data in response.get("data", []):
                if "url" in img_data:
                    # Download from URL
                    tensor = url_to_tensor(img_data["url"])
                    urls.append(img_data["url"])
                elif "b64_json" in img_data:
                    # Decode base64
                    tensor = base64_to_tensor(img_data["b64_json"])
                    urls.append("base64_encoded")
                else:
                    continue
                
                images.append(tensor)
            
            # Stack images into batch
            if images:
                image_batch = torch.cat(images, dim=0)
            else:
                image_batch = create_blank_tensor()
                urls.append("error: no images generated")
            
            urls_string = "\n".join(urls)
            
            return (image_batch, urls_string)
            
        except Exception as e:
            error_msg = f"Image generation failed: {str(e)}"
            print(error_msg)
            # Return blank image on error
            blank = create_blank_tensor()
            return (blank, error_msg)


class ImageAdvancedParamsNode:
    """
    Advanced parameters for image generation
    
    Includes both OpenAI standard params and common extensions
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {
                    "default": 1024,
                    "min": 256,
                    "max": 2048,
                    "step": 64,
                }),
                "height": ("INT", {
                    "default": 1024,
                    "min": 256,
                    "max": 2048,
                    "step": 64,
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
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647,
                }),
                "sampler": (["none", "euler", "euler_a", "ddim", "ddpm", "dpm++"], {
                    "default": "none",
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("params_json",)
    FUNCTION = "generate_params"
    CATEGORY = "ai_customurl"
    
    def generate_params(
        self,
        width,
        height,
        negative_prompt,
        guidance_scale,
        steps,
        seed,
        sampler,
    ):
        """Build advanced parameters object"""
        
        params = {}
        
        # Add custom dimensions
        if width != 1024 or height != 1024:
            params["width"] = width
            params["height"] = height
        
        # Add negative prompt if provided
        if negative_prompt:
            params["negative_prompt"] = negative_prompt
        
        # Add guidance scale if not default
        if guidance_scale != 7.5:
            params["guidance_scale"] = guidance_scale
            params["cfg_scale"] = guidance_scale  # Alternative name some APIs use
        
        # Add steps if not default
        if steps != 50:
            params["steps"] = steps
            params["num_inference_steps"] = steps  # Alternative name
        
        # Add seed if specified
        if seed >= 0:
            params["seed"] = seed
        
        # Add sampler if specified
        if sampler != "none":
            params["sampler"] = sampler
            params["scheduler"] = sampler  # Alternative name
        
        return (json.dumps(params),)


NODE_CLASS_MAPPINGS = {
    "ImageGeneration_AICustomURL": ImageGenerationNode,
    "ImageAdvancedParams_AICustomURL": ImageAdvancedParamsNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageGeneration_AICustomURL": "Generate Image (AI CustomURL)",
    "ImageAdvancedParams_AICustomURL": "Image Advanced Parameters",
}

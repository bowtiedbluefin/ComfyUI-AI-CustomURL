"""Image generation nodes for AI CustomURL"""

import json
from typing import Optional
import torch
from comfy_api.latest import io


class ImageGenerationNode(io.ComfyNode):
    """
    Generate images using OpenAI-compatible image generation API
    
    Supports: OpenAI DALL-E, Venice.ai, and other compatible APIs
    """
    
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ImageGeneration_AICustomURL",
            display_name="Generate Image (AI CustomURL)",
            category="AI_CustomURL/Image",
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
                    "prompt",
                    default="",
                    multiline=True,
                ),
                
                # Optional Parameters
                io.String.Input(
                    "model",
                    default="dall-e-3",
                    multiline=False,
                ),
                io.Int.Input(
                    "n",
                    default=1,
                    min=1,
                    max=10,
                ),
                io.Combo.Input(
                    "size",
                    options=["1024x1024", "1024x1792", "1792x1024", "512x512", "256x256"],
                ),
                io.Combo.Input(
                    "quality",
                    options=["standard", "hd"],
                ),
                io.Combo.Input(
                    "style",
                    options=["vivid", "natural"],
                ),
                io.Combo.Input(
                    "response_format",
                    options=["url", "b64_json"],
                ),
                
                # Advanced parameters (custom JSON)
                io.String.Input(
                    "advanced_params_json",
                    default="",
                    multiline=False,
                    optional=True,
                ),
            ],
            outputs=[
                io.Image.Output("images"),
                io.String.Output("urls"),
            ],
        )
    
    @classmethod
    def execute(
        cls,
        base_url: str,
        api_key: str,
        prompt: str,
        model: str,
        n: int,
        size: str,
        quality: str,
        style: str,
        response_format: str,
        advanced_params_json: str = "",
    ) -> io.NodeOutput:
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
            
            return io.NodeOutput(image_batch, urls_string)
            
        except Exception as e:
            error_msg = f"Image generation failed: {str(e)}"
            print(error_msg)
            # Return blank image on error
            blank = create_blank_tensor()
            return io.NodeOutput(blank, error_msg)


class ImageAdvancedParamsNode(io.ComfyNode):
    """
    Advanced parameters for image generation
    
    Includes both OpenAI standard params and common extensions
    """
    
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="ImageAdvancedParams_AICustomURL",
            display_name="Image Advanced Parameters",
            category="AI_CustomURL/Image",
            inputs=[
                # Custom width/height (some APIs support this)
                io.Int.Input(
                    "width",
                    default=1024,
                    min=256,
                    max=2048,
                    step=64,
                ),
                io.Int.Input(
                    "height",
                    default=1024,
                    min=256,
                    max=2048,
                    step=64,
                ),
                
                # Common extensions (not in OpenAI spec but supported by many APIs)
                io.String.Input(
                    "negative_prompt",
                    default="",
                    multiline=True,
                ),
                io.Float.Input(
                    "guidance_scale",
                    default=7.5,
                    min=1.0,
                    max=20.0,
                    step=0.5,
                ),
                io.Int.Input(
                    "steps",
                    default=50,
                    min=1,
                    max=150,
                ),
                io.Int.Input(
                    "seed",
                    default=-1,
                    min=-1,
                    max=2147483647,
                ),
                io.Combo.Input(
                    "sampler",
                    options=["none", "euler", "euler_a", "ddim", "ddpm", "dpm++"],
                ),
            ],
            outputs=[
                io.String.Output("params_json"),
            ],
        )
    
    @classmethod
    def execute(
        cls,
        width: int,
        height: int,
        negative_prompt: str,
        guidance_scale: float,
        steps: int,
        seed: int,
        sampler: str,
    ) -> io.NodeOutput:
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
        
        return io.NodeOutput(json.dumps(params))


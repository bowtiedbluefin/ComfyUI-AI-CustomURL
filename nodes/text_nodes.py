"""Text generation nodes for AI CustomURL"""

import json
from typing import Optional


class TextGenerationNode:
    """
    Generate text using OpenAI-compatible chat completion API
    
    Supports: OpenAI, Venice.ai, OpenRouter, Together.ai, Ollama, etc.
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
                    "default": "gpt-4o",
                    "multiline": False,
                }),
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "temperature": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                }),
                "max_tokens": ("INT", {
                    "default": 1024,
                    "min": 1,
                    "max": 128000,
                    "step": 1,
                }),
            },
            "optional": {
                "system_prompt": ("STRING", {
                    "default": "You are a helpful assistant.",
                    "multiline": True,
                }),
                "image": ("IMAGE",),
                "advanced_params_json": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "full_response")
    FUNCTION = "generate_text"
    CATEGORY = "ai_customurl"
    
    def generate_text(
        self,
        base_url,
        api_key,
        model,
        prompt,
        temperature,
        max_tokens,
        system_prompt="You are a helpful assistant.",
        image=None,
        advanced_params_json="",
    ):
        """Execute text generation"""
        
        from ..utils.api_client import OpenAIAPIClient
        from ..utils.converters import image_to_base64
        
        try:
            client = OpenAIAPIClient(base_url, api_key)
            
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Handle vision if image provided
            if image is not None:
                user_content = [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_to_base64(image)}"
                        }
                    }
                ]
                messages.append({"role": "user", "content": user_content})
            else:
                messages.append({"role": "user", "content": prompt})
            
            # Build parameters
            params = {
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            # Merge advanced parameters if provided
            if advanced_params_json:
                try:
                    advanced_params = json.loads(advanced_params_json)
                    params.update(advanced_params)
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse advanced_params_json: {e}")
            
            # Make API call
            response = client.chat_completion(
                model=model,
                messages=messages,
                **params
            )
            
            text_response = response["choices"][0]["message"]["content"]
            full_response = json.dumps(response, indent=2)
            
            return (text_response, full_response)
            
        except Exception as e:
            error_msg = f"Text generation failed: {str(e)}"
            print(error_msg)
            return (error_msg, str(e))


class TextAdvancedParamsNode:
    """
    Advanced parameters for text generation (OpenAI API spec)
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "top_p": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                }),
                "frequency_penalty": ("FLOAT", {
                    "default": 0.0,
                    "min": -2.0,
                    "max": 2.0,
                    "step": 0.1,
                }),
                "presence_penalty": ("FLOAT", {
                    "default": 0.0,
                    "min": -2.0,
                    "max": 2.0,
                    "step": 0.1,
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647,
                }),
                "stop_sequences": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
                "response_format": (["text", "json_object"], {
                    "default": "text",
                }),
                "n": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 10,
                }),
                "enable_logprobs": (["false", "true"], {
                    "default": "false",
                }),
                "top_logprobs": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 20,
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("params_json",)
    FUNCTION = "generate_params"
    CATEGORY = "ai_customurl"
    
    def generate_params(
        self,
        top_p,
        frequency_penalty,
        presence_penalty,
        seed,
        stop_sequences,
        response_format,
        n,
        enable_logprobs,
        top_logprobs,
    ):
        """Build advanced parameters object"""
        
        params = {}
        
        # Add parameters only if non-default
        if top_p != 1.0:
            params["top_p"] = top_p
        
        if frequency_penalty != 0.0:
            params["frequency_penalty"] = frequency_penalty
        
        if presence_penalty != 0.0:
            params["presence_penalty"] = presence_penalty
        
        if seed >= 0:
            params["seed"] = seed
        
        if stop_sequences:
            # Parse comma-separated stop sequences
            stops = [s.strip() for s in stop_sequences.split(",") if s.strip()]
            if stops:
                params["stop"] = stops
        
        if response_format == "json_object":
            params["response_format"] = {"type": "json_object"}
        
        if n > 1:
            params["n"] = n
        
        if enable_logprobs == "true":
            params["logprobs"] = True
            if top_logprobs > 0:
                params["top_logprobs"] = top_logprobs
        
        return (json.dumps(params),)


NODE_CLASS_MAPPINGS = {
    "TextGeneration_AICustomURL": TextGenerationNode,
    "TextAdvancedParams_AICustomURL": TextAdvancedParamsNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextGeneration_AICustomURL": "Generate Text (AI CustomURL)",
    "TextAdvancedParams_AICustomURL": "Text Advanced Parameters",
}

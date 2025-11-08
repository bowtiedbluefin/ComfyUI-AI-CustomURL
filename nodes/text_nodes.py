"""Text generation nodes for AI CustomURL"""

import json
from typing import Optional
from comfy_api.latest import io


class TextGenerationNode(io.ComfyNode):
    """
    Generate text using OpenAI-compatible chat completion API
    
    Supports: OpenAI, Venice.ai, OpenRouter, Together.ai, Ollama, etc.
    """
    
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="TextGeneration_AICustomURL",
            display_name="Generate Text (AI CustomURL)",
            category="AI_CustomURL/Text",
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
                    default="gpt-4o",
                    multiline=False,
                ),
                io.String.Input(
                    "prompt",
                    default="",
                    multiline=True,
                ),
                
                # Common Optional Parameters
                io.String.Input(
                    "system_prompt",
                    default="You are a helpful assistant.",
                    multiline=True,
                ),
                io.Float.Input(
                    "temperature",
                    default=1.0,
                    min=0.0,
                    max=2.0,
                    step=0.1,
                ),
                io.Int.Input(
                    "max_tokens",
                    default=1024,
                    min=1,
                    max=128000,
                    step=1,
                ),
                
                # Optional Inputs
                io.Image.Input("image", optional=True),  # For vision models
                io.String.Input("advanced_params_json", default="", multiline=False, optional=True),
            ],
            outputs=[
                io.String.Output("text"),
                io.String.Output("full_response"),
            ],
        )
    
    @classmethod
    def execute(
        cls,
        base_url: str,
        api_key: str,
        model: str,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int,
        image: Optional[object] = None,
        advanced_params_json: str = "",
    ) -> io.NodeOutput:
        """Execute text generation"""
        
        from utils.api_client import OpenAIAPIClient
        from utils.converters import image_to_base64
        
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
            
            return io.NodeOutput(text_response, full_response)
            
        except Exception as e:
            error_msg = f"Text generation failed: {str(e)}"
            print(error_msg)
            return io.NodeOutput(error_msg, str(e))


class TextAdvancedParamsNode(io.ComfyNode):
    """
    Advanced parameters for text generation (OpenAI API spec)
    """
    
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="TextAdvancedParams_AICustomURL",
            display_name="Text Advanced Parameters",
            category="AI_CustomURL/Text",
            inputs=[
                # OpenAI standard optional parameters
                io.Float.Input(
                    "top_p",
                    default=1.0,
                    min=0.0,
                    max=1.0,
                    step=0.01,
                ),
                io.Float.Input(
                    "frequency_penalty",
                    default=0.0,
                    min=-2.0,
                    max=2.0,
                    step=0.1,
                ),
                io.Float.Input(
                    "presence_penalty",
                    default=0.0,
                    min=-2.0,
                    max=2.0,
                    step=0.1,
                ),
                io.Int.Input(
                    "seed",
                    default=-1,
                    min=-1,
                    max=2147483647,
                ),
                io.String.Input(
                    "stop_sequences",
                    default="",
                    multiline=False,
                ),
                io.Combo.Input(
                    "response_format",
                    options=["text", "json_object"],
                ),
                io.Int.Input(
                    "n",
                    default=1,
                    min=1,
                    max=10,
                ),
                io.Combo.Input(
                    "enable_logprobs",
                    options=["false", "true"],
                ),
                io.Int.Input(
                    "top_logprobs",
                    default=0,
                    min=0,
                    max=20,
                ),
            ],
            outputs=[
                io.String.Output("params_json"),
            ],
        )
    
    @classmethod
    def execute(
        cls,
        top_p: float,
        frequency_penalty: float,
        presence_penalty: float,
        seed: int,
        stop_sequences: str,
        response_format: str,
        n: int,
        enable_logprobs: str,
        top_logprobs: int,
    ) -> io.NodeOutput:
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
        
        return io.NodeOutput(json.dumps(params))


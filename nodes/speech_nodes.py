"""Speech generation nodes for AI CustomURL"""

import json
import tempfile
import os
import torch
import torchaudio


class SpeechGenerationNode:
    """
    Generate speech using OpenAI-compatible TTS API
    
    Supports: OpenAI TTS, Venice.ai, and other compatible APIs
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
                    "default": "tts-1",
                    "multiline": False,
                }),
                "input": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "voice": ("STRING", {
                    "default": "alloy",
                    "multiline": False,
                }),
                "response_format": (["mp3", "opus", "aac", "flac", "wav", "pcm"], {
                    "default": "mp3",
                }),
                "speed": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.25,
                    "max": 4.0,
                    "step": 0.01,
                }),
            },
            "optional": {
                "advanced_params_json": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
            },
        }
    
    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("audio", "file_path")
    FUNCTION = "generate_speech"
    CATEGORY = "ai_customurl"
    
    def generate_speech(
        self,
        base_url,
        api_key,
        model,
        input,
        voice,
        response_format,
        speed,
        advanced_params_json="",
    ):
        """Execute speech generation"""
        
        from ..utils.api_client import OpenAIAPIClient
        
        try:
            client = OpenAIAPIClient(base_url, api_key)
            
            # Build parameters
            params = {
                "response_format": response_format,
                "speed": speed,
            }
            
            # Merge advanced parameters if provided
            if advanced_params_json:
                try:
                    advanced_params = json.loads(advanced_params_json)
                    params.update(advanced_params)
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse advanced_params_json: {e}")
            
            # Make API call
            audio_bytes = client.generate_speech(
                model=model,
                input=input,
                voice=voice,
                **params
            )
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(
                suffix=f".{response_format}",
                delete=False
            ) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            try:
                # Load audio using torchaudio
                waveform, sample_rate = torchaudio.load(temp_file_path)
                
                # Ensure shape is [B, C, T] (batch size 1)
                if waveform.dim() == 2:
                    waveform = waveform.unsqueeze(0)  # [1, C, T]
                elif waveform.dim() == 1:
                    waveform = waveform.unsqueeze(0).unsqueeze(0)  # [1, 1, T]
                
                audio_output = {
                    "waveform": waveform,
                    "sample_rate": sample_rate,
                }
                
                return (audio_output, temp_file_path)
                
            except Exception as e:
                print(f"Warning: Failed to load audio with torchaudio: {e}")
                # Return file path if loading fails
                return ("audio_bytes_saved", temp_file_path)
            
        except Exception as e:
            error_msg = f"Speech generation failed: {str(e)}"
            print(error_msg)
            return (error_msg, "")


class SpeechAdvancedParamsNode:
    """
    Advanced parameters for speech generation
    
    Includes extended parameters supported by some APIs
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "pitch": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.5,
                    "max": 2.0,
                    "step": 0.1,
                }),
                "stability": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                }),
                "similarity_boost": ("FLOAT", {
                    "default": 0.75,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                }),
                "emotion": (["neutral", "happy", "sad", "angry", "fearful", "surprised"], {
                    "default": "neutral",
                }),
                "language": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("params_json",)
    FUNCTION = "generate_params"
    CATEGORY = "ai_customurl"
    
    def generate_params(
        self,
        pitch,
        stability,
        similarity_boost,
        emotion,
        language,
    ):
        """Build advanced parameters object"""
        
        params = {}
        
        # Add pitch if not default
        if pitch != 1.0:
            params["pitch"] = pitch
        
        # Add stability if not default
        if stability != 0.5:
            params["stability"] = stability
        
        # Add similarity boost if not default
        if similarity_boost != 0.75:
            params["similarity_boost"] = similarity_boost
        
        # Add emotion if specified
        if emotion != "neutral":
            params["emotion"] = emotion
        
        # Add language if specified
        if language:
            params["language"] = language
        
        return (json.dumps(params),)


NODE_CLASS_MAPPINGS = {
    "SpeechGeneration_AICustomURL": SpeechGenerationNode,
    "SpeechAdvancedParams_AICustomURL": SpeechAdvancedParamsNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SpeechGeneration_AICustomURL": "Generate Speech (AI CustomURL)",
    "SpeechAdvancedParams_AICustomURL": "Speech Advanced Parameters",
}

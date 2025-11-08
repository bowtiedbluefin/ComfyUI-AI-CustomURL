"""Speech generation nodes for AI CustomURL"""

import json
import tempfile
import os
from typing import Optional
import torch
import torchaudio
from comfy_api.latest import io


class SpeechGenerationNode(io.ComfyNode):
    """
    Generate speech using OpenAI-compatible TTS API
    
    Supports: OpenAI TTS, Venice.ai, and other compatible APIs
    """
    
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SpeechGeneration_AICustomURL",
            display_name="Generate Speech (AI CustomURL)",
            category="AI_CustomURL/Speech",
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
                    default="tts-1",
                    multiline=False,
                ),
                io.String.Input(
                    "input",
                    default="",
                    multiline=True,
                ),
                io.String.Input(
                    "voice",
                    default="alloy",
                    multiline=False,
                ),
                
                # Optional Parameters
                io.Combo.Input(
                    "response_format",
                    options=["mp3", "opus", "aac", "flac", "wav", "pcm"],
                ),
                io.Float.Input(
                    "speed",
                    default=1.0,
                    min=0.25,
                    max=4.0,
                    step=0.01,
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
                io.String.Output("audio"),  # AUDIO type
                io.String.Output("file_path"),
            ],
        )
    
    @classmethod
    def execute(
        cls,
        base_url: str,
        api_key: str,
        model: str,
        input: str,
        voice: str,
        response_format: str,
        speed: float,
        advanced_params_json: str = "",
    ) -> io.NodeOutput:
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
                
                return io.NodeOutput(str(audio_output), temp_file_path)
                
            except Exception as e:
                print(f"Warning: Failed to load audio with torchaudio: {e}")
                # Return file path if loading fails
                return io.NodeOutput("audio_bytes_saved", temp_file_path)
            
        except Exception as e:
            error_msg = f"Speech generation failed: {str(e)}"
            print(error_msg)
            return io.NodeOutput(error_msg, "")


class SpeechAdvancedParamsNode(io.ComfyNode):
    """
    Advanced parameters for speech generation
    
    Includes extended parameters supported by some APIs
    """
    
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SpeechAdvancedParams_AICustomURL",
            display_name="Speech Advanced Parameters",
            category="AI_CustomURL/Speech",
            inputs=[
                # Voice settings (some APIs)
                io.Float.Input(
                    "pitch",
                    default=1.0,
                    min=0.5,
                    max=2.0,
                    step=0.1,
                ),
                io.Float.Input(
                    "stability",
                    default=0.5,
                    min=0.0,
                    max=1.0,
                    step=0.1,
                ),
                io.Float.Input(
                    "similarity_boost",
                    default=0.75,
                    min=0.0,
                    max=1.0,
                    step=0.05,
                ),
                
                # Emotion (some APIs)
                io.Combo.Input(
                    "emotion",
                    options=["neutral", "happy", "sad", "angry", "fearful", "surprised"],
                ),
                
                # Language (some APIs)
                io.String.Input(
                    "language",
                    default="",
                    multiline=False,
                ),
            ],
            outputs=[
                io.String.Output("params_json"),
            ],
        )
    
    @classmethod
    def execute(
        cls,
        pitch: float,
        stability: float,
        similarity_boost: float,
        emotion: str,
        language: str,
    ) -> io.NodeOutput:
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
        
        return io.NodeOutput(json.dumps(params))


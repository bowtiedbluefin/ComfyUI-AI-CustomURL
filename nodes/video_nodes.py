"""Video generation nodes for AI CustomURL"""

import json
import time


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
                    "default": "sora-2",
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
                    "default": 4,
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
                "auto_poll": (["true", "false"], {
                    "default": "true",
                }),
                "poll_interval": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 60,
                    "step": 1,
                }),
                "max_wait_time": ("INT", {
                    "default": 1200,
                    "min": 60,
                    "max": 7200,
                    "step": 60,
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
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("video_url", "video_id", "api_key", "status", "response_json")
    FUNCTION = "generate_video"
    CATEGORY = "ai_customurl"
    OUTPUT_NODE = True
    
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
        auto_poll,
        poll_interval,
        max_wait_time,
        image=None,
        advanced_params_json="",
    ):
        """Execute video generation with optional auto-polling"""
        
        from ..utils.api_client import OpenAIAPIClient
        from ..utils.converters import image_to_base64
        
        try:
            client = OpenAIAPIClient(base_url, api_key)
            
            # Convert parameters to OpenAI format
            # OpenAI only supports 4 specific sizes: 720x1280, 1280x720, 1024x1792, 1792x1024
            # Map resolution + aspect_ratio to closest OpenAI supported size
            if "openai.com" in base_url:
                # Use OpenAI's exact supported sizes
                size_mapping = {
                    # 16:9 landscape
                    ("1080p", "16:9"): "1280x720",
                    ("720p", "16:9"): "1280x720",
                    ("480p", "16:9"): "1280x720",
                    # 9:16 portrait
                    ("1080p", "9:16"): "720x1280",
                    ("720p", "9:16"): "720x1280",
                    ("480p", "9:16"): "720x1280",
                    # Wide landscape (21:9, 4:3) → use 1792x1024
                    ("1080p", "21:9"): "1792x1024",
                    ("720p", "21:9"): "1792x1024",
                    ("480p", "21:9"): "1792x1024",
                    ("1080p", "4:3"): "1792x1024",
                    ("720p", "4:3"): "1792x1024",
                    ("480p", "4:3"): "1792x1024",
                    # Square (1:1) → use closest landscape
                    ("1080p", "1:1"): "1280x720",
                    ("720p", "1:1"): "1280x720",
                    ("480p", "1:1"): "1280x720",
                }
            else:
                # Full size mapping for non-OpenAI APIs
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
            # OpenAI only accepts specific values for seconds: "4", "8", or "12"
            if "openai.com" in base_url:
                valid_seconds = ["4", "8", "12"]
                closest_seconds = min(valid_seconds, key=lambda x: abs(int(x) - duration))
                if int(closest_seconds) != duration:
                    print(f"[INFO] OpenAI only supports 4, 8, or 12 second videos. Converting {duration}s → {closest_seconds}s")
                
                final_size = size_mapping.get((resolution, aspect_ratio), "1280x720")
                print(f"[INFO] OpenAI video size: {resolution} {aspect_ratio} → {final_size}")
                
                params = {
                    "size": final_size,
                    "seconds": closest_seconds,  # OpenAI expects string: "4", "8", or "12"
                }
            else:
                # Other APIs may support different formats
                params = {
                    "size": size_mapping.get((resolution, aspect_ratio), "1920x1080"),
                    "seconds": duration,
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
                # OpenAI uses "image" parameter for image-to-video (as form field)
                if "openai.com" in base_url:
                    params["image"] = f"data:image/png;base64,{base64_img}"
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
            
            # Log the full response for debugging
            response_json = json.dumps(response, indent=2)
            print(f"[DEBUG] Initial API Response:\n{response_json}")
            
            # Extract video ID or URL from response
            video_url = ""
            video_id = ""
            status = "unknown"
            status_log = []  # Track all status updates for UI display
            
            # Check for video ID (async response)
            if "id" in response:
                video_id = response.get("id", "")
                status = response.get("status", "unknown")
                status_log.append(f"Video generation started. ID: {video_id}")
                status_log.append(f"Initial status: {status}")
                print(f"[INFO] Video generation started. ID: {video_id}")
                print(f"[INFO] Initial status: {status}")
                
                # If auto-polling enabled and not completed, poll until done
                if auto_poll == "true" and status != "completed":
                    status_log.append(f"Auto-polling enabled. Checking every {poll_interval}s (max {max_wait_time}s)")
                    print(f"[INFO] Auto-polling enabled. Will check every {poll_interval}s (max {max_wait_time}s)")
                    
                    start_time = time.time()
                    poll_count = 0
                    while (time.time() - start_time) < max_wait_time:
                        if status == "completed":
                            break
                        
                        # Wait before polling
                        print(f"[INFO] Waiting {poll_interval}s before checking status...")
                        time.sleep(poll_interval)
                        
                        # Poll for status
                        try:
                            poll_response = client._request("GET", f"/videos/{video_id}")
                            status = poll_response.get("status", "unknown")
                            elapsed = int(time.time() - start_time)
                            poll_count += 1
                            status_log.append(f"Check #{poll_count} ({elapsed}s): {status}")
                            print(f"[INFO] Status check ({elapsed}s elapsed): {status}")
                            
                            if status == "completed":
                                response = poll_response
                                response_json = json.dumps(response, indent=2)
                                status_log.append(f"✅ Video completed after {elapsed}s!")
                                print(f"[SUCCESS] Video completed after {elapsed}s!")
                                break
                            elif status == "failed":
                                error_msg = poll_response.get("error", "Unknown error")
                                status_log.append(f"❌ Video generation failed: {error_msg}")
                                print(f"[ERROR] Video generation failed: {error_msg}")
                                status_message = "\n".join(status_log)
                                return {
                                    "ui": {"text": status_message},
                                    "result": ("", video_id, api_key, "failed", json.dumps(poll_response, indent=2))
                                }
                        except Exception as poll_error:
                            print(f"[WARNING] Poll error: {poll_error}")
                            status_log.append(f"⚠️ Poll warning: {str(poll_error)}")
                            # Continue polling despite error
                    
                    # Check if we timed out
                    if status != "completed":
                        status_log.append(f"⏱️ Timeout after {max_wait_time}s. Status: {status}")
                        status_log.append(f"Use 'Retrieve Video Status' node with ID: {video_id}")
                        print(f"[WARNING] Max wait time ({max_wait_time}s) reached. Status: {status}")
                        print(f"[INFO] Use 'Retrieve Video Status' node with ID: {video_id}")
                        status_message = "\n".join(status_log)
                        return {
                            "ui": {"text": status_message},
                            "result": ("", video_id, api_key, f"timeout (status: {status})", response_json)
                        }
                
                # Extract URL if completed
                if status == "completed":
                    # OpenAI doesn't return a direct URL in the status response
                    # Need to construct the download URL from the video ID
                    if "openai.com" in base_url:
                        # OpenAI format: GET /v1/videos/{id}/content
                        video_url = f"{base_url}/videos/{video_id}/content"
                        print(f"[SUCCESS] Video download URL: {video_url}")
                    # Check for direct URL fields (other APIs)
                    elif "url" in response:
                        video_url = response.get("url", "")
                        print(f"[SUCCESS] Video URL: {video_url}")
                    elif "output_url" in response:
                        video_url = response.get("output_url", "")
                        print(f"[SUCCESS] Video URL: {video_url}")
                    elif "download_url" in response:
                        video_url = response.get("download_url", "")
                        print(f"[SUCCESS] Video URL: {video_url}")
                    else:
                        print(f"[WARNING] Video completed but no URL found in response")
            
            # Check for direct video URL (sync response - non-OpenAI APIs)
            elif "video" in response:
                video_url = response["video"].get("url", "")
            elif "data" in response and len(response["data"]) > 0:
                video_url = response["data"][0].get("url", "")
            elif "url" in response:
                video_url = response.get("url", "")
            
            if not video_url and not video_id:
                print(f"[WARNING] No video URL or ID found in response")
                status = "error"
                status_log.append("⚠️ No video URL or ID found in response")
            elif not video_url:
                status = "processing"
                if video_id:
                    status_log.append(f"Video is still processing. ID: {video_id}")
            else:
                status = "completed"
                status_log.append(f"✅ Video ready! URL: {video_url[:50]}...")
            
            # Return with UI text for status display
            status_message = "\n".join(status_log) if status_log else f"Status: {status}"
            return {
                "ui": {"text": status_message},
                "result": (video_url, video_id, api_key, status, response_json)
            }
            
        except Exception as e:
            error_msg = f"❌ Video generation failed: {str(e)}"
            print(error_msg)
            return {
                "ui": {"text": error_msg},
                "result": (error_msg, "", "", "error", str(e))
            }


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


class VideoRetrieveNode:
    """
    Retrieve/check status of video generation by ID
    
    Used for async video generation APIs like OpenAI Sora
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
                "video_id": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("video_url", "status", "response_json")
    FUNCTION = "retrieve_video"
    CATEGORY = "ai_customurl"
    OUTPUT_NODE = True
    
    def retrieve_video(self, base_url, api_key, video_id):
        """Retrieve video generation status/result"""
        
        from ..utils.api_client import OpenAIAPIClient
        
        try:
            if not video_id or video_id.startswith("error:") or video_id.startswith("processing:"):
                # Extract video ID from processing message
                if "video ID " in video_id:
                    video_id = video_id.split("video ID ")[1].split(",")[0].strip()
                else:
                    error_msg = f"❌ Invalid video ID: {video_id}"
                    return {
                        "ui": {"text": error_msg},
                        "result": ("", "error", f"Invalid video ID: {video_id}")
                    }
            
            client = OpenAIAPIClient(base_url, api_key)
            
            # Try to retrieve video status
            print(f"[INFO] Retrieving video: {video_id}")
            response = client._request("GET", f"/videos/{video_id}")
            
            response_json = json.dumps(response, indent=2)
            print(f"[DEBUG] Retrieve Response:\n{response_json}")
            
            # Extract status and URL
            status = response.get("status", "unknown")
            video_url = ""
            status_message = f"Checking video ID: {video_id}\n"
            
            if status == "completed":
                # Try different possible URL fields
                if "url" in response:
                    video_url = response.get("url", "")
                elif "output_url" in response:
                    video_url = response.get("output_url", "")
                elif "download_url" in response:
                    video_url = response.get("download_url", "")
                
                if video_url:
                    status_message += f"✅ Video completed!\nURL: {video_url[:50]}..."
                    print(f"[SUCCESS] Video completed: {video_url}")
                else:
                    # For OpenAI, construct the content URL
                    if "openai.com" in base_url:
                        video_url = f"{base_url}/videos/{video_id}/content"
                        status_message += f"✅ Video completed!\nDownload URL: {video_url[:50]}..."
                        print(f"[SUCCESS] Video completed. Download URL: {video_url}")
                    else:
                        status_message += "⚠️ Video completed but no URL found in response"
                        print(f"[WARNING] Video completed but no URL found")
            elif status == "failed":
                error_info = response.get("error", "Unknown error")
                status_message += f"❌ Video generation failed\nError: {error_info}"
                print(f"[ERROR] Video failed: {error_info}")
            elif status == "processing" or status == "queued":
                status_message += f"⏳ Video status: {status}\nStill processing..."
                print(f"[INFO] Video status: {status}")
            else:
                status_message += f"ℹ️ Video status: {status}"
                print(f"[INFO] Video status: {status}")
            
            return {
                "ui": {"text": status_message},
                "result": (video_url, status, response_json)
            }
            
        except Exception as e:
            error_msg = f"❌ Failed to retrieve video: {str(e)}"
            print(error_msg)
            return {
                "ui": {"text": error_msg},
                "result": ("", "error", str(e))
            }


class VideoPreviewNode:
    """
    Preview video in ComfyUI interface
    
    Downloads video and displays it in the UI
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url": ("STRING", {
                    "default": "",
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
    
    RETURN_TYPES = ()
    FUNCTION = "preview_video"
    CATEGORY = "ai_customurl"
    OUTPUT_NODE = True
    
    def preview_video(self, video_url, api_key=""):
        """Download and preview video"""
        
        import os
        import hashlib
        import requests
        import folder_paths
        
        try:
            if not video_url or video_url.startswith("error:"):
                return {"ui": {"text": (f"Error: Invalid video URL: {video_url}",)}}
            
            # Use ComfyUI's temp directory for previews
            output_dir = folder_paths.get_temp_directory()
            
            # Generate filename from URL hash to avoid duplicates
            url_hash = hashlib.md5(video_url.encode()).hexdigest()[:8]
            filename = f"preview_{url_hash}.mp4"
            video_path = os.path.join(output_dir, filename)
            
            print(f"[INFO] Downloading video for preview: {video_url}")
            
            # Setup headers for authenticated requests
            headers = {}
            if api_key and ("openai.com" in video_url or "api.openai" in video_url):
                headers["Authorization"] = f"Bearer {api_key}"
                print(f"[INFO] Using authenticated download for preview")
            
            # Download video
            response = requests.get(video_url, headers=headers, stream=True, timeout=300)
            response.raise_for_status()
            
            # Save to file
            with open(video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Get file size
            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            print(f"[SUCCESS] Video downloaded for preview: {file_size_mb:.2f} MB")
            print(f"[INFO] Video preview at: {video_path}")
            
            # Return video in proper ComfyUI format for video preview
            # This format is what ComfyUI expects for displaying videos in the UI
            return {
                "ui": {
                    "videos": [{
                        "filename": filename,
                        "subfolder": "",
                        "type": "temp",
                        "format": "video/h264-mp4"
                    }],
                    "text": (f"✅ Video ready ({file_size_mb:.2f} MB)",)
                }
            }
            
        except Exception as e:
            error_msg = f"Failed to preview video: {str(e)}"
            print(error_msg)
            return {"ui": {"text": (error_msg,)}}


NODE_CLASS_MAPPINGS = {
    "VideoGeneration_AICustomURL": VideoGenerationNode,
    "VideoAdvancedParams_AICustomURL": VideoAdvancedParamsNode,
    "VideoRetrieve_AICustomURL": VideoRetrieveNode,
    "VideoPreview_AICustomURL": VideoPreviewNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoGeneration_AICustomURL": "Generate Video (AI CustomURL)",
    "VideoAdvancedParams_AICustomURL": "Video Advanced Parameters",
    "VideoRetrieve_AICustomURL": "Retrieve Video Status (AI CustomURL)",
    "VideoPreview_AICustomURL": "Preview Video (AI CustomURL)",
}

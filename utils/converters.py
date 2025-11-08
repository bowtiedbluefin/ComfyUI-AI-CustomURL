"""Data type conversion utilities"""

import base64
import io
from typing import Optional
import numpy as np
import requests
import torch
from PIL import Image


def tensor_to_pil(tensor: torch.Tensor) -> Image.Image:
    """
    Convert PyTorch tensor to PIL Image
    
    Args:
        tensor: Image tensor (H, W, C) or (B, H, W, C)
        
    Returns:
        PIL Image
    """
    # Handle batch dimension
    if tensor.dim() == 4:
        tensor = tensor[0]
    
    # Convert to numpy
    if tensor.is_cuda:
        tensor = tensor.cpu()
    
    numpy_image = tensor.numpy()
    
    # Handle channel ordering
    if numpy_image.shape[0] == 3:  # (C, H, W)
        numpy_image = np.transpose(numpy_image, (1, 2, 0))  # (H, W, C)
    
    # Convert to 0-255 range if needed
    if numpy_image.dtype == np.float32 or numpy_image.dtype == np.float64:
        if numpy_image.max() <= 1.0:
            numpy_image = (numpy_image * 255).astype(np.uint8)
        else:
            numpy_image = numpy_image.astype(np.uint8)
    
    return Image.fromarray(numpy_image)


def pil_to_tensor(image: Image.Image) -> torch.Tensor:
    """
    Convert PIL Image to PyTorch tensor
    
    Args:
        image: PIL Image
        
    Returns:
        Image tensor (1, H, W, C) in range [0, 1]
    """
    # Convert to RGB if needed
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Convert to numpy array
    numpy_image = np.array(image).astype(np.float32) / 255.0
    
    # Convert to tensor and add batch dimension
    tensor = torch.from_numpy(numpy_image).unsqueeze(0)
    
    return tensor


def image_to_base64(tensor: torch.Tensor, format: str = "PNG") -> str:
    """
    Convert image tensor to base64 string
    
    Args:
        tensor: Image tensor
        format: Image format (PNG, JPEG, WEBP)
        
    Returns:
        Base64 encoded image string
    """
    pil_image = tensor_to_pil(tensor)
    
    buffered = io.BytesIO()
    pil_image.save(buffered, format=format)
    img_bytes = buffered.getvalue()
    
    return base64.b64encode(img_bytes).decode("utf-8")


def base64_to_tensor(base64_string: str) -> torch.Tensor:
    """
    Convert base64 string to image tensor
    
    Args:
        base64_string: Base64 encoded image
        
    Returns:
        Image tensor (1, H, W, C)
    """
    img_bytes = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(img_bytes))
    
    return pil_to_tensor(image)


def url_to_tensor(url: str) -> torch.Tensor:
    """
    Download image from URL and convert to tensor
    
    Args:
        url: Image URL
        
    Returns:
        Image tensor (1, H, W, C)
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    image = Image.open(io.BytesIO(response.content))
    
    return pil_to_tensor(image)


def create_blank_tensor(width: int = 512, height: int = 512) -> torch.Tensor:
    """
    Create a blank black image tensor
    
    Args:
        width: Image width
        height: Image height
        
    Returns:
        Black image tensor (1, H, W, C)
    """
    return torch.zeros((1, height, width, 3), dtype=torch.float32)


import torch
import torch.nn as nn
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np
import requests
import os
from io import BytesIO

class CLIPImageEncoder:
    """
    OpenAI CLIP model wrapper for generating image embeddings
    """
    
    def __init__(self, model_name="openai/clip-vit-base-patch32", cache_dir=None):
        """
        Initialize CLIP model and processor
        
        Args:
            model_name (str): HuggingFace model identifier
            cache_dir (str, optional): Directory to cache downloaded models
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Set cache directory if provided
        if cache_dir:
            os.environ['TRANSFORMERS_CACHE'] = cache_dir
            os.environ['HF_HOME'] = cache_dir
        
        try:
            # Load CLIP model and processor
            self.model = CLIPModel.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                local_files_only=False  # Allow downloading if not cached
            )
            self.processor = CLIPProcessor.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                local_files_only=False
            )
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()
            
            print(f"CLIP model '{model_name}' loaded successfully")
            
        except Exception as e:
            print(f"Error loading CLIP model: {e}")
            raise
    
    def load_image_from_path(self, image_path):
        """
        Load image from local file path
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            PIL.Image: Loaded image
        """
        try:
            image = Image.open(image_path).convert('RGB')
            return image
        except Exception as e:
            raise ValueError(f"Error loading image from {image_path}: {str(e)}")
    
    def load_image_from_url(self, image_url):
        """
        Load image from URL
        
        Args:
            image_url (str): URL to image
            
        Returns:
            PIL.Image: Loaded image
        """
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert('RGB')
            return image
        except Exception as e:
            raise ValueError(f"Error loading image from URL {image_url}: {str(e)}")
    
    def encode_image(self, image):
        """
        Generate CLIP embedding for an image
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            np.ndarray: Normalized image embedding vector
        """
        try:
            # Process image
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embedding
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
                
            # Normalize the embedding
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Convert to numpy and return
            embedding = image_features.cpu().numpy().flatten()
            return embedding
            
        except Exception as e:
            raise ValueError(f"Error encoding image: {str(e)}")
    
    def encode_image_from_path(self, image_path):
        """
        Generate embedding directly from image path
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            np.ndarray: Normalized image embedding vector
        """
        image = self.load_image_from_path(image_path)
        return self.encode_image(image)
    
    def encode_image_from_url(self, image_url):
        """
        Generate embedding directly from image URL
        
        Args:
            image_url (str): URL to image
            
        Returns:
            np.ndarray: Normalized image embedding vector
        """
        image = self.load_image_from_url(image_url)
        return self.encode_image(image)
    
    def batch_encode_images(self, images):
        """
        Generate embeddings for multiple images efficiently
        
        Args:
            images (list): List of PIL Images
            
        Returns:
            np.ndarray: Array of normalized embeddings
        """
        try:
            # Process all images
            inputs = self.processor(images=images, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embeddings
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
                
            # Normalize embeddings
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Convert to numpy
            embeddings = image_features.cpu().numpy()
            return embeddings
            
        except Exception as e:
            raise ValueError(f"Error batch encoding images: {str(e)}")
    
    def get_embedding_dimension(self):
        """
        Get the dimension of the embedding vectors
        
        Returns:
            int: Embedding dimension
        """
        return self.model.config.projection_dim

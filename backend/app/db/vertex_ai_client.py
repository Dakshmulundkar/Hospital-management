"""Vertex AI client for AI/ML predictions"""
import vertexai
from typing import Optional
from ..config import settings

try:
    from vertexai.preview.generative_models import GenerativeModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    GenerativeModel = None


class VertexAIClient:
    """Client for interacting with Vertex AI"""
    
    def __init__(self):
        self.model = None
        self.available = False
        
        # Only initialize if credentials and project are available
        if VERTEX_AI_AVAILABLE and settings.vertex_ai_project:
            try:
                # Initialize Vertex AI
                vertexai.init(
                    project=settings.vertex_ai_project,
                    location=settings.vertex_ai_location
                )
                self.model = GenerativeModel(settings.vertex_ai_model)
                self.available = True
            except Exception as e:
                print(f"Vertex AI initialization failed: {e}")
                self.available = False
    
    async def check_connection(self) -> bool:
        """Check if Vertex AI is accessible"""
        if not self.available or not self.model:
            return False
            
        try:
            # Try a simple generation to test connectivity
            response = self.model.generate_content("Hello")
            return True
        except Exception as e:
            print(f"Vertex AI connection check failed: {e}")
            return False
    
    def generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Optional[str]:
        """Generate content using Vertex AI"""
        if not self.available or not self.model:
            print("Vertex AI not available, returning None")
            return None
            
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )
            return response.text
        except Exception as e:
            print(f"Error generating content: {e}")
            return None


# Singleton instance
vertex_ai_client = VertexAIClient()

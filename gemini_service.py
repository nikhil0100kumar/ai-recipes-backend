"""
Gemini API service for ingredient analysis and recipe generation
"""
import json
import asyncio
import logging
from typing import Optional, Dict, Any, Tuple
from io import BytesIO
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image
import httpx

from config import settings
from models import AnalysisResponse, Ingredient, Recipe, SYSTEM_PROMPT, USER_PROMPT

logger = logging.getLogger(__name__)


class GeminiServiceError(Exception):
    """Custom exception for Gemini service errors."""
    pass


class GeminiService:
    """Service for interacting with Google Gemini API."""
    
    def __init__(self):
        """Initialize Gemini service with API key."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
        logger.info(f"Initialized Gemini service with model: {settings.gemini_model}")
    
    async def analyze_image(self, image_bytes: bytes) -> AnalysisResponse:
        """
        Analyze image using Gemini API and return structured response.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            AnalysisResponse: Parsed ingredients and recipes
            
        Raises:
            GeminiServiceError: If analysis fails
        """
        try:
            # Validate and process image
            pil_image = await self._process_image(image_bytes)
            
            # Prepare prompt
            full_prompt = f"{SYSTEM_PROMPT}\n\n{USER_PROMPT}"
            
            # Make API call with retry logic
            response_text = await self._call_gemini_with_retry(pil_image, full_prompt)
            
            # Parse and validate response
            analysis_response = await self._parse_gemini_response(response_text)
            
            logger.info(f"Successfully analyzed image - found {len(analysis_response.ingredients)} ingredients and {len(analysis_response.recipes)} recipes")
            return analysis_response
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            if isinstance(e, GeminiServiceError):
                raise
            raise GeminiServiceError(f"Unexpected error during image analysis: {str(e)}")
    
    async def _process_image(self, image_bytes: bytes) -> Image.Image:
        """Process and validate image bytes."""
        try:
            # Open and validate image
            pil_image = Image.open(BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Resize if too large (max 4MB for Gemini)
            if len(image_bytes) > 4 * 1024 * 1024:
                pil_image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                logger.info("Resized large image for Gemini API")
            
            return pil_image
            
        except Exception as e:
            raise GeminiServiceError(f"Invalid image format: {str(e)}")
    
    async def _call_gemini_with_retry(self, image: Image.Image, prompt: str) -> str:
        """Call Gemini API with retry logic and timeout handling."""
        last_error = None
        
        for attempt in range(settings.max_retries):
            try:
                logger.debug(f"Calling Gemini API (attempt {attempt + 1}/{settings.max_retries})")
                
                # Use asyncio.wait_for for timeout
                response = await asyncio.wait_for(
                    self._generate_content(image, prompt),
                    timeout=settings.request_timeout
                )
                
                if not response or not response.text:
                    raise GeminiServiceError("Empty response from Gemini API")
                
                logger.debug("Received response from Gemini API")
                return response.text.strip()
                
            except asyncio.TimeoutError:
                last_error = GeminiServiceError(f"Gemini API timeout after {settings.request_timeout} seconds")
                logger.warning(f"Timeout on attempt {attempt + 1}")
                
            except Exception as e:
                last_error = GeminiServiceError(f"Gemini API error: {str(e)}")
                logger.warning(f"Error on attempt {attempt + 1}: {str(e)}")
            
            # Wait before retry (except on last attempt)
            if attempt < settings.max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # All retries failed
        raise last_error or GeminiServiceError("All retry attempts failed")
    
    async def _generate_content(self, image: Image.Image, prompt: str):
        """Generate content using Gemini API (async wrapper)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.model.generate_content([prompt, image])
        )
    
    async def _parse_gemini_response(self, response_text: str) -> AnalysisResponse:
        """Parse and validate Gemini API response."""
        try:
            # Clean response text
            cleaned_text = self._clean_response_text(response_text)
            
            # Parse JSON
            try:
                data = json.loads(cleaned_text)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed, attempting to extract JSON: {str(e)}")
                data = self._extract_json_from_text(cleaned_text)
            
            # Validate structure
            if not isinstance(data, dict):
                raise GeminiServiceError("Response is not a valid JSON object")
            
            # Parse ingredients
            ingredients = []
            if "ingredients" in data and isinstance(data["ingredients"], list):
                for ing_data in data["ingredients"]:
                    if isinstance(ing_data, dict) and "name" in ing_data:
                        ingredients.append(Ingredient(
                            name=str(ing_data["name"]),
                            category=str(ing_data.get("category", "unknown"))
                        ))
            
            # Parse recipes
            recipes = []
            if "recipes" in data and isinstance(data["recipes"], list):
                for recipe_data in data["recipes"][:3]:  # Limit to 3 recipes
                    if isinstance(recipe_data, dict) and "title" in recipe_data:
                        steps = recipe_data.get("steps", [])
                        if isinstance(steps, list):
                            steps = [str(step) for step in steps if step]
                        else:
                            steps = []
                        
                        recipes.append(Recipe(
                            title=str(recipe_data["title"]),
                            prep_time=str(recipe_data.get("prep_time", "30 minutes")),
                            difficulty=str(recipe_data.get("difficulty", "medium")),
                            steps=steps
                        ))
            
            return AnalysisResponse(ingredients=ingredients, recipes=recipes)
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            # Return empty response instead of failing completely
            return AnalysisResponse(ingredients=[], recipes=[])
    
    def _clean_response_text(self, text: str) -> str:
        """Clean response text to extract JSON."""
        # Remove markdown code blocks
        text = text.replace("```json", "").replace("```", "")
        
        # Remove common prefixes/suffixes
        text = text.strip()
        
        # Find JSON-like content
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return text[start_idx:end_idx + 1]
        
        return text
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from malformed text response."""
        try:
            # Try to find JSON-like patterns
            import re
            
            # Look for ingredients pattern
            ingredients_pattern = r'"ingredients"\s*:\s*\[(.*?)\]'
            recipes_pattern = r'"recipes"\s*:\s*\[(.*?)\]'
            
            result = {"ingredients": [], "recipes": []}
            
            # Extract ingredients
            ing_match = re.search(ingredients_pattern, text, re.DOTALL)
            if ing_match:
                try:
                    ingredients_json = f'[{ing_match.group(1)}]'
                    result["ingredients"] = json.loads(ingredients_json)
                except:
                    pass
            
            # Extract recipes
            recipe_match = re.search(recipes_pattern, text, re.DOTALL)
            if recipe_match:
                try:
                    recipes_json = f'[{recipe_match.group(1)}]'
                    result["recipes"] = json.loads(recipes_json)
                except:
                    pass
            
            return result
            
        except Exception as e:
            logger.warning(f"Failed to extract JSON from malformed response: {str(e)}")
            return {"ingredients": [], "recipes": []}


# Global service instance
gemini_service = GeminiService()

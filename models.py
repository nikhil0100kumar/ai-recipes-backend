"""
Data models for AI Recipes Backend API
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    """Detected ingredient from image analysis."""
    name: str = Field(..., description="Name of the ingredient")
    category: str = Field(..., description="Category of the ingredient (e.g., 'vegetable', 'protein', 'grain')")


class Recipe(BaseModel):
    """Recipe suggestion based on detected ingredients."""
    title: str = Field(..., description="Name of the recipe")
    prep_time: str = Field(..., description="Preparation time (e.g., '30 minutes')")
    difficulty: str = Field(..., description="Difficulty level (e.g., 'easy', 'medium', 'hard')")
    steps: List[str] = Field(..., description="List of cooking steps")


class AnalysisResponse(BaseModel):
    """Response model for ingredient analysis and recipe suggestions."""
    ingredients: List[Ingredient] = Field(default_factory=list, description="Detected ingredients")
    recipes: List[Recipe] = Field(default_factory=list, description="Recipe suggestions")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")


class SuccessResponse(BaseModel):
    """Success response wrapper."""
    success: bool = Field(default=True)
    data: AnalysisResponse = Field(..., description="Analysis results")
    message: Optional[str] = Field(None, description="Success message")


# Gemini API system prompt
SYSTEM_PROMPT = """You are an AI chef assistant. 
- Your job is to identify ingredients from an uploaded image and generate simple recipes. 
- IMPORTANT: Always include at least 3 recipes in your response.
- Always return valid JSON.
- JSON schema:
  {
    "ingredients": [ { "name": string, "category": string } ],
    "recipes": [
      { "title": string, "prep_time": string, "difficulty": string, "steps": [string] }
    ]
  }
- Each recipe must have:
  * A descriptive title
  * prep_time like "15 minutes", "30 minutes", or "1 hour"
  * difficulty: "easy", "medium", or "hard"
  * steps: Array of at least 3 detailed cooking steps
- Do not include explanations or extra text outside JSON.
- If the image is unclear or contains non-food items, return an empty ingredient list and recipes array."""

# User prompt for Gemini API
USER_PROMPT = """Analyze the uploaded image. 
1) Detect all visible food ingredients. 
2) MANDATORY: Generate exactly 3 recipes using these ingredients and common kitchen staples (oil, salt, pepper, basic spices).
3) Make sure each recipe has complete steps with clear instructions.
Remember: You MUST include 3 recipes in the response."""

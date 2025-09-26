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


# Gemini API system prompt - Master Food Analyzer & Recipe Generator
SYSTEM_PROMPT = """# Master Food Analyzer & Recipe Generator System

You are an advanced AI combining expertise of a nutritionist, food scientist, and Michelin-starred chef.

## Core Instructions
1. Analyze uploaded images for food items
2. Provide nutritional information
3. Generate 3 creative, healthy recipes using ONLY detected ingredients + common household items

## Workflow

### Step 1: Image Analysis
- Identify ALL visible food items
- Categorize (vegetables, fruits, proteins, grains, dairy, etc.)
- If NO food detected: return empty ingredients and recipes arrays

### Step 2: Recipe Generation
Generate EXACTLY 3 recipes using ONLY:
- Detected ingredients from the image
- Common household items: salt, pepper, oil, garlic, basic spices

## STRICT OUTPUT FORMAT - JSON ONLY
Return ONLY valid JSON in this exact structure:
{
  "ingredients": [
    { "name": "ingredient name", "category": "vegetable/protein/grain/etc" }
  ],
  "recipes": [
    {
      "title": "Creative recipe name",
      "prep_time": "X minutes",
      "difficulty": "easy/medium/hard",
      "steps": [
        "Step 1: Detailed preparation instructions",
        "Step 2: Cooking process with temperatures and timing",
        "Step 3: Professional techniques and tips",
        "Step 4: Final touches and plating"
      ]
    }
  ]
}

## Recipe Quality Standards
- Each recipe must have 4-6 detailed steps
- Include specific temperatures and cooking times
- Add professional chef techniques
- Focus on maximizing flavor with detected ingredients
- Ensure variety in cooking methods across the 3 recipes

## CRITICAL RULES
1. Output ONLY valid JSON - no extra text or explanations
2. ALWAYS return exactly 3 recipes
3. Each recipe must have at least 4 detailed steps
4. Use professional culinary terminology
5. Never add ingredients not visible in the image (except basic household items)"""

# User prompt for Gemini API
USER_PROMPT = """Analyze this food image as a Master Chef and Nutritionist:

1. IDENTIFY: List all visible food ingredients with their categories
2. CREATE: Generate EXACTLY 3 professional recipes using ONLY:
   - The detected ingredients
   - Basic household items (salt, pepper, oil, common spices)
3. DETAIL: Each recipe must have:
   - Creative, appetizing name
   - Precise prep time
   - 4-6 detailed cooking steps with temperatures and techniques
   - Professional chef tips embedded in steps

Return ONLY valid JSON. No explanations outside the JSON structure."""

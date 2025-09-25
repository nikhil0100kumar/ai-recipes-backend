# AI Recipes Backend

A production-ready FastAPI backend that handles Gemini 2.5 Flash API calls for ingredient analysis and recipe generation. This separates backend concerns from your Flutter frontend and provides better error handling, security, and scalability.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Gemini API key from Google AI Studio

### Setup

1. **Navigate to backend directory:**
   ```bash
   cd ai-recipes-backend
   ```

2. **Create environment file:**
   ```bash
   copy .env.example .env
   ```
   
3. **Edit .env file and add your Gemini API key:**
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   DEBUG=true
   ```

4. **Run the startup script:**
   ```bash
   python start.py
   ```

The server will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

## 📁 Project Structure

```
ai-recipes-backend/
├── main.py              # FastAPI application and routes
├── config.py            # Configuration management
├── models.py            # Pydantic data models
├── gemini_service.py    # Gemini API integration
├── requirements.txt     # Python dependencies
├── start.py            # Easy startup script
├── Dockerfile          # Container deployment
├── .env.example        # Environment template
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Your Gemini API key | - | ✅ |
| `HOST` | Server host | `0.0.0.0` | ❌ |
| `PORT` | Server port | `8000` | ❌ |
| `DEBUG` | Enable debug mode | `false` | ❌ |
| `ALLOWED_ORIGINS` | CORS origins | `http://localhost:3000` | ❌ |
| `MAX_FILE_SIZE_MB` | Max upload size | `10` | ❌ |

### Manual Setup (Alternative)

If you prefer manual setup:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python main.py
   ```

## 📡 API Endpoints

### POST /analyze

Analyze an image to detect ingredients and generate recipes.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Image file (`file` field)

**Supported formats:** JPEG, PNG, WebP (max 10MB)

**Response:**
```json
{
  "success": true,
  "message": "Image analyzed successfully",
  "data": {
    "ingredients": [
      {
        "name": "tomato",
        "category": "vegetable"
      }
    ],
    "recipes": [
      {
        "title": "Simple Tomato Salad",
        "prep_time": "15 minutes",
        "difficulty": "easy",
        "steps": [
          "Wash and slice tomatoes",
          "Add salt and pepper",
          "Serve fresh"
        ]
      }
    ]
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Recipes Backend",
  "version": "1.0.0"
}
```

### Debug Endpoints (Development Only)

- `GET /debug/config` - View current configuration
- `POST /debug/test-gemini` - Test Gemini API connectivity

## 🛡️ Error Handling

The API provides comprehensive error handling with meaningful HTTP status codes:

- `400` - Bad Request (invalid file, unsupported format, etc.)
- `503` - Service Unavailable (Gemini API issues)
- `500` - Internal Server Error

**Error Response Format:**
```json
{
  "error": "Brief error description",
  "detail": "Detailed error information (debug mode only)",
  "status_code": 400
}
```

## 📱 Flutter Integration

Update your Flutter app to use the backend instead of calling Gemini directly:

### 1. Add the Backend API Service

Copy `backend_api_service.dart` to your Flutter project's `lib/services/` directory.

### 2. Update Your Ingredient Analysis Screen

Replace your existing API service with the backend service:

```dart
// Import the backend service
import '../services/backend_api_service.dart';

class IngredientAnalysisScreen extends StatefulWidget {
  // ... existing code ...

  Future<void> _analyzeImage() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Use backend service instead of direct Gemini calls
      final backendService = BackendApiService();
      final result = await backendService.analyzeIngredients(_imageFile!);

      if (result.isSuccess && result.data != null) {
        setState(() {
          _analysisResult = result.data;
          _isLoading = false;
        });
      } else {
        setState(() {
          _error = result.error ?? 'Failed to analyze image';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error: $e';
        _isLoading = false;
      });
    }
  }
}
```

### 3. Update Dependencies

Make sure your Flutter app's `pubspec.yaml` includes:

```yaml
dependencies:
  http: ^1.1.0  # For API calls
  # ... other dependencies
```

### 4. Network Configuration

#### Android
Add to `android/app/src/main/AndroidManifest.xml`:
```xml
<application
    android:usesCleartextTraffic="true"
    ... >
```

#### iOS
No additional configuration needed for localhost.

## 🚢 Production Deployment

### Using Docker

1. **Build the image:**
   ```bash
   docker build -t ai-recipes-backend .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 --env-file .env ai-recipes-backend
   ```

### Using Cloud Platforms

The backend is ready for deployment on:
- **Google Cloud Run**
- **AWS Lambda** (with Mangum)
- **Heroku**
- **DigitalOcean App Platform**

Make sure to:
1. Set environment variables in your platform
2. Update `ALLOWED_ORIGINS` for production domains
3. Set `DEBUG=false` for production
4. Configure proper SSL/HTTPS

## 🔧 Customization

### Adding New Endpoints

Add new routes to `main.py`:

```python
@app.post("/recipes")
async def get_recipes_only(ingredients: List[str]):
    # Your custom logic here
    pass
```

### Modifying Prompts

Update the system and user prompts in `models.py`:

```python
SYSTEM_PROMPT = """Your custom system prompt..."""
USER_PROMPT = """Your custom user prompt..."""
```

### Adding Authentication

You can easily add authentication middleware:

```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    token: str = Depends(security)
):
    # Validate token
    # ... rest of your code
```

## 🐛 Troubleshooting

### Backend Issues

1. **"Gemini API key not configured"**
   - Make sure your `.env` file contains `GEMINI_API_KEY=your_key_here`
   - Restart the server after updating the env file

2. **"Failed to connect to backend"**
   - Check if the backend is running on `http://localhost:8000`
   - Verify the backend health: `curl http://localhost:8000/health`

3. **CORS errors**
   - Update `ALLOWED_ORIGINS` in your `.env` file
   - Make sure your Flutter app is connecting to the right URL

### Flutter Integration Issues

1. **"Failed to connect to backend"**
   - Make sure the backend URL in `backend_api_service.dart` is correct
   - Check that your device/emulator can reach localhost:8000

2. **Upload issues**
   - Verify file sizes are under 10MB
   - Check that file types are supported (JPEG, PNG, WebP)

## 📊 Monitoring

### Logs

The backend logs to both console and `ai-recipes-backend.log` file:

- Request/response information
- Error details and stack traces
- Performance metrics

### Health Monitoring

Use the `/health` endpoint for health checks in production:

```bash
curl http://localhost:8000/health
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the AI Recipes application.

---

## 🎯 Next Steps

After setting up the backend:

1. ✅ **Test the backend** - Use the `/docs` endpoint to test API calls
2. ✅ **Update Flutter** - Replace the old API service with backend calls
3. ✅ **Test integration** - Verify the full flow works end-to-end
4. 🔄 **Deploy to production** - Use Docker or cloud platforms
5. 📈 **Monitor and optimize** - Add logging and performance monitoring

**Need help?** Check the troubleshooting section or create an issue in the repository.

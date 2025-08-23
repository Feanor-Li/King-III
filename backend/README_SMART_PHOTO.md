# Smart Photo System

An intelligent photo system based on LangGraph that analyzes reference photos and natural language instructions to automatically adjust iPhone camera parameters for photography.

## 🏗️ System Architecture

```
Reference Photo Upload → Image Analysis → Parameter Generation → User Refinement → iPhone Control → Photo Capture
     ↑                                       ↓                                  
     └─────────── Optimization Loop ←──────────────────┘
```

### Core Components

- **UploadNode**: Handle reference photo uploads
- **ImageAnalyzerNode**: Analyze image features, extract exposure, composition information
- **RefinementNode**: Parse user natural language instructions, adjust camera parameters  
- **iPhoneControlNode**: Convert parameters to iPhone API calls
- **PhotoCaptureNode**: Trigger photo capture and return results

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy and modify configuration file:
```bash
cp env.example .env
```

Modify the `.env` file configuration:
```
HOST=0.0.0.0
PORT=8000
UPLOAD_DIR=/tmp/smart_photo_uploads
OUTPUT_DIR=/tmp/smart_photo_output
IPHONE_API_ENDPOINT=http://your-iphone-ip:8080/control
```

### 3. Start Service

```bash
python main.py
```

The service will start at `http://localhost:8000`.

## 📝 API Usage Guide

### 1. Upload Reference Photo

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@reference_photo.jpg"
```

Response:
```json
{
  "session_id": "uuid-string",
  "current_step": "ready_for_refinement",
  "error_message": null
}
```

### 2. View Analysis Results

```bash
curl "http://localhost:8000/status/{session_id}"
```

Response:
```json
{
  "session_id": "uuid-string", 
  "current_step": "ready_for_refinement",
  "analysis": {
    "brightness": 0.6,
    "contrast": 0.4,
    "scene_type": "portrait"
  },
  "final_params": {
    "aperture": "f/1.6",
    "exposure": 0.0,
    "iso": 200
  }
}
```

### 3. Send Refinement Instructions

```bash
curl -X POST "http://localhost:8000/refine" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-string",
    "user_input": "increase exposure a bit, need more background blur"
  }'
```

### 4. Trigger Photo Capture

```bash
curl -X POST "http://localhost:8000/capture/{session_id}"
```

### 5. Get Capture Results

```bash
curl "http://localhost:8000/photo/{session_id}" --output captured_photo.jpg
```

## 🎯 Supported Natural Language Instructions

### Exposure Related
- "increase exposure" / "brighten"
- "decrease exposure" / "darken"
- "exposure +1" / "exposure -0.5"

### Aperture Related  
- "more blur" / "larger aperture"
- "sharper background" / "smaller aperture"
- "aperture f/1.6"

### Scene Related
- "portrait mode"
- "landscape mode"
- "night mode"

### Other Parameters
- "increase ISO" / "ISO 800"
- "auto focus" / "macro focus"
- "warm tone" / "cool tone"

## 🐳 Docker Deployment

### Build and Start

```bash
docker-compose up -d
```

### Scale Deployment

```bash
docker-compose up -d --scale smart-photo-api=3
```

## 📱 iPhone Integration

The system supports multiple iPhone control methods:

### 1. HTTP API Method
Run camera app supporting HTTP control on iPhone

### 2. iOS Shortcuts Method
Create corresponding shortcuts to receive parameters and control camera

### 3. Simulation Mode
Used for development testing, generates simulated capture results

## 🔧 System Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| HOST | 0.0.0.0 | Service binding address |
| PORT | 8000 | Service port |
| UPLOAD_DIR | /tmp/smart_photo_uploads | Upload file directory |
| OUTPUT_DIR | /tmp/smart_photo_output | Output file directory |
| IPHONE_API_ENDPOINT | localhost:8080/iphone-control | iPhone control API |
| CAPTURE_API_ENDPOINT | localhost:8080/iphone-capture | iPhone capture API |

## 🔍 Monitoring and Debugging

### Health Check
```bash
curl http://localhost:8000/health
```

### View Active Sessions
```bash
curl http://localhost:8000/sessions
```

### View System Info
```bash
curl http://localhost:8000/graph/info
```

## 🛠️ Development Guide

### Project Structure
```
backend/
├── smart_photo_system/
│   ├── models/           # Data models
│   ├── nodes/            # LangGraph nodes
│   ├── api.py            # FastAPI interface
│   └── graph.py          # Workflow definition
├── main.py               # Entry file
├── requirements.txt      # Dependencies
└── Dockerfile           # Container config
```

### Custom Nodes

Inherit from `BaseNode` class to create new processing nodes:

```python
from smart_photo_system.nodes.base import BaseNode

class CustomNode(BaseNode):
    async def execute(self, state: PhotoSystemState) -> PhotoSystemState:
        # Implement custom logic
        return state
```

### Extend API

Add new routes in `SmartPhotoAPI` class:

```python
@self.app.post("/custom-endpoint")
async def custom_handler():
    # Implement custom functionality
    pass
```

## 🚧 Known Limitations

1. iPhone control currently mainly in simulation mode, needs actual iPhone API integration
2. Image analysis uses traditional CV methods, consider integrating AI models
3. Session storage in memory, production environment should use Redis or database
4. File upload size limits need adjustment based on actual requirements

## 🔮 Future Roadmap

- [ ] Integrate OpenAI Vision API for smarter image analysis
- [ ] Support more camera brands (Android, professional cameras)
- [ ] Add photo post-processing capabilities
- [ ] Implement user preference learning
- [ ] Support batch processing
- [ ] Add web interface

## 📄 License

MIT License
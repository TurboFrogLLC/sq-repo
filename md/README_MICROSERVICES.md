# ShopQuote Microservices Setup

This guide explains how to set up and test the ShopQuote microservices locally for development and deployment.

## 🏗️ Architecture Overview

The ShopQuote application uses a microservices architecture with the following components:

- **Main Application** (`main.py`) - Taipy web interface
- **DXF Parser** (`uploaders/DXF/`) - Processes DXF CAD files
- **PDF Parser** (`uploaders/PDF/`) - Extracts data from PDF drawings
- **STEP Parser** (`uploaders/step/`) - Handles STEP 3D model files
- **Trace Logger** (`uploaders/trace/`) - Audit logging service

## 🚀 Local Development Setup

### 1. Start the Microservices Hub

```bash
cd shopquote-taipy
python microservices.py
```

This starts the microservices management interface on `http://localhost:8005`

### 2. Start Individual Services

#### Option A: Start All Services
```bash
curl -X POST http://localhost:8005/start-all
```

#### Option B: Start Individual Services
```bash
# Start DXF parser
curl -X POST http://localhost:8005/start/dxf

# Start PDF parser
curl -X POST http://localhost:8005/start/pdf

# Start STEP parser
curl -X POST http://localhost:8005/start/step

# Start Trace logger
curl -X POST http://localhost:8005/start/trace
```

### 3. Check Service Status

```bash
curl http://localhost:8005/status
```

Expected response:
```json
{
  "services": {
    "dxf": {"status": "running", "port": 8001, "pid": 12345},
    "pdf": {"status": "running", "port": 8002, "pid": 12346},
    "step": {"status": "running", "port": 8003, "pid": 12347},
    "trace": {"status": "running", "port": 8004, "pid": 12348}
  }
}
```

## 🧪 Testing Microservices

### 1. Create Test Files

```bash
python test_microservices.py --create-test-files
```

This creates sample test files in the `test_files/` directory.

### 2. Run Tests

```bash
python test_microservices.py
```

This will:
- ✅ Check service hub connectivity
- ✅ Start all microservices
- ✅ Test file processing with sample files
- ✅ Verify service management
- ✅ Stop all services

### 3. Manual Testing

#### Test File Upload
```bash
# Test DXF file processing
curl -X POST -F "file=@test_files/test.dxf" http://localhost:8005/test-file-processing

# Test PDF file processing
curl -X POST -F "file=@test_files/test.pdf" http://localhost:8005/test-file-processing

# Test STEP file processing
curl -X POST -F "file=@test_files/test.step" http://localhost:8005/test-file-processing
```

## 🔧 Service Configuration

Each microservice has its own configuration:

### DXF Parser (Port 8001)
- **Path**: `uploaders/DXF/`
- **Main File**: `main.py`
- **Purpose**: Extract geometry and metadata from DXF files
- **Dependencies**: `ezdxf`, `shapely`

### PDF Parser (Port 8002)
- **Path**: `uploaders/PDF/`
- **Main File**: `shopquote_ocr.py`
- **Purpose**: OCR and text extraction from PDF drawings
- **Dependencies**: `pdfminer.six`, `pytesseract`, `opencv-python`

### STEP Parser (Port 8003)
- **Path**: `uploaders/step/`
- **Main File**: `main_freecad.py`
- **Purpose**: Process STEP files for 3D geometry analysis
- **Dependencies**: `FreeCAD` (external), `numpy`

### Trace Logger (Port 8004)
- **Path**: `uploaders/trace/`
- **Main File**: `main.py`
- **Purpose**: Centralized audit logging and session tracking
- **Dependencies**: `requests`, `python-json-logger`

## 🌐 Render.com Deployment

### 1. Connect Repository

1. Go to [Render.com](https://render.com)
2. Connect your GitHub repository: `https://github.com/TurboFrogLLC/shopquote`
3. Select the `shopquote-taipy` directory

### 2. Configure Services

#### Main Application Service
```yaml
# render.yaml
services:
  - type: web
    name: shopquote-main
    runtime: python3
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: TAIPY_PORT
        value: 10000
      - key: TAIPY_HOST
        value: 0.0.0.0
    healthCheckPath: /
```

#### Microservices (Optional - can be combined)
```yaml
# Additional services for microservices
  - type: web
    name: shopquote-dxf-parser
    runtime: python3
    buildCommand: cd uploaders/DXF && pip install -r requirements.txt
    startCommand: cd uploaders/DXF && python main.py
    envVars:
      - key: PORT
        value: 8001

  - type: web
    name: shopquote-pdf-parser
    runtime: python3
    buildCommand: cd uploaders/PDF && pip install -r requirements.txt
    startCommand: cd uploaders/PDF && python shopquote_ocr.py
    envVars:
      - key: PORT
        value: 8002
```

### 3. Environment Variables

Set these in Render.com dashboard:

```bash
# Main application
TAIPY_PORT=10000
TAIPY_HOST=0.0.0.0
PYTHON_VERSION=3.11

# Database (if using)
DATABASE_URL=your_database_url

# File storage (if using cloud storage)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET=your_bucket
```

### 4. Deploy

1. Push changes to GitHub
2. Render.com will auto-deploy
3. Access your application at the provided URL

## 🔍 Troubleshooting

### Service Won't Start
```bash
# Check logs
curl http://localhost:8005/status

# Check specific service logs
tail -f uploaders/DXF/logs/service.log
```

### File Processing Fails
```bash
# Test with simple file
echo "test content" > test.txt
curl -X POST -F "file=@test.txt" http://localhost:8005/test-file-processing
```

### Port Conflicts
```bash
# Find process using port
lsof -i :8001

# Kill process
kill -9 <PID>
```

## 📊 Monitoring

### Health Checks
```bash
# Check all services
curl http://localhost:8005/

# Individual service health
curl http://localhost:8001/health  # DXF
curl http://localhost:8002/health  # PDF
curl http://localhost:8003/health  # STEP
curl http://localhost:8004/health  # Trace
```

### Performance Monitoring
```bash
# Service metrics
curl http://localhost:8005/metrics

# Individual service metrics
curl http://localhost:8001/metrics
```

## 🚀 Production Considerations

### Scaling
- Use Render.com's paid tiers for higher traffic
- Consider load balancers for multiple instances
- Implement caching for frequently accessed data

### Security
- Use HTTPS (Render.com provides SSL certificates)
- Implement authentication for sensitive endpoints
- Use environment variables for secrets
- Regular security updates

### Backup
- Database backups (if applicable)
- File storage backups
- Configuration backups

## 📞 Support

For issues with microservices setup:

1. Check the service logs
2. Verify dependencies are installed
3. Test individual components
4. Check network connectivity
5. Review configuration files

## 🎯 Next Steps

1. **Test Locally**: Run the test suite
2. **Deploy to Render**: Use the provided configuration
3. **Monitor Performance**: Set up logging and monitoring
4. **Scale as Needed**: Upgrade Render.com plan based on usage
5. **Add Features**: Extend microservices as needed

---

**Happy coding!** 🎉
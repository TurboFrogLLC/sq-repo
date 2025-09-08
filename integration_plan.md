# ShopQuote Microservices Integration Plan

## Executive Summary

This document outlines the integration of four specialized microservices (DXF, PDF, STEP, Trace) into the main Taipy web application, creating a unified file processing pipeline that maintains all business rules and provides comprehensive CAD file analysis capabilities.

## Current Microservices Analysis

### 1. DXF Microservice (`ui/microservices/dxf/`)
**Libraries**: `ezdxf`, `typing-extensions`
**Functionality**:
- Parses DXF files for geometry extraction
- Extracts bend count from layers and annotations
- Detects hardware references (FH-, CLS-, PEM- prefixes)
- Calculates bounding boxes and flat patterns
- Filters known vs unknown layers per business rules

**Key Features**:
- Layer classification (L-EXTERNAL, C-FORM, etc.)
- Hardware detection from TEXT/MTEXT annotations
- Bend count extraction from "BENDS:" patterns
- Unit conversion (inches/mm)
- Unknown layer filtering

### 2. PDF Microservice (`ui/microservices/PDF/`)
**Libraries**: `pdf2image`, `pytesseract`, `fastapi`, `pillow`
**Functionality**:
- OCR processing of PDF files
- Metadata extraction from title blocks
- Pattern matching for part information
- Confidence scoring for OCR quality

**Key Features**:
- Regex patterns for part number, material, thickness
- OCR score calculation (0.2-0.8 range)
- Structured field extraction
- Fallback handling for poor OCR quality

### 3. STEP Microservice (`ui/microservices/step/`)
**Libraries**: `freecad`, `python-magic`, `SheetMetalUnfolder`
**Functionality**:
- STEP file parsing and unfolding
- Sheet metal flat pattern generation
- Bend detection and counting
- Dimension extraction

**Key Features**:
- FreeCAD integration for 3D model processing
- SheetMetalUnfolder for flat pattern generation
- Thickness detection from bounding box analysis
- File validation and MIME type checking

### 4. Trace Microservice (`ui/microservices/trace/`)
**Libraries**: `fastapi`, `pydantic`, `python-json-logger`
**Functionality**:
- Audit trail logging
- Session tracking
- Performance monitoring
- Error reporting

**Key Features**:
- Structured JSON logging
- Session correlation
- Performance metrics
- Remote logging to collector service

## Integration Architecture

### Unified File Processing Pipeline

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   File Upload   │───▶│  Type Detection  │───▶│  Parser Router  │
│   (Taipy GUI)   │    │  & Validation    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                       ┌────────────────────────────────┼────────────────────────────────┐
                       │                                │                                │
            ┌─────────▼─────────┐            ┌─────────▼─────────┐            ┌─────────▼─────────┐
            │   DXF Parser     │            │   PDF Parser      │            │  STEP Parser      │
            │  (ezdxf)         │            │  (OCR + pdfminer) │            │ (FreeCAD)         │
            └──────────────────┘            └───────────────────┘            └───────────────────┘
                       │                                │                                │
                       └────────────────────────────────┼────────────────────────────────┘
                                                        │
                                               ┌────────▼────────┐
                                               │  Result Merger  │
                                               │  & Validation   │
                                               └─────────────────┘
                                                        │
                                               ┌────────▼────────┐
                                               │  Quote Update   │
                                               │  (Taipy State)  │
                                               └─────────────────┘
```

### Priority Resolution Logic

Following business rules [SSX002.A] - File Priority Rules:

1. **Material Type** → Trust PDF first
2. **Material Thickness** → Trust PDF first
3. **Notes/Annotations** → Trust PDF first
4. **Outside Processes** → Trust PDF first
5. **Hardware** → Trust PDF first
6. **Flat Pattern Size** → Trust STEP/DXF
7. **Form Count** → Trust STEP/DXF
8. **Part Weight** → Calculated from flat size + PDF thickness

### Fallback Strategy

```
File Processing Decision Tree:
├── PDF Available?
│   ├── Yes → Extract metadata (OCR if needed)
│   └── No → Skip to CAD files
├── CAD Files Available?
│   ├── STEP Available? → Process STEP
│   ├── DXF Available? → Process DXF
│   └── No CAD → Use defaults
└── Merge Results per Priority Rules
```

## Implementation Plan

### Phase 1: Core Integration (Week 1-2)

#### 1.1 Create Unified Parser Module
```python
# ui/integrated_parsers.py
class IntegratedFileProcessor:
    def __init__(self):
        self.dxf_parser = DXFProcessor()
        self.pdf_parser = PDFProcessor()
        self.step_parser = STEPProcessor()

    def process_files(self, uploaded_files: List[UploadedFile]) -> ProcessingResult:
        # Main processing logic with priority resolution
        pass
```

#### 1.2 Update Requirements
```txt
# Add to requirements.txt
ezdxf>=1.3.0
pdf2image>=1.17.0
pytesseract>=0.3.10
python-magic>=0.4.27
# FreeCAD integration (optional for development)
# freecad>=0.21  # Only in production/Docker
```

#### 1.3 Implement Parser Classes

**DXF Processor**:
```python
class DXFProcessor:
    def process(self, file_bytes: bytes) -> DXFResult:
        # Integrate dxf_parser.py logic
        # Return structured result per business rules
        pass
```

**PDF Processor**:
```python
class PDFProcessor:
    def process(self, file_bytes: bytes) -> PDFResult:
        # Integrate OCR logic from shopquote_ocr.py
        # Extract metadata fields with scoring
        pass
```

**STEP Processor**:
```python
class STEPProcessor:
    def process(self, file_bytes: bytes) -> STEPResult:
        # Integrate FreeCAD logic (with fallback for dev)
        # Extract dimensions and bend information
        pass
```

### Phase 2: Business Rules Integration (Week 3)

#### 2.1 Priority Resolution Engine
```python
class PriorityResolver:
    def resolve_conflicts(self, pdf_result, dxf_result, step_result) -> ResolvedData:
        # Implement [SSX002.A] priority rules
        # Material → PDF, Size → CAD, etc.
        pass
```

#### 2.2 Validation Engine
```python
class BusinessRulesValidator:
    def validate(self, resolved_data) -> ValidationResult:
        # Check against all 50+ business rules
        # Return validation status and issues
        pass
```

### Phase 3: Error Handling & Logging (Week 4)

#### 3.1 Comprehensive Error Handling
```python
class ProcessingErrorHandler:
    def handle_error(self, error: Exception, file_type: str) -> ErrorResult:
        # Graceful degradation strategies
        # User-friendly error messages
        # Fallback to manual entry
        pass
```

#### 3.2 Integrated Logging
```python
class TraceLogger:
    def log_processing(self, result: ProcessingResult):
        # Integrate trace microservice logic
        # Session correlation and audit trails
        pass
```

### Phase 4: Testing & Validation (Week 5)

#### 4.1 Unit Tests
- Test each parser individually
- Test priority resolution logic
- Test error handling scenarios

#### 4.2 Integration Tests
- End-to-end file processing workflows
- Multi-file upload scenarios
- Business rules validation

#### 4.3 Performance Testing
- Large file handling
- Concurrent processing
- Memory usage optimization

## Technical Considerations

### Library Dependencies

**Required for All Environments**:
```
ezdxf>=1.3.0          # DXF processing
pdf2image>=1.17.0     # PDF to image conversion
pytesseract>=0.3.10   # OCR processing
python-magic>=0.4.27  # File type detection
```

**Production Only**:
```
freecad>=0.21         # STEP file processing
SheetMetalUnfolder    # Sheet metal unfolding
```

### Environment-Specific Handling

**Development Environment**:
- Mock STEP processing for systems without FreeCAD
- Use sample data for testing
- Graceful degradation for missing libraries

**Production Environment**:
- Full FreeCAD integration
- Docker container with all dependencies
- Optimized performance settings

### Memory Management

**Large File Handling**:
- Stream processing for large files
- Temporary file cleanup
- Memory usage monitoring
- Timeout handling for long operations

## Risk Mitigation

### 1. FreeCAD Dependency
**Risk**: FreeCAD not available in all environments
**Mitigation**:
- Optional STEP processing in development
- Clear error messages for missing dependencies
- Fallback to manual dimension entry

### 2. OCR Accuracy
**Risk**: Poor OCR results affecting quote accuracy
**Mitigation**:
- Confidence scoring and user validation
- Fallback to manual entry
- Multiple OCR engines support

### 3. Performance
**Risk**: Slow processing of large CAD files
**Mitigation**:
- Asynchronous processing
- Progress indicators
- File size limits
- Caching for repeated operations

## Success Metrics

### Functional Metrics
- ✅ All file types processed successfully
- ✅ Business rules compliance maintained
- ✅ Priority resolution working correctly
- ✅ Error handling comprehensive

### Performance Metrics
- ✅ Processing time < 30 seconds for typical files
- ✅ Memory usage < 500MB per operation
- ✅ Concurrent processing support
- ✅ Graceful degradation under load

### Quality Metrics
- ✅ Test coverage > 80%
- ✅ Error rate < 5% for valid files
- ✅ User satisfaction > 90%
- ✅ Business rules compliance 100%

## Deployment Strategy

### Development Deployment
```bash
# Install core dependencies
pip install ezdxf pdf2image pytesseract python-magic

# Optional: FreeCAD for STEP processing
# (Only in production Docker container)
```

### Production Deployment
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    freecad \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

CMD ["python", "main_taipy.py"]
```

## Conclusion

This integration plan provides a comprehensive strategy for unifying the four specialized microservices into a single, cohesive Taipy web application. The approach maintains all existing business rules, provides robust error handling, and ensures scalability for production deployment.

The phased implementation allows for incremental development and testing, with clear success metrics and risk mitigation strategies. The resulting integrated system will provide users with a seamless file processing experience while maintaining the sophisticated parsing capabilities developed in the individual microservices.
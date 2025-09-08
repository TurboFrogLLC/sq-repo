"""
Integrated File Processing Module for ShopQuote Taipy Application

This module integrates the functionality from all four microservices:
- DXF Parser (ezdxf library)
- PDF Parser (OCR + pdfminer)
- STEP Parser (FreeCAD integration)
- Trace Logger (audit trails)

Provides unified file processing with business rules compliance.
"""

from __future__ import annotations
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import io
import time

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Result of file processing operation"""
    success: bool
    filename: str
    file_type: str
    extracted_data: Dict[str, Any]
    confidence_score: float
    errors: List[str]
    processing_time: float

@dataclass
class DXFResult:
    """DXF processing result"""
    units: str
    flat_size_in: Dict[str, float]
    bend_count: int
    bend_types: List[str]
    hardware: List[Dict[str, Any]]
    known_layers: List[str]
    unknown_layers_ignored: List[str]
    entity_counts: Dict[str, int]

@dataclass
class PDFResult:
    """PDF processing result"""
    ocr_score: float
    extracted_fields: Dict[str, Any]
    has_metadata: bool
    text_length: int

@dataclass
class STEPResult:
    """STEP processing result"""
    flat_pattern_mm: Dict[str, float]
    flat_pattern_in: Dict[str, float]
    thickness_mm: float
    thickness_in: float
    bend_count: int
    available: bool = False  # False if FreeCAD not available

class DXFProcessor:
    """DXF file processor using ezdxf library"""

    def process(self, file_bytes: bytes, filename: str) -> ProcessingResult:
        """Process DXF file using integrated DXF parser logic"""
        import time
        start_time = time.time()

        try:
            # Import the DXF parser from microservice
            from src.processors.cad.dxf.dxf_parser import parse_dxf_file

            # Process the file
            result = parse_dxf_file(file_bytes)

            processing_time = time.time() - start_time

            return ProcessingResult(
                success=True,
                filename=filename,
                file_type='DXF',
                extracted_data=result,
                confidence_score=0.95,  # DXF parsing is deterministic
                errors=[],
                processing_time=processing_time
            )

        except Exception as e:
            logger.error(f"DXF processing failed for {filename}: {str(e)}")
            # Return basic file info even on failure
            return ProcessingResult(
                success=True,  # Still consider it processed
                filename=filename,
                file_type='DXF',
                extracted_data={
                    'file_size_kb': len(file_bytes) // 1024,
                    'error': str(e),
                    'note': 'DXF parsing failed, but file was recognized'
                },
                confidence_score=0.1,  # Low confidence due to parsing error
                errors=[str(e)],
                processing_time=time.time() - start_time
            )

class PDFProcessor:
    """PDF file processor with OCR capabilities"""

    def __init__(self):
        self.ocr_processor = None

    def process(self, file_bytes: bytes, filename: str) -> ProcessingResult:
        """Process PDF file using text extraction first, then OCR as fallback"""
        import time
        start_time = time.time()

        try:
            # First attempt: Extract text using pdfminer (fast for text-based PDFs)
            from pdfminer.high_level import extract_text
            text_content = extract_text(io.BytesIO(file_bytes))

            # Check if we got meaningful text content
            has_meaningful_text = self._has_meaningful_text(text_content)

            if has_meaningful_text:
                # Use text-based processing
                logger.info(f"Using text-based processing for {filename}")
                return self._process_text_based(text_content, filename, start_time)
            else:
                # Use OCR processing for scanned PDFs
                logger.info(f"Using OCR processing for {filename} (scanned PDF detected)")
                return self._process_ocr_based(file_bytes, filename, start_time)

        except Exception as e:
            logger.warning(f"Primary PDF processing failed for {filename}: {str(e)}")
            # Fallback to OCR processing
            try:
                logger.info(f"Falling back to OCR processing for {filename}")
                return self._process_ocr_based(file_bytes, filename, start_time)
            except Exception as ocr_error:
                logger.error(f"OCR fallback also failed for {filename}: {str(ocr_error)}")
                return ProcessingResult(
                    success=False,
                    filename=filename,
                    file_type='PDF',
                    extracted_data={},
                    confidence_score=0.0,
                    errors=[str(e), str(ocr_error)],
                    processing_time=time.time() - start_time
                )

    def _has_meaningful_text(self, text_content: str) -> bool:
        """Check if extracted text has meaningful content"""
        if not text_content or len(text_content.strip()) < 50:
            return False

        # Check for common manufacturing terms
        manufacturing_terms = ['part', 'material', 'thickness', 'drawing', 'customer', 'quantity']
        text_lower = text_content.lower()

        # Count meaningful terms
        term_count = sum(1 for term in manufacturing_terms if term in text_lower)

        # If we have at least 2 manufacturing terms, consider it meaningful
        return term_count >= 2

    def _process_text_based(self, text_content: str, filename: str, start_time: float) -> ProcessingResult:
        """Process PDF using text extraction (pdfminer)"""
        try:
            # Check for metadata markers
            has_metadata = 'METADATA SNAPSHOT START' in text_content

            # Basic field extraction using regex patterns
            import re
            patterns = {
                "part_number": r'PART\s*(?:NUMBER|NO\.?)\s*:\s*(.+?)(?:\n|$)',
                "material": r'MATERIAL\s*:\s*(.+?)(?:\n|$)',
                "thickness": r'THICKNESS\s*:\s*([\d\.]+)\s*(in|mm)?(?:\n|$)',
                "finish": r'FINISH:?\s*(.+?)(?:\n|$)',
                "customer_name": r'CUSTOMER\s*:\s*(.+?)(?:\n|$)',
                "part_description": r'(?:DESCRIPTION|DESC)\s*:\s*(.+?)(?:\n|$)',
                "quantity": r'QUANTITY\s*:\s*(\d+)(?:\n|$)',
            }

            extracted_fields = {}
            for key, pattern in patterns.items():
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    if key == "thickness" and len(matches[0]) == 2:
                        # Handle thickness with units
                        value, unit = matches[0]
                        extracted_fields[key] = {
                            "value": float(value),
                            "unit": unit or "in"
                        }
                    else:
                        extracted_fields[key] = matches[0]

            # Calculate confidence score based on extracted fields
            extracted_count = sum(1 for key in ["part_number", "material", "thickness", "finish"]
                                if key in extracted_fields)
            confidence_score = 0.8 if extracted_count == 4 else 0.6 if extracted_count >= 2 else 0.2

            processing_time = time.time() - start_time

            return ProcessingResult(
                success=True,
                filename=filename,
                file_type='PDF',
                extracted_data={
                    'text_content': text_content[:1000],  # First 1000 chars
                    'extracted_fields': extracted_fields,
                    'has_metadata': has_metadata,
                    'text_length': len(text_content),
                    'processing_method': 'text_extraction'
                },
                confidence_score=confidence_score,
                errors=[],
                processing_time=processing_time
            )

        except Exception as e:
            logger.error(f"Text-based PDF processing failed for {filename}: {str(e)}")
            raise

    def _process_ocr_based(self, file_bytes: bytes, filename: str, start_time: float) -> ProcessingResult:
        """Process PDF using OCR (for scanned documents)"""
        try:
            # Lazy import OCR processor to avoid circular imports
            if self.ocr_processor is None:
                from src.processors.pdf.ocr_processor import PDFOCRProcessor
                self.ocr_processor = PDFOCRProcessor()

            # Process with OCR
            ocr_result = self.ocr_processor.process_pdf(file_bytes, filename)

            # Convert OCR result to ProcessingResult format
            extracted_data = {}
            if ocr_result.extracted_data and 'fields' in ocr_result.extracted_data:
                extracted_data = ocr_result.extracted_data['fields']

            # Add OCR-specific metadata
            extracted_data.update({
                'ocr_confidence': ocr_result.overall_confidence,
                'processing_method': 'ocr',
                'ocr_text_sample': ocr_result.ocr_results[0].text[:500] if ocr_result.ocr_results else '',
                'pages_processed': len(ocr_result.ocr_results)
            })

            return ProcessingResult(
                success=ocr_result.success,
                filename=filename,
                file_type='PDF',
                extracted_data=extracted_data,
                confidence_score=ocr_result.overall_confidence,
                errors=ocr_result.errors,
                processing_time=time.time() - start_time
            )

        except Exception as e:
            logger.error(f"OCR-based PDF processing failed for {filename}: {str(e)}")
            raise

class STEPProcessor:
    """STEP file processor with FreeCAD integration"""

    def process(self, file_bytes: bytes, filename: str) -> ProcessingResult:
        """Process STEP file (with fallback for systems without FreeCAD)"""
        import time
        start_time = time.time()

        try:
            # Check if FreeCAD is available
            try:
                import FreeCAD
                freecad_available = True
            except ImportError:
                freecad_available = False

            if freecad_available:
                # Use full FreeCAD processing
                result = self._process_with_freecad(file_bytes, filename)
            else:
                # Fallback processing without FreeCAD
                result = self._process_without_freecad(file_bytes, filename)

            processing_time = time.time() - start_time
            result.processing_time = processing_time

            return result

        except Exception as e:
            logger.error(f"STEP processing failed for {filename}: {str(e)}")
            return ProcessingResult(
                success=False,
                filename=filename,
                file_type='STEP',
                extracted_data={},
                confidence_score=0.0,
                errors=[str(e)],
                processing_time=time.time() - start_time
            )

    def _process_with_freecad(self, file_bytes: bytes, filename: str) -> ProcessingResult:
        """Process STEP file with FreeCAD"""
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix='.step') as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            import FreeCAD
            import Part

            # Create document and load STEP file
            doc = FreeCAD.newDocument()
            shape = Part.read(tmp_path)
            obj = doc.addObject("Part::Feature", "Imported")
            obj.Shape = shape
            doc.recompute()

            # Get bounding box
            bbox = shape.BoundBox
            dims = sorted([bbox.XLength, bbox.YLength, bbox.ZLength])
            thickness_mm = dims[0] if dims else 0.0

            # Try to unfold if SheetMetal tools available
            flat_x = flat_y = 0.0
            bend_count = 0

            try:
                import importlib
                sm = importlib.import_module("SheetMetalUnfolder")
                unfold_obj = sm.makeUnfold(obj)
                doc.recompute()
                flat_shape = unfold_obj.Shape
                flat_bbox = flat_shape.BoundBox
                flat_x = float(flat_bbox.XLength)
                flat_y = float(flat_bbox.YLength)

                # Count bends
                try:
                    bend_count = sum(1 for e in shape.Edges
                                   if getattr(e.Curve, "Curvature", 0) != 0)
                except Exception:
                    bend_count = 0
            except Exception as e:
                logger.warning(f"SheetMetal unfolding failed: {e}")

            # Clean up
            FreeCAD.closeDocument(doc.Name)

            return ProcessingResult(
                success=True,
                filename=filename,
                file_type='STEP',
                extracted_data={
                    'flat_pattern_mm': {'x': flat_x, 'y': flat_y},
                    'flat_pattern_in': {'x': flat_x * 0.03937, 'y': flat_y * 0.03937},
                    'thickness_mm': thickness_mm,
                    'thickness_in': thickness_mm * 0.03937,
                    'bend_count': bend_count,
                    'freecad_available': True
                },
                confidence_score=0.9,
                errors=[],
                processing_time=0.0
            )

        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    def _process_without_freecad(self, file_bytes: bytes, filename: str) -> ProcessingResult:
        """Fallback processing without FreeCAD"""
        file_size_kb = len(file_bytes) // 1024

        return ProcessingResult(
            success=True,
            filename=filename,
            file_type='STEP',
            extracted_data={
                'file_size_kb': file_size_kb,
                'freecad_available': False,
                'note': 'STEP processing requires FreeCAD (available in production)'
            },
            confidence_score=0.3,  # Lower confidence without FreeCAD
            errors=[],
            processing_time=0.0
        )

class PriorityResolver:
    """Resolves conflicts between different file sources per business rules"""

    def resolve(self, results: List[ProcessingResult]) -> Dict[str, Any]:
        """
        Resolve conflicts between multiple file sources following business rules [SSX002.A]

        Priority order:
        - Material Type → PDF
        - Material Thickness → PDF
        - Notes/Annotations → PDF
        - Outside Processes → PDF
        - Hardware → PDF
        - Flat Pattern Size → STEP/DXF
        - Form Count → STEP/DXF
        - Part Weight → Calculated from flat size + PDF thickness
        """

        resolved_data = {
            'customer': None,
            'part_number': None,
            'description': None,
            'material': None,
            'thickness_in': None,
            'flat_size_in': {'width': None, 'height': None},
            'bend_count': None,
            'hardware': [],
            'outside_processes': [],
            'confidence_scores': {},
            'source_files': []
        }

        # Group results by file type
        pdf_results = [r for r in results if r.file_type == 'PDF']
        dxf_results = [r for r in results if r.file_type == 'DXF']
        step_results = [r for r in results if r.file_type == 'STEP']

        # Track source files
        resolved_data['source_files'] = [r.filename for r in results if r.success]

        # PDF takes priority for metadata fields
        if pdf_results:
            pdf_result = pdf_results[0]  # Use first successful PDF
            extracted = pdf_result.extracted_data.get('extracted_fields', {})

            resolved_data['customer'] = extracted.get('customer_name')
            resolved_data['part_number'] = extracted.get('part_number')
            resolved_data['description'] = extracted.get('part_description')
            resolved_data['material'] = extracted.get('material')

            # Handle thickness with units
            thickness_info = extracted.get('thickness')
            if isinstance(thickness_info, dict):
                value = thickness_info.get('value', 0)
                unit = thickness_info.get('unit', 'in')
                if unit == 'mm':
                    value *= 0.03937  # Convert to inches
                resolved_data['thickness_in'] = value

            resolved_data['confidence_scores']['pdf'] = pdf_result.confidence_score

        # CAD files take priority for geometric data
        # STEP has highest priority, then DXF
        if step_results:
            step_result = step_results[0]
            step_data = step_result.extracted_data

            # Use STEP for flat size (highest priority CAD)
            if resolved_data['flat_size_in']['width'] is None:
                resolved_data['flat_size_in'] = step_data.get('flat_pattern_in', {'width': None, 'height': None})

            # Use STEP for bend count (highest priority CAD)
            if resolved_data['bend_count'] is None:
                resolved_data['bend_count'] = step_data.get('bend_count', 0)

            resolved_data['confidence_scores']['step'] = step_result.confidence_score

        elif dxf_results:
            dxf_result = dxf_results[0]
            dxf_data = dxf_result.extracted_data

            # Use DXF for flat size if STEP didn't provide it
            if resolved_data['flat_size_in']['width'] is None:
                resolved_data['flat_size_in'] = dxf_data.get('flat_size_in', {'width': None, 'height': None})

            # Use DXF for bend count if STEP didn't provide it
            if resolved_data['bend_count'] is None:
                resolved_data['bend_count'] = dxf_data.get('bend_count', 0)

            # Use DXF for hardware
            resolved_data['hardware'] = dxf_data.get('hardware', [])

            resolved_data['confidence_scores']['dxf'] = dxf_result.confidence_score

        return resolved_data

class IntegratedFileProcessor:
    """Main integrated file processor"""

    def __init__(self):
        self.dxf_processor = DXFProcessor()
        self.pdf_processor = PDFProcessor()
        self.step_processor = STEPProcessor()
        self.priority_resolver = PriorityResolver()

    def process_files(self, uploaded_files) -> Dict[str, Any]:
        """
        Process multiple uploaded files and return unified results

        Args:
            uploaded_files: List of uploaded file objects from Taipy

        Returns:
            Dict containing processing results and resolved data
        """
        logger.info(f"Processing {len(uploaded_files)} files")

        results = []
        errors = []

        # Process each file
        for uploaded_file in uploaded_files:
            try:
                # Get file content
                file_content = uploaded_file.read()

                # Determine file type and process accordingly
                filename = uploaded_file.name.lower()

                if filename.endswith('.pdf'):
                    result = self.pdf_processor.process(file_content, uploaded_file.name)
                elif filename.endswith('.dxf'):
                    result = self.dxf_processor.process(file_content, uploaded_file.name)
                elif filename.endswith(('.step', '.stp')):
                    result = self.step_processor.process(file_content, uploaded_file.name)
                else:
                    result = ProcessingResult(
                        success=False,
                        filename=uploaded_file.name,
                        file_type='Unknown',
                        extracted_data={},
                        confidence_score=0.0,
                        errors=['Unsupported file type'],
                        processing_time=0.0
                    )

                results.append(result)

                if not result.success:
                    errors.extend(result.errors)

            except Exception as e:
                logger.error(f"Error processing {uploaded_file.name}: {str(e)}")
                errors.append(f"Error processing {uploaded_file.name}: {str(e)}")

        # Resolve conflicts between sources
        resolved_data = self.priority_resolver.resolve([r for r in results if r.success])

        # Prepare final response
        successful_files = [r for r in results if r.success]
        failed_files = [r for r in results if not r.success]

        response = {
            'processed_files': [
                {
                    'filename': r.filename,
                    'type': r.file_type,
                    'status': 'processed',
                    'confidence_score': r.confidence_score,
                    'processing_time': f"{r.processing_time:.2f}s",
                    'extracted_data': r.extracted_data
                }
                for r in successful_files
            ],
            'failed_files': [
                {
                    'filename': r.filename,
                    'type': r.file_type,
                    'errors': r.errors
                }
                for r in failed_files
            ],
            'resolved_data': resolved_data,
            'summary': {
                'total_files': len(uploaded_files),
                'successful': len(successful_files),
                'failed': len(failed_files),
                'errors': errors
            }
        }

        logger.info(f"Processing complete: {len(successful_files)} successful, {len(failed_files)} failed")
        return response

# Global instance for use in Taipy application
file_processor = IntegratedFileProcessor()
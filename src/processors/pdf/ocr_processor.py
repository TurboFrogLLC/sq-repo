#!/usr/bin/env python3
"""
OCR Processor for ShopQuote PDF Processing
Handles OCR processing of scanned PDFs and data extraction
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import time
import re
import io

logger = logging.getLogger(__name__)

@dataclass
class OCRResult:
    """Result of OCR processing"""
    text: str
    confidence_score: float
    word_confidences: List[float]
    processing_time: float
    page_count: int
    total_words: int

@dataclass
class PDFOCRResult:
    """Complete PDF OCR processing result"""
    success: bool
    filename: str
    ocr_results: List[OCRResult]
    extracted_data: Dict[str, Any]
    overall_confidence: float
    processing_time: float
    errors: List[str]

class PDFImageConverter:
    """Converts PDF pages to high-quality images for OCR"""

    def __init__(self, dpi: int = 300, quality: int = 95):
        self.dpi = dpi
        self.quality = quality

    def convert_to_images(self, pdf_bytes: bytes, first_page: int = 1, last_page: Optional[int] = None) -> List[bytes]:
        """
        Convert PDF pages to images

        Args:
            pdf_bytes: PDF file content as bytes
            first_page: First page to convert (1-indexed)
            last_page: Last page to convert (None for all remaining pages)

        Returns:
            List of image bytes (PNG format)
        """
        try:
            from pdf2image import convert_from_bytes
            from PIL import Image
            import io

            # Convert PDF to images
            images = convert_from_bytes(
                pdf_bytes,
                dpi=self.dpi,
                first_page=first_page,
                last_page=last_page,
                fmt='png'
            )

            # Convert PIL images to bytes
            image_bytes = []
            for img in images:
                # Enhance image quality for better OCR
                enhanced_img = self._enhance_image_for_ocr(img)

                # Convert to bytes
                img_buffer = io.BytesIO()
                enhanced_img.save(img_buffer, format='PNG', optimize=True, quality=self.quality)
                image_bytes.append(img_buffer.getvalue())

            logger.info(f"Converted {len(image_bytes)} PDF pages to images")
            return image_bytes

        except Exception as e:
            logger.error(f"PDF to image conversion failed: {e}")
            raise

    def _enhance_image_for_ocr(self, image) -> 'Image':
        """Enhance image quality for better OCR results"""
        try:
            from PIL import Image, ImageFilter, ImageEnhance

            # Convert to grayscale for better OCR
            if image.mode != 'L':
                image = image.convert('L')

            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)

            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)

            # Apply slight blur to reduce noise
            image = image.filter(ImageFilter.MedianFilter(size=1))

            return image

        except Exception as e:
            logger.warning(f"Image enhancement failed: {e}")
            return image

class OCRTextExtractor:
    """Extracts text from images using Tesseract OCR"""

    def __init__(self, language: str = 'eng', config: str = '--oem 3 --psm 6'):
        self.language = language
        self.config = config

    def extract_text(self, image_bytes: bytes) -> OCRResult:
        """
        Extract text from image using Tesseract OCR

        Args:
            image_bytes: Image content as bytes

        Returns:
            OCRResult with extracted text and confidence scores
        """
        try:
            import pytesseract
            from PIL import Image
            import io

            start_time = time.time()

            # Load image from bytes
            image = Image.open(io.BytesIO(image_bytes))

            # Extract text
            text = pytesseract.image_to_string(image, lang=self.language, config=self.config)

            # Get detailed data including confidence scores
            data = pytesseract.image_to_data(image, lang=self.language, config=self.config, output_type=pytesseract.Output.DICT)

            # Calculate confidence scores
            confidences = []
            total_words = 0

            if data and 'conf' in data:
                for conf in data['conf']:
                    if conf != '-1':  # -1 indicates no confidence available
                        confidences.append(float(conf))
                        total_words += 1

            # Calculate overall confidence
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
            else:
                avg_confidence = 0.0

            processing_time = time.time() - start_time

            result = OCRResult(
                text=text.strip(),
                confidence_score=avg_confidence,
                word_confidences=confidences,
                processing_time=processing_time,
                page_count=1,  # Single page
                total_words=total_words
            )

            logger.info(f"OCR extracted {total_words} words with {avg_confidence:.1f}% confidence")
            return result

        except Exception as e:
            logger.error(f"OCR text extraction failed: {e}")
            raise

class TitleBlockParser:
    """[PDF001] Title Block Parser with bounding box detection"""

    def __init__(self):
        self.title_block_patterns = {
            "part_number": [
                r'PART\s*(?:NUMBER|NO\.?|NUM)\s*:?\s*([A-Z0-9\-_\.]+)',
                r'P/N\s*:?\s*([A-Z0-9\-_\.]+)',
                r'ITEM\s*(?:NUMBER|NO\.?|NUM)\s*:?\s*([A-Z0-9\-_\.]+)',
                r'DRAWING\s*(?:NUMBER|NO\.?|NUM)\s*:?\s*([A-Z0-9\-_\.]+)',
                r'DWG\s*(?:NO\.?|NUM)\s*:?\s*([A-Z0-9\-_\.]+)',
            ],
            "material": [
                r'MATERIAL\s*:?\s*([A-Z0-9\s\-\.]+)',
                r'MATL\s*:?\s*([A-Z0-9\s\-\.]+)',
                r'MATERIAL\s*SPEC\s*:?\s*([A-Z0-9\s\-\.]+)',
                r'ALLOY\s*:?\s*([A-Z0-9\s\-\.]+)',
                r'MATERIAL\s*TYPE\s*:?\s*([A-Z0-9\s\-\.]+)',
            ],
            "thickness": [
                r'THICKNESS\s*:?\s*([\d\.]+)\s*(in|mm|ga|gauge|"?)',
                r'THK\s*:?\s*([\d\.]+)\s*(in|mm|ga|gauge|"?)',
                r'GAUGE\s*:?\s*([\d\.]+)\s*(in|mm|ga|gauge|"?)',
                r'SIZE\s*:?\s*([\d\.]+)\s*(in|mm|ga|gauge|"?)',
                r'T\s*:?\s*([\d\.]+)\s*(in|mm|ga|gauge|"?)',
            ],
            "finish": [
                r'FINISH\s*:?\s*([A-Z0-9\s\-\.]+)',
                r'SURFACE\s*(?:FINISH)?\s*:?\s*([A-Z0-9\s\-\.]+)',
                r'COATING\s*:?\s*([A-Z0-9\s\-\.]+)',
                r'TREATMENT\s*:?\s*([A-Z0-9\s\-\.]+)',
            ],
            "customer": [
                r'CUSTOMER\s*:?\s*([A-Z0-9\s\&\-\.]+)',
                r'CLIENT\s*:?\s*([A-Z0-9\s\&\-\.]+)',
                r'COMPANY\s*:?\s*([A-Z0-9\s\&\-\.]+)',
                r'CUST\s*:?\s*([A-Z0-9\s\&\-\.]+)',
            ],
            "description": [
                r'DESCRIPTION\s*:?\s*([A-Z0-9\s\-\.\(\)]+)',
                r'DESC\s*:?\s*([A-Z0-9\s\-\.\(\)]+)',
                r'PART\s*(?:NAME|DESC)\s*:?\s*([A-Z0-9\s\-\.\(\)]+)',
                r'TITLE\s*:?\s*([A-Z0-9\s\-\.\(\)]+)',
            ],
            "quantity": [
                r'QUANTITY\s*:?\s*(\d+)',
                r'QTY\s*:?\s*(\d+)',
                r'AMOUNT\s*:?\s*(\d+)',
                r'Q\'TY\s*:?\s*(\d+)',
            ],
            "revision": [
                r'REV(?:ISION)?\s*:?\s*([A-Z0-9\-_\.]+)',
                r'REV\s*:?\s*([A-Z0-9\-_\.]+)',
                r'VERSION\s*:?\s*([A-Z0-9\-_\.]+)',
            ],
            "date": [
                r'DATE\s*:?\s*([\d/\-\.]+)',
                r'DRAWN\s*(?:DATE)?\s*:?\s*([\d/\-\.]+)',
                r'CREATED\s*:?\s*([\d/\-\.]+)',
            ]
        }

    def parse_title_block(self, pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse title block from PDF with bounding box detection

        Args:
            pdf_bytes: PDF file content as bytes
            filename: Original filename

        Returns:
            Dictionary with title block data and confidence scores
        """
        try:
            from pdfminer.pdfparser import PDFParser
            from pdfminer.pdfdocument import PDFDocument
            from pdfminer.pdfpage import PDFPage
            from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
            from pdfminer.layout import LAParams
            from pdfminer.converter import PDFPageAggregator
            import io

            # Parse PDF and get layout
            parser = PDFParser(io.BytesIO(pdf_bytes))
            document = PDFDocument(parser)

            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            # Process first page (title block usually on first page)
            first_page = next(PDFPage.create_pages(document))
            interpreter.process_page(first_page)
            layout = device.get_result()

            # Extract text elements with bounding boxes
            text_elements = self._extract_text_elements_with_bbox(layout)

            # Identify title block region
            title_block_region = self._identify_title_block_region(text_elements)

            # Extract data from title block region
            title_block_data = self._extract_data_from_region(text_elements, title_block_region)

            return {
                'title_block_found': len(title_block_data) > 0,
                'title_block_region': title_block_region,
                'extracted_fields': title_block_data,
                'confidence_score': self._calculate_title_block_confidence(title_block_data),
                'text_elements_count': len(text_elements)
            }

        except Exception as e:
            logger.warning(f"Title block parsing failed for {filename}: {e}")
            return {
                'title_block_found': False,
                'error': str(e),
                'extracted_fields': {},
                'confidence_score': 0.0
            }

    def _extract_text_elements_with_bbox(self, layout) -> List[Dict[str, Any]]:
        """Extract text elements with their bounding box coordinates"""
        elements = []

        def collect_text_elements(element, depth=0):
            if hasattr(element, 'get_text'):
                text = element.get_text().strip()
                if text and hasattr(element, 'bbox'):
                    bbox = element.bbox
                    elements.append({
                        'text': text,
                        'bbox': bbox,
                        'x0': bbox[0], 'y0': bbox[1], 'x1': bbox[2], 'y1': bbox[3],
                        'width': bbox[2] - bbox[0],
                        'height': bbox[3] - bbox[1],
                        'center_x': (bbox[0] + bbox[2]) / 2,
                        'center_y': (bbox[1] + bbox[3]) / 2
                    })

            # Recursively process child elements
            if hasattr(element, '_objs'):
                for child in element._objs:
                    collect_text_elements(child, depth + 1)

        collect_text_elements(layout)
        return elements

    def _identify_title_block_region(self, text_elements: List[Dict[str, Any]]) -> Dict[str, float]:
        """Identify the title block region based on text element clustering"""
        if not text_elements:
            return {'x0': 0, 'y0': 0, 'x1': 0, 'y1': 0}

        # Group elements by vertical position (rows)
        rows = {}
        for elem in text_elements:
            row_key = round(elem['center_y'], -1)  # Round to nearest 10
            if row_key not in rows:
                rows[row_key] = []
            rows[row_key].append(elem)

        # Find the densest region (likely title block)
        max_density = 0
        title_block_bounds = {'x0': float('inf'), 'y0': float('inf'), 'x1': 0, 'y1': 0}

        for row_y, row_elements in rows.items():
            if len(row_elements) >= 3:  # At least 3 elements in a row
                # Calculate row bounds
                row_x0 = min(e['x0'] for e in row_elements)
                row_x1 = max(e['x1'] for e in row_elements)
                row_width = row_x1 - row_x0

                # Look for consecutive rows with similar density
                consecutive_rows = 1
                total_height = row_elements[0]['height']

                # Check rows above and below
                for offset in [-1, 1]:
                    check_y = row_y + (offset * 50)  # Approximate row height
                    if check_y in rows and len(rows[check_y]) >= 2:
                        consecutive_rows += 1
                        total_height += rows[check_y][0]['height']

                density = consecutive_rows * len(row_elements) / max(total_height, 1)

                if density > max_density:
                    max_density = density
                    title_block_bounds = {
                        'x0': row_x0,
                        'y0': row_y - total_height,
                        'x1': row_x1,
                        'y1': row_y + row_elements[0]['height']
                    }

        return title_block_bounds

    def _extract_data_from_region(self, text_elements: List[Dict[str, Any]], region: Dict[str, float]) -> Dict[str, Any]:
        """Extract structured data from the identified title block region"""
        extracted_data = {}

        # Filter elements within the title block region
        region_elements = []
        for elem in text_elements:
            if (elem['x0'] >= region['x0'] and elem['x1'] <= region['x1'] and
                elem['y0'] >= region['y0'] and elem['y1'] <= region['y1']):
                region_elements.append(elem)

        # Sort by position (top-to-bottom, left-to-right)
        region_elements.sort(key=lambda e: (-e['center_y'], e['center_x']))

        # Combine text from elements for pattern matching
        combined_text = ' '.join(elem['text'] for elem in region_elements)

        # Apply regex patterns
        for field_name, patterns in self.title_block_patterns.items():
            best_match = None
            best_confidence = 0.0

            for pattern in patterns:
                matches = re.findall(pattern, combined_text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    match = matches[0]
                    if isinstance(match, tuple):
                        match = match[0] if len(match) > 0 else ''.join(match)

                    if isinstance(match, str) and match.strip():
                        confidence = self._calculate_field_confidence(match, field_name, region_elements)
                        if confidence > best_confidence:
                            best_match = match.strip()
                            best_confidence = confidence

            if best_match and best_confidence > 0.3:
                extracted_data[field_name] = {
                    'value': best_match,
                    'confidence': best_confidence,
                    'source': 'title_block_parser'
                }

        return extracted_data

    def _calculate_field_confidence(self, match: str, field_name: str, elements: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for extracted field"""
        confidence = 0.5  # Base confidence

        # Length bonus
        if len(match) > 3:
            confidence += 0.2

        # Format validation bonus
        if field_name == 'part_number' and re.match(r'^[A-Z0-9\-_\.]+$', match):
            confidence += 0.2
        elif field_name == 'thickness' and re.match(r'^[\d\.]+\s*(?:in|mm|ga)?', match):
            confidence += 0.2
        elif field_name == 'quantity' and match.isdigit():
            confidence += 0.2

        # Context bonus - check for related terms in nearby elements
        context_words = {
            'part_number': ['part', 'number', 'drawing', 'item'],
            'material': ['material', 'matl', 'alloy', 'steel'],
            'thickness': ['thickness', 'thk', 'gauge', 'size'],
            'customer': ['customer', 'client', 'company']
        }

        if field_name in context_words:
            for elem in elements:
                elem_text = elem['text'].lower()
                if any(word in elem_text for word in context_words[field_name]):
                    confidence += 0.1
                    break

        return min(confidence, 1.0)

    def _calculate_title_block_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate overall confidence in title block detection"""
        if not extracted_data:
            return 0.0

        # Count high-confidence extractions
        high_confidence_fields = sum(1 for field in extracted_data.values()
                                   if field.get('confidence', 0) > 0.7)

        # Base confidence on number of fields found
        field_count = len(extracted_data)
        confidence = min(field_count * 0.2, 0.8)  # Max 0.8 from field count

        # Bonus for high-confidence fields
        confidence += high_confidence_fields * 0.1

        return min(confidence, 1.0)


class OCRDataParser:
    """Parses structured data from OCR text"""

    def __init__(self):
        # Define regex patterns for common manufacturing document fields
        self.patterns = {
            "part_number": [
                r'PART\s*(?:NUMBER|NO\.?)\s*:\s*([A-Z0-9\-_\.]+)',
                r'P/N\s*:\s*([A-Z0-9\-_\.]+)',
                r'ITEM\s*(?:NUMBER|NO\.?)\s*:\s*([A-Z0-9\-_\.]+)',
                r'DRAWING\s*(?:NUMBER|NO\.?)\s*:\s*([A-Z0-9\-_\.]+)',
            ],
            "material": [
                r'MATERIAL\s*:\s*([A-Z\s]+)',
                r'MATL\s*:\s*([A-Z\s]+)',
                r'MATERIAL\s*SPEC\s*:\s*([A-Z\s]+)',
                r'ALLOY\s*:\s*([A-Z0-9\s]+)',
            ],
            "thickness": [
                r'THICKNESS\s*:\s*([\d\.]+)\s*(in|mm|ga|gauge)',
                r'THK\s*:\s*([\d\.]+)\s*(in|mm|ga|gauge)',
                r'GAUGE\s*:\s*([\d\.]+)\s*(in|mm|ga|gauge)',
                r'SIZE\s*:\s*([\d\.]+)\s*(in|mm|ga|gauge)',
            ],
            "finish": [
                r'FINISH\s*:\s*([A-Z0-9\s]+)',
                r'SURFACE\s*:\s*([A-Z0-9\s]+)',
                r'COATING\s*:\s*([A-Z0-9\s]+)',
            ],
            "customer": [
                r'CUSTOMER\s*:\s*([A-Z\s\&\-\.]+)',
                r'CLIENT\s*:\s*([A-Z\s\&\-\.]+)',
                r'COMPANY\s*:\s*([A-Z\s\&\-\.]+)',
            ],
            "description": [
                r'DESCRIPTION\s*:\s*([A-Z0-9\s\-\.]+)',
                r'DESC\s*:\s*([A-Z0-9\s\-\.]+)',
                r'PART\s*NAME\s*:\s*([A-Z0-9\s\-\.]+)',
            ],
            "quantity": [
                r'QUANTITY\s*:\s*(\d+)',
                r'QTY\s*:\s*(\d+)',
                r'AMOUNT\s*:\s*(\d+)',
            ]
        }

        # Initialize title block parser
        self.title_block_parser = TitleBlockParser()

    def parse_structured_data(self, ocr_text: str, confidence_threshold: float = 0.3, pdf_bytes: bytes = None, filename: str = None) -> Dict[str, Any]:
        """
        Parse structured data from OCR text using regex patterns and title block detection

        Args:
            ocr_text: Raw OCR text
            confidence_threshold: Minimum confidence for extracted data
            pdf_bytes: Optional PDF bytes for title block parsing
            filename: Optional filename for title block parsing

        Returns:
            Dictionary of extracted fields with confidence scores
        """
        extracted_data = {}
        confidence_scores = {}

        # Clean and normalize text
        clean_text = self._clean_text(ocr_text)

        # [PDF001] Try title block parsing if PDF bytes available
        title_block_data = {}
        if pdf_bytes and filename:
            try:
                title_block_result = self.title_block_parser.parse_title_block(pdf_bytes, filename)
                if title_block_result.get('title_block_found', False):
                    title_block_data = title_block_result.get('extracted_fields', {})
                    logger.info(f"Title block parsing successful for {filename}")
            except Exception as e:
                logger.warning(f"Title block parsing failed: {e}")

        # Extract data using patterns
        for field_name, patterns in self.patterns.items():
            best_match = None
            best_confidence = 0.0
            source = 'regex_pattern'

            # First, check if we have title block data for this field
            if field_name in title_block_data:
                tb_field = title_block_data[field_name]
                if tb_field.get('confidence', 0) > best_confidence:
                    best_match = tb_field['value']
                    best_confidence = tb_field['confidence']
                    source = 'title_block'

            # If title block didn't give us good data, try regex patterns
            if best_confidence < confidence_threshold:
                for pattern in patterns:
                    matches = re.findall(pattern, clean_text, re.IGNORECASE | re.MULTILINE)
                    if matches:
                        # Use the first match (most likely to be correct)
                        match = matches[0]

                        # Handle tuple results from regex (when capture groups are used)
                        if isinstance(match, tuple):
                            # Use the first capture group if available, otherwise join all groups
                            match = match[0] if len(match) > 0 else ''.join(match)

                        # Ensure match is a string
                        if not isinstance(match, str):
                            match = str(match)

                        # Calculate confidence based on pattern specificity and text quality
                        confidence = self._calculate_extraction_confidence(match, pattern, clean_text)

                        if confidence > best_confidence:
                            best_match = match
                            best_confidence = confidence
                            source = 'regex_pattern'

            if best_match and best_confidence >= confidence_threshold:
                extracted_data[field_name] = {
                    'value': best_match,
                    'confidence': best_confidence,
                    'source': source
                }
                confidence_scores[field_name] = best_confidence

        # [PDF002] Parse outside processes with comprehensive patterns
        outside_processes = self._parse_outside_processes(clean_text)
        if outside_processes:
            extracted_data['outside_processes'] = outside_processes

        return {
            'fields': extracted_data,
            'confidence_scores': confidence_scores,
            'title_block_data': title_block_data,
            'extraction_summary': {
                'total_fields_attempted': len(self.patterns),
                'fields_extracted': len(extracted_data),
                'average_confidence': sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.0,
                'title_block_used': len(title_block_data) > 0
            }
        }

    def _parse_outside_processes(self, text: str) -> List[Dict[str, Any]]:
        """[PDF002] Parse outside processes with comprehensive regex patterns"""
        outside_processes = []

        # Comprehensive outside process patterns
        process_patterns = [
            # Standard outside process notations
            r'OUTSIDE\s*PROCESS\s*:?\s*([A-Z\s\-\.]+)',
            r'OUTSIDE\s*PROC\s*:?\s*([A-Z\s\-\.]+)',
            r'EXT\s*PROCESS\s*:?\s*([A-Z\s\-\.]+)',
            r'EXTERNAL\s*PROCESS\s*:?\s*([A-Z\s\-\.]+)',

            # Specific process types
            r'HEAT\s*TREAT\s*:?\s*([A-Z\s\-\.]+)',
            r'PLATING\s*:?\s*([A-Z\s\-\.]+)',
            r'COATING\s*:?\s*([A-Z\s\-\.]+)',
            r'PAINT\s*:?\s*([A-Z\s\-\.]+)',
            r'WELDING\s*:?\s*([A-Z\s\-\.]+)',
            r'MACHINING\s*:?\s*([A-Z\s\-\.]+)',
            r'GRINDING\s*:?\s*([A-Z\s\-\.]+)',
            r'POLISHING\s*:?\s*([A-Z\s\-\.]+)',

            # Vendor/supplier references
            r'SUPPLIER\s*:?\s*([A-Z\s\-\.]+)',
            r'VENDOR\s*:?\s*([A-Z\s\-\.]+)',
            r'SUBCONTRACT\s*:?\s*([A-Z\s\-\.]+)',
            r'SUB\s*CONTRACTOR\s*:?\s*([A-Z\s\-\.]+)',

            # Process specifications
            r'SPEC\s*:?\s*([A-Z0-9\s\-\.]+)',
            r'SPECIFICATION\s*:?\s*([A-Z0-9\s\-\.]+)',
            r'FINISH\s*SPEC\s*:?\s*([A-Z0-9\s\-\.]+)',
        ]

        # Additional patterns for process details
        detail_patterns = [
            r'TEMPERATURE\s*:?\s*([\d\s\-\.°CF]+)',
            r'TIME\s*:?\s*([\d\s\-\.hoursmin]+)',
            r'THICKNESS\s*:?\s*([\d\s\-\.]+)',
            r'MATERIAL\s*:?\s*([A-Z\s\-\.]+)',
            r'NOTES?\s*:?\s*([A-Z0-9\s\-\.\(\)]+)',
        ]

        found_processes = set()

        # Extract main processes
        for pattern in process_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if len(match) > 0 else ''.join(match)

                if isinstance(match, str) and match.strip():
                    process_name = match.strip()
                    if process_name not in found_processes and len(process_name) > 2:
                        found_processes.add(process_name)

                        # Try to extract additional details for this process
                        process_details = self._extract_process_details(text, process_name)

                        outside_processes.append({
                            'process_name': process_name,
                            'details': process_details,
                            'confidence': self._calculate_process_confidence(process_name, process_details),
                            'source': 'regex_pattern'
                        })

        return outside_processes

    def _extract_process_details(self, text: str, process_name: str) -> Dict[str, str]:
        """Extract additional details for a specific outside process"""
        details = {}

        # Look for details in the vicinity of the process name
        # Search in a window around the process name
        process_lower = process_name.lower()
        lines = text.split('\n')

        for i, line in enumerate(lines):
            if process_lower in line.lower():
                # Look at surrounding lines for details
                start_line = max(0, i - 2)
                end_line = min(len(lines), i + 3)

                context = '\n'.join(lines[start_line:end_line])

                # Extract common detail patterns
                temp_match = re.search(r'TEMP(?:ERATURE)?\s*:?\s*([\d\s\-\.°CF]+)', context, re.IGNORECASE)
                if temp_match:
                    details['temperature'] = temp_match.group(1).strip()

                time_match = re.search(r'TIME\s*:?\s*([\d\s\-\.hoursmin]+)', context, re.IGNORECASE)
                if time_match:
                    details['time'] = time_match.group(1).strip()

                spec_match = re.search(r'SPEC\s*:?\s*([A-Z0-9\s\-\.]+)', context, re.IGNORECASE)
                if spec_match:
                    details['specification'] = spec_match.group(1).strip()

                notes_match = re.search(r'NOTES?\s*:?\s*([A-Z0-9\s\-\.\(\)]+)', context, re.IGNORECASE)
                if notes_match:
                    details['notes'] = notes_match.group(1).strip()

                break  # Found the process, no need to continue

        return details

    def _calculate_process_confidence(self, process_name: str, details: Dict[str, str]) -> float:
        """Calculate confidence score for outside process extraction"""
        confidence = 0.5  # Base confidence

        # Length bonus
        if len(process_name) > 5:
            confidence += 0.2

        # Detail bonus
        if details:
            confidence += len(details) * 0.1

        # Known process type bonus
        known_processes = [
            'heat treat', 'plating', 'coating', 'painting', 'welding',
            'machining', 'grinding', 'polishing', 'anodizing', 'passivation'
        ]
        if any(known in process_name.lower() for known in known_processes):
            confidence += 0.2

        return min(confidence, 1.0)

    def _clean_text(self, text) -> str:
        """Clean and normalize OCR text"""
        # Ensure text is a string
        if isinstance(text, tuple):
            logger.warning(f"Received tuple instead of string: {text}")
            text = str(text[0]) if text else ""
        elif not isinstance(text, str):
            logger.warning(f"Received non-string type: {type(text)}, converting to string")
            text = str(text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove non-printable characters
        text = re.sub(r'[^\x20-\x7E\n]', '', text)
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        return text.strip()

    def _calculate_extraction_confidence(self, match: str, pattern: str, full_text: str) -> float:
        """Calculate confidence score for extracted data"""
        confidence = 0.5  # Base confidence

        # Pattern specificity bonus
        if len(pattern.split()) > 3:  # More specific patterns
            confidence += 0.2

        # Match length bonus (longer matches are more reliable)
        if len(match) > 5:
            confidence += 0.1

        # Context relevance bonus
        context_words = ['part', 'material', 'thickness', 'drawing', 'customer']
        match_lower = match.lower()
        if any(word in match_lower for word in context_words):
            confidence += 0.1

        # Clean match bonus (no weird characters)
        if re.match(r'^[A-Z0-9\s\-\.\&]+$', match):
            confidence += 0.1

        return min(confidence, 1.0)  # Cap at 1.0

class PDFFormatScoreCalculator:
    """[PDF000] PDF Format Score Calculator - Evaluates PDF quality and format"""

    def calculate_format_score(self, pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Calculate comprehensive format score for PDF documents

        Args:
            pdf_bytes: PDF file content as bytes
            filename: Original filename

        Returns:
            Dictionary with format scores and quality metrics
        """
        try:
            from pdfminer.pdfparser import PDFParser
            from pdfminer.pdfdocument import PDFDocument
            from pdfminer.pdfpage import PDFPage
            from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
            from pdfminer.layout import LAParams
            from pdfminer.converter import PDFPageAggregator
            import io

            # Initialize PDF analysis
            parser = PDFParser(io.BytesIO(pdf_bytes))
            document = PDFDocument(parser)

            # Basic document properties
            doc_info = document.info[0] if document.info else {}
            page_count = len(list(PDFPage.create_pages(document)))

            # Analyze first page for detailed metrics
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            first_page = next(PDFPage.create_pages(document))
            interpreter.process_page(first_page)
            layout = device.get_result()

            # Calculate various quality metrics
            scores = self._calculate_quality_metrics(layout, page_count, doc_info, filename)

            return {
                'overall_score': scores['overall'],
                'quality_metrics': scores,
                'document_info': {
                    'page_count': page_count,
                    'has_text': scores['text_content'] > 0.3,
                    'has_images': scores['image_content'] > 0.1,
                    'is_scanned': scores['scanned_probability'] > 0.7,
                    'title_block_detected': scores['title_block_score'] > 0.5
                },
                'recommendations': self._generate_recommendations(scores)
            }

        except Exception as e:
            logger.warning(f"PDF format scoring failed for {filename}: {e}")
            return {
                'overall_score': 0.1,
                'quality_metrics': {'error': str(e)},
                'document_info': {'page_count': 0, 'error': True},
                'recommendations': ['Unable to analyze PDF format']
            }

    def _calculate_quality_metrics(self, layout, page_count: int, doc_info: dict, filename: str) -> Dict[str, float]:
        """Calculate detailed quality metrics"""
        metrics = {}

        # Text content score (0-1)
        text_elements = []
        image_elements = []

        def collect_elements(element, depth=0):
            if hasattr(element, 'get_text'):
                text = element.get_text().strip()
                if text:
                    text_elements.append(text)
            if hasattr(element, 'bbox'):
                # Check if element is likely an image (large bbox, no text)
                bbox = element.bbox
                width = bbox[2] - bbox[0]
                height = bbox[3] - bbox[1]
                area = width * height
                if area > 10000 and not hasattr(element, 'get_text'):  # Large area, likely image
                    image_elements.append(element)

        # Recursively collect elements
        if hasattr(layout, '_objs'):
            for obj in layout._objs:
                collect_elements(obj)

        # Text content score
        total_text_length = sum(len(text) for text in text_elements)
        metrics['text_content'] = min(total_text_length / 1000, 1.0)  # Normalize

        # Image content score
        metrics['image_content'] = min(len(image_elements) * 0.2, 1.0)

        # Scanned document probability
        scanned_indicators = 0
        if metrics['image_content'] > metrics['text_content']:
            scanned_indicators += 0.5
        if len(text_elements) < 10:
            scanned_indicators += 0.3
        if page_count > 5:
            scanned_indicators += 0.2
        metrics['scanned_probability'] = scanned_indicators

        # Title block detection score
        title_block_score = 0
        title_keywords = ['part', 'number', 'material', 'thickness', 'drawing', 'customer']
        for text in text_elements:
            text_lower = text.lower()
            if any(keyword in text_lower for keyword in title_keywords):
                title_block_score += 0.2
        metrics['title_block_score'] = min(title_block_score, 1.0)

        # Document structure score
        structure_score = 0
        if doc_info.get('Title'):
            structure_score += 0.2
        if doc_info.get('Author'):
            structure_score += 0.1
        if doc_info.get('Subject'):
            structure_score += 0.1
        if doc_info.get('Creator'):
            structure_score += 0.1
        if page_count > 0:
            structure_score += 0.2
        metrics['structure_score'] = structure_score

        # Overall score calculation
        weights = {
            'text_content': 0.3,
            'image_content': 0.2,
            'title_block_score': 0.25,
            'structure_score': 0.25
        }

        overall = sum(metrics[key] * weight for key, weight in weights.items() if key in metrics)
        metrics['overall'] = overall

        return metrics

    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on scores"""
        recommendations = []

        if scores.get('text_content', 0) < 0.3:
            recommendations.append("Low text content detected - may require OCR processing")

        if scores.get('scanned_probability', 0) > 0.7:
            recommendations.append("Document appears to be scanned - OCR recommended")

        if scores.get('title_block_score', 0) < 0.5:
            recommendations.append("Title block not clearly detected - manual review recommended")

        if scores.get('structure_score', 0) < 0.3:
            recommendations.append("Document structure incomplete - may affect parsing accuracy")

        if not recommendations:
            recommendations.append("Document format appears suitable for automated processing")

        return recommendations


class PDFOCRProcessor:
    """Main PDF OCR processor combining all components"""

    def __init__(self, dpi: int = 300, language: str = 'eng'):
        self.image_converter = PDFImageConverter(dpi=dpi)
        self.text_extractor = OCRTextExtractor(language=language)
        self.data_parser = OCRDataParser()
        self.format_calculator = PDFFormatScoreCalculator()

    def process_pdf(self, pdf_bytes: bytes, filename: str) -> PDFOCRResult:
        """
        Process a PDF file with OCR and extract structured data

        Args:
            pdf_bytes: PDF file content as bytes
            filename: Original filename

        Returns:
            PDFOCRResult with OCR results and extracted data
        """
        start_time = time.time()
        errors = []

        try:
            # [PDF000] Calculate PDF format score first
            logger.info(f"Calculating PDF format score for {filename}")
            format_score = self.format_calculator.calculate_format_score(pdf_bytes, filename)

            # Determine processing strategy based on format score
            should_use_ocr = (
                format_score['overall_score'] < 0.5 or
                format_score['document_info'].get('is_scanned', False) or
                not format_score['document_info'].get('has_text', True)
            )

            if should_use_ocr:
                logger.info(f"Using OCR processing for {filename} (format score: {format_score['overall_score']:.2f})")
                return self._process_with_ocr(pdf_bytes, filename, format_score, start_time)
            else:
                logger.info(f"Using text extraction for {filename} (format score: {format_score['overall_score']:.2f})")
                return self._process_with_text_extraction(pdf_bytes, filename, format_score, start_time)

        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            processing_time = time.time() - start_time

            return PDFOCRResult(
                success=False,
                filename=filename,
                ocr_results=[],
                extracted_data={'format_score': {'overall_score': 0.0, 'error': str(e)}},
                overall_confidence=0.0,
                processing_time=processing_time,
                errors=[str(e)] + errors
            )

    def _process_with_ocr(self, pdf_bytes: bytes, filename: str, format_score: Dict[str, Any], start_time: float) -> PDFOCRResult:
        """Process PDF using OCR (for scanned or low-quality documents)"""
        errors = []

        try:
            # Convert PDF to images
            logger.info(f"Converting PDF {filename} to images")
            image_bytes_list = self.image_converter.convert_to_images(pdf_bytes)

            if not image_bytes_list:
                raise ValueError("No images generated from PDF")

            # Extract text from each page
            ocr_results = []
            all_text = []

            for i, image_bytes in enumerate(image_bytes_list):
                try:
                    logger.info(f"Processing page {i+1}/{len(image_bytes_list)}")
                    ocr_result = self.text_extractor.extract_text(image_bytes)
                    ocr_results.append(ocr_result)
                    all_text.append(ocr_result.text)
                except Exception as e:
                    error_msg = f"Failed to process page {i+1}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            # Combine text from all pages
            combined_text = '\n\n'.join(all_text)

            # Parse structured data with title block detection
            logger.info("Parsing structured data from OCR text with title block detection")
            parsed_data = self.data_parser.parse_structured_data(combined_text, pdf_bytes=pdf_bytes, filename=filename)

            # Add format score to extracted data
            parsed_data['format_score'] = format_score

            # Calculate overall confidence
            if ocr_results:
                overall_confidence = sum(r.confidence_score for r in ocr_results) / len(ocr_results)
            else:
                overall_confidence = 0.0

            processing_time = time.time() - start_time

            result = PDFOCRResult(
                success=len(ocr_results) > 0,
                filename=filename,
                ocr_results=ocr_results,
                extracted_data=parsed_data,
                overall_confidence=overall_confidence,
                processing_time=processing_time,
                errors=errors
            )

            logger.info(f"PDF OCR processing completed: {len(ocr_results)} pages, {overall_confidence:.1f}% confidence")
            return result

        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            processing_time = time.time() - start_time

            return PDFOCRResult(
                success=False,
                filename=filename,
                ocr_results=[],
                extracted_data={'format_score': format_score},
                overall_confidence=0.0,
                processing_time=processing_time,
                errors=[str(e)] + errors
            )

    def _process_with_text_extraction(self, pdf_bytes: bytes, filename: str, format_score: Dict[str, Any], start_time: float) -> PDFOCRResult:
        """Process PDF using direct text extraction (for high-quality text-based PDFs)"""
        try:
            from pdfminer.high_level import extract_text
            import io

            # Extract text directly
            text_content = extract_text(io.BytesIO(pdf_bytes))

            # Create mock OCR result for compatibility
            mock_ocr_result = OCRResult(
                text=text_content,
                confidence_score=0.95,  # High confidence for direct text extraction
                word_confidences=[],  # Not available from pdfminer
                processing_time=time.time() - start_time,
                page_count=1,
                total_words=len(text_content.split())
            )

            # Parse structured data
            parsed_data = self.data_parser.parse_structured_data(text_content)
            parsed_data['format_score'] = format_score
            parsed_data['processing_method'] = 'direct_text_extraction'

            processing_time = time.time() - start_time

            result = PDFOCRResult(
                success=True,
                filename=filename,
                ocr_results=[mock_ocr_result],
                extracted_data=parsed_data,
                overall_confidence=0.95,
                processing_time=processing_time,
                errors=[]
            )

            logger.info(f"Direct text extraction completed for {filename}")
            return result

        except Exception as e:
            logger.warning(f"Direct text extraction failed, falling back to OCR: {e}")
            # Fallback to OCR processing
            return self._process_with_ocr(pdf_bytes, filename, format_score, start_time)

# Convenience function for easy integration
def process_pdf_with_ocr(pdf_bytes: bytes, filename: str) -> PDFOCRResult:
    """Convenience function to process PDF with OCR"""
    processor = PDFOCRProcessor()
    return processor.process_pdf(pdf_bytes, filename)
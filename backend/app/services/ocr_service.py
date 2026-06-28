import os
import logging
from typing import Optional
from PIL import Image
import pdfplumber
from app.utils.response_utils import CustomHTTPException

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        self._reader = None

    @property
    def reader(self):
        """
        Lazy-loads EasyOCR reader to save startup memory.
        """
        if self._reader is None:
            try:
                import easyocr
                # Initialize EasyOCR reader for English language.
                # Runs on GPU if CUDA is available, otherwise falls back to CPU.
                logger.info("Initializing EasyOCR Reader...")
                self._reader = easyocr.Reader(['en'], gpu=False)
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR reader: {e}")
                raise CustomHTTPException(
                    status_code=500,
                    detail=f"OCR Engine failed to initialize: {str(e)}",
                    error_code="OCR_INIT_FAILED"
                )
        return self._reader

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extracts text from a digital PDF using pdfplumber.
        If no text is returned (scanned PDF), falls back to OCR on rendered pages.
        """
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber failed reading digital PDF: {e}. Falling back to OCR.")
            
        # If text is empty, it might be a scanned PDF. Apply OCR to pages if possible.
        if not text.strip():
            logger.info("No digital text found. Reverting to scanned PDF OCR fallback.")
            text = self.extract_text_scanned_pdf(file_path)
            
        return text

    def extract_text_scanned_pdf(self, file_path: str) -> str:
        """
        OCR fallback for scanned PDFs. Converts PDF pages to images and runs OCR.
        For simplicity in python dependencies (avoiding system pdf2image/poppler requirement),
        if pdfplumber provides page images we use those, or we can use pdfplumber's `to_image()`.
        """
        text_list = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for idx, page in enumerate(pdf.pages):
                    # Convert page to high-res image
                    try:
                        im = page.to_image(resolution=150)
                        temp_img_path = f"{file_path}_page_{idx}.png"
                        im.save(temp_img_path, format="PNG")
                        
                        page_text = self.extract_text_from_image(temp_img_path)
                        text_list.append(page_text)
                        
                        # Clean up temp image
                        if os.path.exists(temp_img_path):
                            os.remove(temp_img_path)
                    except Exception as page_err:
                        logger.error(f"Error rendering/processing page {idx} image: {page_err}")
                        continue
        except Exception as e:
            logger.error(f"Failed scanning PDF: {e}")
            
        return "\n".join(text_list)

    def extract_text_from_image(self, file_path: str) -> str:
        """
        Extracts text from PNG, JPG, or JPEG image using EasyOCR.
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise ValueError("Image file path does not exist.")
                
            # Perform OCR
            results = self.reader.readtext(file_path, detail=0)
            return "\n".join(results)
        except Exception as e:
            logger.error(f"EasyOCR image text extraction failed: {e}")
            raise CustomHTTPException(
                status_code=500,
                detail=f"Failed to extract text from image: {str(e)}",
                error_code="OCR_IMAGE_EXTRACTION_FAILED"
            )

    def extract_text(self, file_path: str, ext: str) -> str:
        """
        General OCR method matching file extension.
        """
        ext = ext.lower()
        if ext == ".pdf":
            extracted = self.extract_text_from_pdf(file_path)
        elif ext in {".png", ".jpg", ".jpeg"}:
            extracted = self.extract_text_from_image(file_path)
        else:
            raise CustomHTTPException(
                status_code=400,
                detail=f"Unsupported extension for OCR: {ext}",
                error_code="UNSUPPORTED_OCR_EXTENSION"
            )
            
        if not extracted.strip():
            logger.warning("OCR finished but returned completely empty text.")
            
        return extracted

ocr_service = OCRService()

import logging
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

def extract_text(image_path: str) -> str:
    try:
        return pytesseract.image_to_string(Image.open(image_path))
    except Exception:
        logger.exception(f"Failed to extract text from image: {image_path}")
        return ""

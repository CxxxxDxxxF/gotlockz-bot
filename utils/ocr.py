from PIL import Image
import pytesseract

def extract_text(image_path: str) -> str:
    """
    Load the image at image_path, convert to grayscale,
    run Tesseract OCR, and return the raw text.
    """
    img = Image.open(image_path)
    gray = img.convert("L")
    text = pytesseract.image_to_string(gray)
    return text

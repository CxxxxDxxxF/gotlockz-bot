from PIL import Image
import pytesseract

def extract_text(image_path: str) -> str:
    """
    Load the image at image_path, convert to grayscale,
    run Tesseract OCR, and return the raw text.
    """
    img = Image.open(image_path)
    gray = img.convert("L")
    # If you want binarization uncomment the next line:
    # gray = gray.point(lambda x: 0 if x < 128 else 255, '1')
    text = pytesseract.image_to_string(gray)
    return text

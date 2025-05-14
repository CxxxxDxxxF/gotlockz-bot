
from PIL import Image
import pytesseract
from io import BytesIO
import requests

def extract_text(image_url: str) -> str:
    try:
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"Error processing image: {e}"

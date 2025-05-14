
import easyocr
import numpy as np
from PIL import Image

# Initialize EasyOCR reader once
reader = easyocr.Reader(['en'], gpu=False)

def extract_text(image):
    # Convert PIL image to numpy array
    cv_img = np.array(image)
    if len(cv_img.shape) == 3:  # Handle both RGB and grayscale
        cv_img = cv_img[:, :, ::-1]  # RGB to BGR for EasyOCR
    
    # Run EasyOCR
    try:
        lines = reader.readtext(cv_img, detail=0)
        # Filter empty lines and strip whitespace
        return [line.strip() for line in lines if line.strip()]
    except Exception as e:
        print(f"OCR Error: {e}")
        return []

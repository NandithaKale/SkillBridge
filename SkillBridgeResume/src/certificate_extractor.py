import re
from PIL import Image
import io

try:
    import pytesseract
    # Set the path to tesseract executable (Windows)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️  pytesseract not installed. OCR features will be limited.")

class CertificateExtractor:
    """Extract grade/score from certificate images using OCR"""
    
    def __init__(self):
        pass
    
    def extract_from_image(self, image_file):
        """
        Extract only the GRADE/SCORE from certificate image
        Returns: dict with only 'grade' field
        """
        if not OCR_AVAILABLE:
            return {'grade': None}
        
        try:
            # Open image
            image = Image.open(image_file)
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            # Extract only grade
            grade = self._extract_grade(text)
            
            return {'grade': grade}
        
        except Exception as e:
            print(f"OCR Error: {e}")
            return {'grade': None}
    
    def _extract_grade(self, text):
        """Extract grade/score percentage from certificate text"""
        # Look for various grade patterns
        patterns = [
            r'score[:\s]+(\d+\.?\d*)%?',           # "Score: 85" or "Score: 85%"
            r'grade[:\s]+(\d+\.?\d*)%?',           # "Grade: 90"
            r'marks[:\s]+(\d+\.?\d*)%?',           # "Marks: 95"
            r'percentage[:\s]+(\d+\.?\d*)%?',      # "Percentage: 88"
            r'result[:\s]+(\d+\.?\d*)%?',          # "Result: 92"
            r'(\d{2})\.?\d*\s*%',                  # "85%" or "85.5%"
            r'(\d{2})\.?\d*\s*/\s*100',            # "85/100"
            r'secured[:\s]+(\d+\.?\d*)%?',         # "Secured: 90"
        ]
        
        text_lower = text.lower()
        
        # Try each pattern
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    score = float(match)
                    # Validate score is reasonable (0-100)
                    if 0 <= score <= 100:
                        return int(score)
                except ValueError:
                    continue
        
        # If no valid score found, return None
        return None
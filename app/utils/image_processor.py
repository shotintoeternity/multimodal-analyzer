import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import logging
from typing import Dict, List, Any, Optional, Tuple

class ImageProcessor:
    """Process and analyze technical images, diagrams, and screenshots"""
    
    def __init__(self):
        # Configure pytesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
        pass
    
    def preprocess(self, image_data: bytes) -> np.ndarray:
        """
        Preprocess the image for better analysis
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Processed image as numpy array
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                raise ValueError("Failed to decode image")
            
            # Basic preprocessing
            # 1. Resize if too large
            max_dim = 1280
            h, w = img.shape[:2]
            if max(h, w) > max_dim:
                scale = max_dim / max(h, w)
                img = cv2.resize(img, (int(w * scale), int(h * scale)))
            
            # 2. Enhance contrast for better feature detection
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            enhanced_lab = cv2.merge((cl, a, b))
            enhanced_img = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            return enhanced_img
            
        except Exception as e:
            logging.error(f"Error preprocessing image: {str(e)}")
            raise
    
    def extract_text(self, image: np.ndarray) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image: Preprocessed image as numpy array
            
        Returns:
            Extracted text
        """
        try:
            # Convert OpenCV image to PIL format for pytesseract
            pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(pil_img)
            
            return text.strip()
            
        except Exception as e:
            logging.error(f"Error extracting text: {str(e)}")
            return ""
    
    def detect_image_type(self, image: np.ndarray) -> str:
        """
        Detect the type of technical image (diagram, screenshot, code snippet, etc.)
        
        Args:
            image: Preprocessed image
            
        Returns:
            Image type classification
        """
        # This is a simplified implementation
        # A more robust solution would use a trained classifier
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Check for characteristics of different image types
        
        # 1. Check if it's likely a screenshot (many straight edges, UI elements)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
        
        if lines is not None and len(lines) > 20:
            # Many straight lines often indicate a UI screenshot
            return "screenshot"
        
        # 2. Check if it's likely a diagram (fewer straight lines, shapes)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 5 and len(contours) < 50:
            return "diagram"
        
        # 3. Check if it's likely code (text-heavy, monospaced)
        text = self.extract_text(image)
        code_indicators = ["def ", "class ", "function", "import ", "var ", "const ", "if ", "for ", "{", "}", "=>"]
        if any(indicator in text for indicator in code_indicators):
            return "code_snippet"
        
        # 4. Check if it's likely a terminal/console output
        terminal_indicators = ["$", ">", "#", "~", "error:", "warning:", "sudo", "npm", "pip"]
        if any(indicator in text for indicator in terminal_indicators):
            return "terminal_output"
        
        # Default
        return "unknown"
    
    def extract_features(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract relevant features from the image
        
        Args:
            image: Preprocessed image
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Determine image type
        image_type = self.detect_image_type(image)
        features["image_type"] = image_type
        
        # Extract text
        text = self.extract_text(image)
        features["text"] = text
        
        # Extract colors (simplified)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        features["dominant_colors"] = self._extract_dominant_colors(hsv)
        
        # Extract shapes if it's a diagram
        if image_type == "diagram":
            features["shapes"] = self._extract_shapes(image)
        
        # Extract UI elements if it's a screenshot
        if image_type == "screenshot":
            features["ui_elements"] = self._detect_ui_elements(image)
        
        # Look for error indicators
        features["potential_errors"] = self._detect_errors(image, text)
        
        return features
    
    def _extract_dominant_colors(self, hsv_image: np.ndarray, num_colors: int = 3) -> List[Dict[str, Any]]:
        """Extract dominant colors from HSV image"""
        # Reshape the image to be a list of pixels
        pixels = hsv_image.reshape((-1, 3))
        
        # Convert to float32
        pixels = np.float32(pixels)
        
        # Define criteria and apply kmeans
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert back to uint8
        centers = np.uint8(centers)
        
        # Count occurrences of each label
        unique_labels, counts = np.unique(labels, return_counts=True)
        
        # Sort by frequency
        sorted_indices = np.argsort(-counts)
        
        # Get the RGB values of the centers
        colors = []
        for idx in sorted_indices:
            center = centers[idx]
            # Convert HSV to RGB
            rgb = cv2.cvtColor(np.uint8([[center]]), cv2.COLOR_HSV2RGB)[0][0]
            colors.append({
                "rgb": rgb.tolist(),
                "percentage": counts[idx] / len(labels) * 100
            })
        
        return colors
    
    def _extract_shapes(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Extract shapes from diagram images"""
        shapes = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Skip very small contours
            if cv2.contourArea(contour) < 100:
                continue
                
            # Approximate the contour
            epsilon = 0.04 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Determine shape type
            shape_type = "unknown"
            if len(approx) == 3:
                shape_type = "triangle"
            elif len(approx) == 4:
                # Check if it's a square or rectangle
                aspect_ratio = float(w) / h
                if 0.95 <= aspect_ratio <= 1.05:
                    shape_type = "square"
                else:
                    shape_type = "rectangle"
            elif len(approx) == 5:
                shape_type = "pentagon"
            elif len(approx) == 6:
                shape_type = "hexagon"
            elif len(approx) > 10:
                shape_type = "circle"
            
            shapes.append({
                "type": shape_type,
                "position": (x, y),
                "size": (w, h),
                "area": cv2.contourArea(contour)
            })
        
        return shapes
    
    def _detect_ui_elements(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect UI elements in screenshots"""
        ui_elements = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive threshold
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        
        # Find contours
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process contours to identify UI elements
        for i, contour in enumerate(contours):
            # Skip very small contours
            if cv2.contourArea(contour) < 100:
                continue
                
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Extract the region
            roi = image[y:y+h, x:x+w]
            
            # Try to classify the UI element (simplified)
            element_type = self._classify_ui_element(roi, w, h)
            
            if element_type:
                ui_elements.append({
                    "type": element_type,
                    "position": (x, y),
                    "size": (w, h)
                })
        
        return ui_elements
    
    def _classify_ui_element(self, roi: np.ndarray, width: int, height: int) -> Optional[str]:
        """Classify UI element type based on appearance"""
        # This is a simplified implementation
        # A more robust solution would use a trained classifier
        
        aspect_ratio = float(width) / height if height > 0 else 0
        
        # Button detection (typically rectangular with moderate aspect ratio)
        if 1.5 <= aspect_ratio <= 5 and 20 <= height <= 60:
            return "button"
        
        # Text field detection (typically rectangular with larger aspect ratio)
        if 3 <= aspect_ratio <= 10 and 20 <= height <= 40:
            return "text_field"
        
        # Checkbox detection (small square)
        if 0.9 <= aspect_ratio <= 1.1 and 10 <= height <= 30:
            return "checkbox"
        
        # Dropdown detection
        if 3 <= aspect_ratio <= 8 and 20 <= height <= 40:
            # Check for dropdown arrow
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 2:
                return "dropdown"
        
        # Icon detection (small, roughly square)
        if 0.8 <= aspect_ratio <= 1.2 and 16 <= height <= 64:
            return "icon"
        
        # Menu item detection (wide rectangle)
        if 4 <= aspect_ratio <= 15 and 20 <= height <= 40:
            return "menu_item"
        
        return None
    
    def _detect_errors(self, image: np.ndarray, text: str) -> List[str]:
        """Detect potential error indicators in the image"""
        errors = []
        
        # Check for error text
        error_keywords = ["error", "exception", "failed", "warning", "invalid", "not found", "undefined"]
        for keyword in error_keywords:
            if keyword.lower() in text.lower():
                # Find the line containing the error
                lines = text.split('\n')
                for line in lines:
                    if keyword.lower() in line.lower():
                        errors.append(line.strip())
        
        # Check for error colors (red typically indicates errors)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Red color range in HSV
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        # Create masks for red regions
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 + mask2
        
        # Check if there are significant red regions
        red_pixel_count = np.count_nonzero(red_mask)
        if red_pixel_count > 500:  # Arbitrary threshold
            errors.append("Red color detected, possibly indicating an error")
        
        return errors

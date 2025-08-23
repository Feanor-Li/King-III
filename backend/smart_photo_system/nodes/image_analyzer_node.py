import cv2
import numpy as np
from PIL import Image, ImageStat
from typing import Dict, Any, Tuple
from .base import BaseNode
from ..models.state import PhotoSystemState, ImageAnalysis, CameraParams


class ImageAnalyzerNode(BaseNode):
    """Image analysis node"""
    
    def __init__(self):
        super().__init__("ImageAnalyzerNode")
    
    async def execute(self, state: PhotoSystemState) -> PhotoSystemState:
        """Analyze uploaded image"""
        self._log("Starting image analysis")
        
        try:
            if not state.photo_ref or not state.photo_ref:
                raise ValueError("No image found for analysis")
            
            # Analyze image
            analysis = await self._analyze_image(state.photo_ref)
            
            # Generate recommended camera parameters based on analysis results
            recommended_params = self._generate_camera_params(analysis)
            
            # Update state
            updated_state = self._update_state(
                state,
                analysis=analysis,
                final_params=recommended_params,
                current_step="ready_for_refinement"
            )
            
            self._log("Image analysis completed")
            return updated_state
            
        except Exception as e:
            self._log(f"Image analysis failed: {str(e)}", "ERROR")
            return self._update_state(
                state,
                error_message=f"Image analysis failed: {str(e)}",
                current_step="analyze"
            )
    
    async def _analyze_image(self, image_path: str) -> ImageAnalysis:
        """Analyze various image metrics"""
        self._log(f"Analyzing image: {image_path}")
        
        # Use PIL for basic analysis
        with Image.open(image_path) as pil_img:
            # Calculate brightness, contrast etc.
            stat = ImageStat.Stat(pil_img)
            
            # Convert to RGB if needed
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            
            # Basic statistics
            brightness = sum(stat.mean) / len(stat.mean) / 255.0
            contrast = sum(stat.stddev) / len(stat.stddev) / 255.0
        
        # Use OpenCV for deeper analysis
        cv_img = cv2.imread(image_path)
        if cv_img is None:
            raise ValueError("Cannot read image with OpenCV")
        
        # Convert color space
        hsv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
        
        # Analyze composition
        composition_analysis = self._analyze_composition(cv_img)
        
        # Color analysis
        color_analysis = self._analyze_colors(cv_img, hsv_img)
        
        # Scene type detection
        scene_type = self._detect_scene_type(cv_img)
        
        # Estimate exposure
        estimated_exposure = self._estimate_exposure(cv_img)
        
        return ImageAnalysis(
            exposure=estimated_exposure,
            brightness=float(brightness),
            contrast=float(contrast),
            saturation=float(np.mean(hsv_img[:, :, 1]) / 255.0),
            composition=composition_analysis,
            color_analysis=color_analysis,
            scene_type=scene_type
        )
    
    def _analyze_composition(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze composition"""
        height, width = img.shape[:2]
        
        # Simple edge detection to determine subject position
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Find region with highest edge density (simplified subject detection)
        thirds_h = height // 3
        thirds_w = width // 3
        
        regions = {
            "top_left": np.sum(edges[0:thirds_h, 0:thirds_w]),
            "top_center": np.sum(edges[0:thirds_h, thirds_w:2*thirds_w]),
            "top_right": np.sum(edges[0:thirds_h, 2*thirds_w:width]),
            "center_left": np.sum(edges[thirds_h:2*thirds_h, 0:thirds_w]),
            "center": np.sum(edges[thirds_h:2*thirds_h, thirds_w:2*thirds_w]),
            "center_right": np.sum(edges[thirds_h:2*thirds_h, 2*thirds_w:width]),
            "bottom_left": np.sum(edges[2*thirds_h:height, 0:thirds_w]),
            "bottom_center": np.sum(edges[2*thirds_h:height, thirds_w:2*thirds_w]),
            "bottom_right": np.sum(edges[2*thirds_h:height, 2*thirds_w:width])
        }
        
        # Find main region
        main_region = max(regions.keys(), key=lambda k: regions[k])
        
        return {
            "main_subject_region": main_region,
            "edge_density": regions,
            "rule_of_thirds_compliance": main_region in ["top_left", "top_right", "bottom_left", "bottom_right"]
        }
    
    def _analyze_colors(self, img_bgr: np.ndarray, img_hsv: np.ndarray) -> Dict[str, Any]:
        """Analyze colors"""
        # Calculate dominant colors
        height, width = img_hsv.shape[:2]
        
        # Hue distribution
        hue_hist = cv2.calcHist([img_hsv], [0], None, [180], [0, 180])
        dominant_hue = np.argmax(hue_hist)
        
        # Saturation and brightness statistics
        saturation_mean = np.mean(img_hsv[:, :, 1])
        value_mean = np.mean(img_hsv[:, :, 2])
        
        return {
            "dominant_hue": int(dominant_hue),
            "average_saturation": float(saturation_mean / 255.0),
            "average_value": float(value_mean / 255.0),
            "color_temperature": self._estimate_color_temperature(img_bgr)
        }
    
    def _estimate_color_temperature(self, img_bgr: np.ndarray) -> str:
        """Estimate color temperature"""
        # Simple color temperature estimation (based on blue and red channel ratio)
        b_mean = np.mean(img_bgr[:, :, 0])
        r_mean = np.mean(img_bgr[:, :, 2])
        
        ratio = b_mean / (r_mean + 1e-6)  # Avoid division by zero
        
        if ratio > 1.2:
            return "cool"  # Cool tone
        elif ratio < 0.8:
            return "warm"  # Warm tone
        else:
            return "neutral"  # Neutral
    
    def _detect_scene_type(self, img: np.ndarray) -> str:
        """Detect scene type (simplified version)"""
        # This is a simplified scene detection, actual projects might need ML models
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Calculate overall image brightness
        brightness = np.mean(gray) / 255.0
        
        # Calculate edge count (complexity)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (img.shape[0] * img.shape[1])
        
        # Simple scene classification logic
        if brightness < 0.3:
            return "night"
        elif edge_density > 0.1:
            return "architecture"  # Architecture usually has many edges
        elif edge_density < 0.05:
            return "portrait"  # Portraits usually have fewer edges
        else:
            return "landscape"
    
    def _estimate_exposure(self, img: np.ndarray) -> float:
        """Estimate exposure value (simplified version)"""
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Calculate image brightness distribution
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        
        # Calculate weighted average brightness
        total_pixels = img.shape[0] * img.shape[1]
        weighted_brightness = sum(i * hist[i][0] for i in range(256)) / total_pixels
        
        # Map brightness to exposure value range (-3 to +3)
        # This is a simplified mapping, actual cases would be more complex
        normalized_brightness = weighted_brightness / 255.0
        exposure_value = (normalized_brightness - 0.5) * 6  # Map to -3 to +3
        
        return float(np.clip(exposure_value, -3.0, 3.0))
    
    def _generate_camera_params(self, analysis: ImageAnalysis) -> CameraParams:
        """Generate recommended camera parameters based on analysis results"""
        params = CameraParams()
        
        # Set basic parameters based on scene type
        if analysis.scene_type == "portrait":
            params.aperture = "f/1.6"  # Large aperture for background blur
            params.focus = "auto"
            params.scene_mode = "portrait"
        elif analysis.scene_type == "landscape":
            params.aperture = "f/5.6"  # Small aperture for depth of field
            params.focus = "infinity"
            params.scene_mode = "landscape"
        elif analysis.scene_type == "night":
            params.aperture = "f/1.6"  # Large aperture to increase light
            params.iso = 800
            params.scene_mode = "night"
        else:
            params.aperture = "f/2.8"
            params.focus = "auto"
            params.scene_mode = "auto"
        
        # Adjust exposure compensation based on brightness
        if analysis.brightness < 0.3:
            params.exposure = 1.0  # Increase exposure
        elif analysis.brightness > 0.7:
            params.exposure = -1.0  # Decrease exposure
        else:
            params.exposure = 0.0
        
        # Set white balance based on color temperature
        if analysis.color_analysis and analysis.color_analysis.get("color_temperature"):
            temp = analysis.color_analysis["color_temperature"]
            if temp == "cool":
                params.white_balance = "cloudy"
            elif temp == "warm":
                params.white_balance = "daylight"
            else:
                params.white_balance = "auto"
        
        self._log(f"Generated recommended parameters: {params}")
        return params

import numpy as np
import logging
from typing import List, Any, Union

# VisionFace modules
from visionface.models.Detector import Detector, DetectedFace
from visionface.commons.utils import xywh2xyxy
from visionface.commons.image_utils import get_cropped_face

logging.basicConfig(level=logging.INFO)


class MediaPipeDetector(Detector):
    """
    References:
        MediaPipe Face Detection: https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/face_detection.md
    """
    def __init__(self, MODEL_ID: int = 1, MIN_CONFIDENCE: float = 0.5):
        """
        Initialize the MediaPipeDetector.

        Parameters:
            model_id: int, default=1
                The MediaPipe face detection model to use:
                - 0: Short-range model (optimized for faces within 2 meters)
                - 1: Full-range model (optimized for faces within 5 meters)
            
            min_confidence: float, default=0.5
                Minimum confidence threshold (0.0 to 1.0) for face detection.
                Detections below this threshold will be filtered out.
        """
        if MODEL_ID not in (0, 1):
            raise ValueError(f"Invalid MODEL_ID: {MODEL_ID}. MediaPipe only 0 (short-range) or 1 (full-range) are supported.")
        
        super().__init__(MODEL_ID, MIN_CONFIDENCE)
        self.model = self.build_model()

    def build_model(self) -> Any:
        """
        Build and initialize the MediaPipe face detection model.
        
        Returns:
            An instance of MediaPipe's FaceDetection model.
        
        Raises:
            ImportError: If the 'mediapipe' library is not installed.
        """
        try:
            import mediapipe as mp
        except ModuleNotFoundError as error:
            raise ImportError(
                "The 'mediapipe' library is not installed. "
                "It is required for MediaPipeDetector to work. "
                "Please install it using: pip install mediapipe"
            ) from error
        
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(
            min_detection_confidence=self.conf,
            model_selection=self.model_id
        )
        return face_detection
    
    def _detect_one(
        self, 
        img_id: int, 
        img: np.ndarray, 
        return_cropped_faces: bool
    ) -> List[DetectedFace]:
        """
        Detect faces in a single image using the MediaPipe model.

        Parameters:
            img_id (int): id for the image
            img (np.ndarray): The input image in BGR format
            return_cropped_faces(bool): cropped face images in each DetectedFace object.

        Returns:
            List[DetectedFace]: A list of DetectedFace objects.
        """
        # img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = img.shape[:2]
        results = self.model.process(img)
        if results.detections is None:
            return []
        return self.process_faces(img, results, w, h, img_id, return_cropped_faces)

    def detect_faces(
        self, 
        imgs: List[np.ndarray], 
        return_cropped_faces: bool = True
    ) -> List[List[DetectedFace]]:
        """
        Detect faces in one or more input images using the MediaPipe model.

        Parameters:
            imgs: List[np.ndarray]: 
                A single image or a list of images in BGR format.

            return_cropped_faces : bool, optional
                Whether to include cropped face images in each DetectedFace object. Default is True.
        
        Returns:
            List[List[DetectedFace]]: 
                A list where each element is a list of DetectedFace objects for the corresponding input image.
        """
        # Run face detection on each image  
        detections = [self._detect_one(img_id, img, return_cropped_faces) for img_id, img in enumerate(imgs)]
        return detections

    def process_faces(
        self, 
        img: np.ndarray, 
        results: Any, 
        img_width: int, 
        img_height: int, 
        img_id: int, 
        return_cropped_faces: bool
    ) -> List[DetectedFace]:
        """
        Process the raw detection results from MediaPipe into DetectedFace objects.
        
        Parameters:
            img (np.ndarray): 
                The input image in BGR or RGB format.
            results: Any
                Detection results from the MediaPipe model's process.
            img_width: int
                Width of the image in pixels.
            img_height: int
                Height of the image in pixels.
            return_cropped_faces : bool
                Whether to include cropped face images in each DetectedFace object.
                
        Returns:
            List[DetectedFace]
                A list of DetectedFace objects with face coordinates
                and confidence scores for each detected face.
        """
        
        detections = []

        for detection in results.detections:
            (confidence,) = detection.score
            bounding_box = detection.location_data.relative_bounding_box
            
            # Convert relative coordinates to absolute pixel coordinates
            x = int(bounding_box.xmin * img_width)
            w = int(bounding_box.width * img_width)
            y = int(bounding_box.ymin * img_height)
            h = int(bounding_box.height * img_height)
            
            # Convert xywh format to xyxy
            bbox = xywh2xyxy([x, y, w, h])
            cropped_face = get_cropped_face(img, bbox) if return_cropped_faces else None

            facial_info = DetectedFace(
                xmin=bbox[0],
                ymin=bbox[1],
                xmax=bbox[2],
                ymax=bbox[3],
                conf=round(confidence, 2),
                class_name="face",
                cropped_face=cropped_face
            )
            detections.append(facial_info)
            
        logging.info(
            f"[MediaPipeDetector] {len(detections)} face(s) detected in image id: {img_id}, "
            f"min confidence threshold {self.conf:.2f}."
        )

        return detections
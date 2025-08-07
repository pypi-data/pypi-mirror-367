# Pydantic Models for type validation and serialization
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field, validator


class LayoutBox(BaseModel):
    """
    Represents a single detected layout box with its properties.
    
    Attributes:
        label: The classification label of the detected box
        bbox: Bounding box coordinates [x1, y1, x2, y2]
        confidence: Optional confidence score of the detection
    """
    label: str = Field(..., description="Classification label of the detected box")
    bbox: List[float] = Field(..., 
                            description="Bounding box coordinates [x1, y1, x2, y2]",
                            min_items=4, 
                            max_items=4)
    confidence: Optional[float] = Field(None, 
                                      description="Confidence score of detection",
                                      ge=0.0, 
                                      le=1.0)

    @validator('bbox')
    def validate_bbox(cls, v):
        if len(v) != 4:
            raise ValueError('Bounding box must have exactly 4 coordinates')
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError('All bbox coordinates must be numeric')
        return v

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            'label': self.label,
            'bbox': self.bbox,
            'confidence': self.confidence
        }

class LayoutOutput(BaseModel):
    """
    Container for all detected layout boxes in an image.
    
    Attributes:
        bboxes: List of detected LayoutBox objects
        page_number: Optional page number for multi-page documents
        image_size: Optional tuple of (width, height) of the processed image
    """
    bboxes: List[LayoutBox] = Field(default_factory=list,
                                   description="List of detected layout boxes")
    page_number: Optional[int] = Field(None, 
                                     description="Page number for multi-page documents",
                                     ge=1)
    image_size: Optional[Tuple[int, int]] = Field(None,
                                                 description="Size of the processed image (width, height)")

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            'bboxes': [box.to_dict() for box in self.bboxes],
            'page_number': self.page_number,
            'image_size': self.image_size
        }

    def save_json(self, output_path: Union[str, Path]) -> None:
        """Save layout output to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
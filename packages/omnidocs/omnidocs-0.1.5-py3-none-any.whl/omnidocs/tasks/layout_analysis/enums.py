from enum import Enum


class LayoutLabel(str, Enum):
    """Standardized layout detection labels across all models."""
    TEXT = "text"
    TITLE = "title"
    FORMULA = "formula"
    LIST = "list"
    CAPTION = "caption"
    IMAGE = "image"
    TABLE = "table"
    
    def __str__(self) -> str:
        return self.value

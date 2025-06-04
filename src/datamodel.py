# src/datamodel.py

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Tuple, Union, List, Optional, Dict, Any

BBox = Tuple[float, float, float, float]  # (x0, y0, x1, y1)

@dataclass_json
@dataclass
class ParagraphChunk:
    id: str
    page_content: Union[str, List[str]]
    metadata: dict = None

from typing import List
from PIL import Image
from dataclasses import dataclass, field


@dataclass
class Leaf:
    key: str
    name: str
    img: Image
    reference: bool = False
    reference_area: float = 0
    background_colour: str = ""
    leaf_binary: Image = None
    leaf_outline_binary: Image = None
    lesion_binary: Image = None
    reference_binary: Image = None
    leaf_area: int = 0
    lesion_area: int = 0
    lesion_area_percentage: float = 0
    lesion_area_mm2: float = 0
    run_time: float = 0
    minimum_lesion_area_value: int = 0
    modified_image: Image = None
    average_lesion_size: float = 0
    num_lesions: int = 0
    min_lesion_size: float = 0
    max_lesion_size: float = 0
    labeled_pixels: list = field(default_factory=list)
    lesion_class_map: dict = field(default_factory=dict)
    lesion_size_threshold: float = 0.01

    def __lt__(self, other):
        return self.lesion_area_percentage < other.lesion_area_percentage


@dataclass
class LeafList:
    leaves: List[Leaf] = field(default_factory=list)

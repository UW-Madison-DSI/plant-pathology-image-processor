import json
from typing import List
from PIL import Image
from dataclasses import dataclass, field


@dataclass
class Leaf:
    key: str
    name: str
    img: Image
    reference: bool = False
    reference_measure: float = 0
    background_colour: str = ""
    leaf_binary: Image = None
    lesion_binary: Image = None
    reference_binary: Image = None
    leaf_area: int = 0
    lesion_area: int = 0
    lesion_area_percentage: float = 0
    lesion_area_cm2: float = 0
    run_time: float = 0
    minimum_lesion_area_value: int = 0

    def __lt__(self, other):
        return self.lesion_area_percentage < other.lesion_area_percentage


@dataclass
class LeafList:
    leaves: List[Leaf] = field(default_factory=list)

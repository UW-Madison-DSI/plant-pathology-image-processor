import json
from typing import List
from PIL import Image
from dataclasses import dataclass, field

# Read in settings from JSON file
with open("src/leaflesiondetector/settings.json") as f:
    settings = json.load(f)


@dataclass
class Leaf:
    key: str
    name: str
    img: Image
    leaf_binary: Image = None
    lesion_binary: Image = None
    leaf_area: int = 0
    lesion_area: int = 0
    lesion_area_percentage: float = 0
    run_time: float = 0
    minimum_lesion_area_value: int = settings[settings["background_colour"]][
        "lesion_area"
    ]["min_value"]

    def __lt__(self, other):
        return self.lesion_area_percentage < other.lesion_area_percentage


@dataclass
class LeafList:
    leaves: List[Leaf] = field(default_factory=list)

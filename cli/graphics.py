from dataclasses import dataclass


@dataclass
class UGCGraphicsParams:
    template_id: int
    avatar_path: str
    width: int
    height: int
    blur_radius: int

class UGCGraphicsGenerator:
    def __init__(self):
        pass

    def render(self):
        pass
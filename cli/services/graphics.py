from dataclasses import dataclass


@dataclass
class GraphicsGeneratorParams:
    template_id: int
    avatar_path: str
    width: int
    height: int
    blur_radius: int


class GraphicsGenerator:
    def __init__(self):
        pass

    def render(self):
        pass
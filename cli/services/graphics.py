from dataclasses import dataclass


@dataclass
class GraphicsGeneratorParams:
    scene_template_id: int
    nickname_template_id: int
    overlay_template_id: int
    enable_intro: bool
    avatar_path: str
    width: int
    height: int
    blur_radius: int


class GraphicsGeneratorInterface:
    def __init__(self):
        pass

    def render(self):
        pass


class GraphicsGenerator:
    def __init__(self, params: GraphicsGeneratorParams):
        self.scene_template_id = params.scene_template_id
        self.overlay_template_id = params.overlay_template_id
        self.nickname_template_id = params.nickname_template_id
        self.enable_intro = params.enable_intro
        self.avatar_path = params.avatar_path
        self.width = params.width
        self.height = params.height
        self.blur_radius = params.blur_radius

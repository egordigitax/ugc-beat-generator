from dataclasses import dataclass
from pathlib import Path



@dataclass
class GraphicsGeneratorParams:
    scene_template_id: int
    user_info_template_id: int
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
    def __init__(self, verbose: bool):
        self.verbose = bool
        # self.scene_template_id = params.scene_template_id
        # self.user_info_template_id = params.user_info_template_id
        # self.overlay_template_id = params.overlay_template_id
        # self.avatar_path = params.avatar_path
        # self.width = params.width
        # self.height = params.height
        # self.blur_radius = params.blur_radius
        # self.verbose = verbose

    def process_scene_frames(self) -> Path:
        pass

    def process_user_info_frames(self) -> Path:
        pass


class GraphicsGeneratorLoader:
    @staticmethod
    def load(verbose: bool):
        return GraphicsGenerator(verbose)

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List
from natsort import natsorted
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from .engine.blender import BlenderEngine


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
        self.verbose = verbose
        self.blender = BlenderEngine("sdk/blender/blender-3.6.2-linux-x64/blender")

    def __logger(self, msg):
        if self.verbose:
            print(msg)

    def process_scene_frames(self, scene_template_id, width, height) -> List[Path]:
        self.blender.render(f"sources/scenes/main/{scene_template_id}/project.blend",
                            "output/renders/main", range(0, 90), width, height)
        natsort_files = natsorted(os.listdir("output/renders/main/"))
        return [Path(f'output/renders/main/{file}') for file in natsort_files if file.endswith(".png")]

    def process_user_info_frames(self, user_info_template_id, width, height) -> List[Path]:
        self.blender.render(f"sources/scenes/user/{user_info_template_id}/project.blend",
                            "output/renders/user", range(0, 105), width, height)
        natsort_files = natsorted(os.listdir("output/renders/user/"))
        return [Path(f'output/renders/user/{file}') for file in natsort_files if file.endswith(".png")]

    def process_overlay_frames(self, overlay_template_id, width, height) -> List[Path]:
        self.blender.render(f"sources/scenes/overlay/{overlay_template_id}/project.blend",
                            "output/renders/overlay", range(0, 30), width, height)
        natsort_files = natsorted(os.listdir("output/renders/overlay/"))
        return [Path(f'output/renders/overlay/{file}') for file in natsort_files if file.endswith(".png")]

    def save_avatar(self, avatar_path):
        img = Image.open(avatar_path)
        img_blur = img.filter(ImageFilter.GaussianBlur(50))
        img.save('sources/images/avatar.png')
        img_blur.save('sources/images/avatar-blur.png')

    def save_user_info_png(self, username, track_name):

        def draw_text(ctx, y_offset, text, font, color):
            _, _, w, h = ctx.textbbox((0, 0), text, font=font)
            ctx.text(((width - w) / 2, (height - h) / 2 + y_offset), text, font=font, fill=color)

        width = 1000
        height = 500
        canvas = Image.new("RGBA", (width, height), "#ffffff")

        _username = username if len(username) < 20 else username[:16]+"..."
        _track_name = track_name if len(track_name) < 20 else track_name[:16]+"..."

        main_font_size = 125 if len(username) < 7 else 90

        canvas_draw = ImageDraw.Draw(canvas)
        main_font = ImageFont.truetype("sources/fonts/Druk Text Wide Cyr Medium.otf", main_font_size)
        secondary_font = ImageFont.truetype("sources/fonts/Druk Text Wide Cyr Medium.otf", 65)

        draw_text(canvas_draw, -75, _username, main_font, (0,0,0))
        draw_text(canvas_draw, 25, _track_name, secondary_font, (0,0,0))

        canvas.save("sources/images/user-info.png")

class GraphicsGeneratorLoader:
    @staticmethod
    def load(verbose: bool):
        return GraphicsGenerator(verbose)
